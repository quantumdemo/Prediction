"""
Stage 15 Evidence Validation Engine Implementation

Deterministically validates pre-match research items against source allowlists,
URL validity, timestamp freshness, claim completeness, entity association, deduplication,
and contradiction checks while preserving full provenance and state integrity.
"""

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Set

from services.ml.app.evidence.schemas import (
    EvidenceValidationReport,
    ValidatedEvidenceItem,
    ValidationOutcome,
    ValidationReason,
)
from services.ml.app.research.schemas import (
    FactCategory,
    FixtureVerification,
    ResearchItem,
    ResearchReport,
    ResearchState,
)

logger = logging.getLogger("football_ml.evidence.validator")

# Default Credible Source Allowlist
ALLOWLISTED_DOMAINS: Set[str] = {
    "bbc.com",
    "skysports.com",
    "manutd.com",
    "arsenal.com",
    "chelseafc.com",
    "liverpoolfc.com",
    "mancity.com",
    "realmadrid.com",
    "fcbarcelona.com",
    "theathletic.com",
    "theguardian.com",
    "opta.com",
    "uefa.com",
    "premierleague.com",
}


class EvidenceValidationEngine:
    """
    Deterministic Evidence Validation Engine.
    """

    def __init__(self, allowlisted_domains: Optional[Set[str]] = None, max_freshness_days: int = 7):
        self.allowlisted_domains = allowlisted_domains or ALLOWLISTED_DOMAINS
        self.max_freshness_days = max_freshness_days

    def validate_research_report(self, research_report: ResearchReport) -> EvidenceValidationReport:
        """
        Validates all research items in a Stage 14 ResearchReport.
        """
        logger.info(f"Validating research report for fixture {research_report.fixture.fixture_id} ({len(research_report.items)} items)...")

        fixture = research_report.fixture
        validated_items: List[ValidatedEvidenceItem] = []
        rejected_items: List[ValidatedEvidenceItem] = []
        seen_claims: Set[str] = set()

        accepted_count = 0
        downgraded_count = 0
        rejected_count = 0
        conflicting_count = 0

        for item in research_report.items:
            val_item = self.validate_item(item, fixture, seen_claims)

            if val_item.validation_outcome == ValidationOutcome.REJECTED:
                rejected_count += 1
                rejected_items.append(val_item)
            else:
                if val_item.validation_outcome == ValidationOutcome.ACCEPTED:
                    accepted_count += 1
                elif val_item.validation_outcome == ValidationOutcome.DOWNGRADED:
                    downgraded_count += 1
                elif val_item.validation_outcome == ValidationOutcome.FLAGGED_CONFLICT:
                    conflicting_count += 1

                validated_items.append(val_item)

        # Calculate SHA256 audit trail hash over deterministic validated items
        audit_data = [
            {
                "fact_id": v.fact_id,
                "fixture_id": v.fixture_id,
                "claim": v.claim,
                "source_url": v.source_url,
                "retrieval_timestamp_utc": v.retrieval_timestamp_utc,
                "validation_outcome": v.validation_outcome.value,
                "validation_reasons": [r.value for r in v.validation_reasons],
            }
            for v in validated_items + rejected_items
        ]
        audit_hash = hashlib.sha256(json.dumps(audit_data, sort_keys=True).encode("utf-8")).hexdigest()

        report = EvidenceValidationReport(
            report_id=f"VAL_{fixture.fixture_id}_{int(datetime.now(timezone.utc).timestamp())}",
            fixture_id=fixture.fixture_id,
            total_evaluated=len(research_report.items),
            accepted_count=accepted_count,
            downgraded_count=downgraded_count,
            rejected_count=rejected_count,
            conflicting_count=conflicting_count,
            validated_items=validated_items,
            rejected_items=rejected_items,
            audit_trail_hash=audit_hash,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            validation_engine_version="STAGE15_EVIDENCE_VALIDATION_v1.0.0",
        )

        logger.info(f"Validation complete for {fixture.fixture_id}: Accepted={accepted_count}, Downgraded={downgraded_count}, Conflicting={conflicting_count}, Rejected={rejected_count}.")
        return report

    def validate_item(
        self,
        item: ResearchItem,
        fixture: FixtureVerification,
        seen_claims: Set[str],
    ) -> ValidatedEvidenceItem:
        reasons: List[ValidationReason] = []
        outcome = ValidationOutcome.ACCEPTED
        adjusted_state = item.research_state

        # 1. URL & Protocol Validation
        if not item.source_url or not item.source_url.startswith(("http://", "https://")):
            reasons.append(ValidationReason.INVALID_URL)
            outcome = ValidationOutcome.REJECTED
            adjusted_state = ResearchState.UNAVAILABLE

        # Extract domain from URL
        domain = self._extract_domain(item.source_url) if outcome != ValidationOutcome.REJECTED else ""
        if outcome != ValidationOutcome.REJECTED:
            if domain in self.allowlisted_domains:
                reasons.append(ValidationReason.VALID_PRIMARY_SOURCE)
            else:
                reasons.append(ValidationReason.UNALLOWLISTED_SOURCE)
                if adjusted_state == ResearchState.VERIFIED:
                    adjusted_state = ResearchState.LIKELY
                    outcome = ValidationOutcome.DOWNGRADED

        # 2. Claim Completeness Check
        if not item.claim or not item.claim.strip():
            reasons.append(ValidationReason.EMPTY_CLAIM)
            outcome = ValidationOutcome.REJECTED
            adjusted_state = ResearchState.UNAVAILABLE

        # 3. Retrieval Timestamp Presence & Freshness Check
        if not item.retrieval_timestamp_utc:
            reasons.append(ValidationReason.MISSING_TIMESTAMP)
            outcome = ValidationOutcome.REJECTED
            adjusted_state = ResearchState.UNAVAILABLE
        else:
            is_stale, days_diff = self._check_timestamp_freshness(item.retrieval_timestamp_utc, fixture.match_date)
            if is_stale:
                reasons.append(ValidationReason.STALE_TIMESTAMP)
                adjusted_state = ResearchState.UNCERTAIN
                if outcome != ValidationOutcome.REJECTED:
                    outcome = ValidationOutcome.DOWNGRADED

        # 4. Entity / Fixture Association Check
        if outcome != ValidationOutcome.REJECTED:
            has_valid_entity = self._verify_entity_association(item, fixture)
            if not has_valid_entity:
                reasons.append(ValidationReason.WRONG_ENTITY_ASSOCIATION)
                outcome = ValidationOutcome.REJECTED
                adjusted_state = ResearchState.UNAVAILABLE

        # 5. Duplicate Evidence Check
        if outcome != ValidationOutcome.REJECTED:
            claim_hash = hashlib.md5(f"{item.category.value}_{item.claim.lower().strip()}".encode("utf-8")).hexdigest()
            if claim_hash in seen_claims:
                reasons.append(ValidationReason.DUPLICATE_EVIDENCE)
                outcome = ValidationOutcome.REJECTED
                adjusted_state = ResearchState.UNAVAILABLE
            else:
                seen_claims.add(claim_hash)

        # 6. Contradiction Flagging Check
        if outcome != ValidationOutcome.REJECTED:
            if item.research_state == ResearchState.CONFLICTING or item.contradiction_details:
                reasons.append(ValidationReason.CONTRADICTORY_EVIDENCE)
                outcome = ValidationOutcome.FLAGGED_CONFLICT
                adjusted_state = ResearchState.CONFLICTING

        val_id = f"VAL_ITEM_{item.fact_id}"

        return ValidatedEvidenceItem(
            validation_id=val_id,
            fact_id=item.fact_id,
            fixture_id=fixture.fixture_id,
            category=item.category,
            claim=item.claim,
            source_name=item.source_name,
            source_url=item.source_url,
            retrieval_timestamp_utc=item.retrieval_timestamp_utc,
            publication_timestamp_utc=item.publication_timestamp_utc,
            original_research_state=item.research_state,
            adjusted_research_state=adjusted_state,
            validation_outcome=outcome,
            validation_reasons=reasons,
            canonical_entities_mentioned=item.canonical_entities_mentioned,
            contradiction_details=item.contradiction_details,
            validation_timestamp_utc=item.retrieval_timestamp_utc or datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            domain = url.split("//")[-1].split("/")[0].lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def _check_timestamp_freshness(self, timestamp_str: str, match_date_str: str) -> Tuple[bool, float]:
        try:
            ts_clean = timestamp_str.replace("Z", "+00:00")
            retrieval_dt = datetime.fromisoformat(ts_clean)
            match_dt = datetime.strptime(match_date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)

            diff_days = (match_dt - retrieval_dt).total_seconds() / 86400.0
            is_stale = diff_days > self.max_freshness_days or diff_days < -1.0
            return is_stale, float(diff_days)
        except Exception as e:
            logger.warning(f"Error checking timestamp freshness for '{timestamp_str}' vs '{match_date_str}': {e}")
            return True, 999.0

    @staticmethod
    def _verify_entity_association(item: ResearchItem, fixture: FixtureVerification) -> bool:
        if not item.canonical_entities_mentioned:
            return True

        home = fixture.home_team.lower()
        away = fixture.away_team.lower()
        home_id = fixture.home_canonical_id.lower()
        away_id = fixture.away_canonical_id.lower()

        for ent in item.canonical_entities_mentioned:
            ent_clean = ent.lower()

            # Matches team name or canonical ID
            if ent_clean in home or ent_clean in away or home in ent_clean or away in ent_clean or ent_clean in home_id or ent_clean in away_id:
                return True
            if "team" in ent_clean or "match" in ent_clean or "league" in ent_clean:
                return True

        return False
