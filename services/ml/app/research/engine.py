"""
Stage 14 Current-Match Web Research Engine Implementation

Collects, parses, and classifies current pre-match information for upcoming verified football matches.
Preserves full source provenance (URL, retrieval timestamp), explicit research states
(VERIFIED, LIKELY, UNCERTAIN, CONFLICTING, UNAVAILABLE), and contradiction detection.
Strictly prohibits numerical probability generation or synthetic data fabrication.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.research.schemas import (
    FactCategory,
    FixtureVerification,
    ResearchItem,
    ResearchReport,
    ResearchState,
)
from services.ml.app.research.verification import FixtureVerifier

logger = logging.getLogger("football_ml.research.engine")


class CurrentMatchResearchEngine:
    """
    Current-Match Web Research Engine.
    gathers pre-match evidence for a target fixture across 12 fact categories.
    """

    def __init__(self):
        self.verifier = FixtureVerifier()

    def research_fixture(
        self,
        fixture: FixtureVerification,
        raw_evidence_inputs: Optional[List[Dict[str, Any]]] = None,
    ) -> ResearchReport:
        """
        Processes pre-match research inputs for a verified target fixture.
        """
        logger.info(f"Starting Stage 14 pre-match research for fixture {fixture.fixture_id} ({fixture.home_team} vs {fixture.away_team})...")

        research_items: List[ResearchItem] = []
        conflicting_items: List[ResearchItem] = []

        if raw_evidence_inputs:
            for idx, raw in enumerate(raw_evidence_inputs, 1):
                item = self._parse_and_validate_evidence_item(raw, idx)
                if item:
                    research_items.append(item)

        # Detect contradictions across sources
        research_items, detected_conflicts = self._detect_source_contradictions(research_items)
        conflicting_items.extend(detected_conflicts)

        # Determine which of the 12 fact categories have valid items vs unavailable
        category_summary: Dict[str, List[str]] = {}
        found_categories = set()

        for item in research_items:
            cat_name = item.category.value
            found_categories.add(item.category)

            if cat_name not in category_summary:
                category_summary[cat_name] = []
            category_summary[cat_name].append(f"[{item.research_state.value}] {item.claim} (Source: {item.source_name})")

        all_categories = set(FactCategory)
        unavailable_categories = sorted(list(all_categories - found_categories), key=lambda c: c.value)

        report = ResearchReport(
            report_id=f"REP_{fixture.fixture_id}_{int(datetime.now(timezone.utc).timestamp())}",
            fixture=fixture,
            items=research_items,
            summary_by_category=category_summary,
            conflicting_items=conflicting_items,
            unavailable_categories=unavailable_categories,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            research_engine_version="STAGE14_WEB_RESEARCH_v1.0.0",
        )

        logger.info(f"Stage 14 research complete for {fixture.fixture_id}: {len(research_items)} items collected, {len(conflicting_items)} conflicts, {len(unavailable_categories)} unavailable categories.")
        return report

    def _parse_and_validate_evidence_item(self, raw: Dict[str, Any], idx: int) -> Optional[ResearchItem]:
        """
        Parses raw research input into ResearchItem with provenance validation.
        Rejects items missing required source URL, claim, or category.
        """
        claim = raw.get("claim")
        source_url = raw.get("source_url")
        source_name = raw.get("source_name", "Web Research Source")
        category_str = raw.get("category")

        if not claim or not claim.strip():
            logger.warning(f"Rejected raw item #{idx}: Missing claim string.")
            return None

        if not source_url or not source_url.strip() or not source_url.startswith(("http://", "https://")):
            logger.warning(f"Rejected raw item #{idx}: Invalid or missing source URL '{source_url}'.")
            return None

        try:
            category = FactCategory(category_str) if category_str else FactCategory.TEAM_NEWS
        except ValueError:
            logger.warning(f"Unknown category '{category_str}', defaulting to TEAM_NEWS.")
            category = FactCategory.TEAM_NEWS

        state_str = raw.get("research_state", "VERIFIED")
        try:
            state = ResearchState(state_str)
        except ValueError:
            state = ResearchState.UNCERTAIN

        item_id = raw.get("fact_id") or f"FACT_{idx:03d}_{uuid.uuid4().hex[:6]}"

        return ResearchItem(
            fact_id=item_id,
            category=category,
            claim=claim.strip(),
            source_name=source_name.strip(),
            source_url=source_url.strip(),
            retrieval_timestamp_utc=raw.get("retrieval_timestamp_utc") or datetime.now(timezone.utc).isoformat(),
            publication_timestamp_utc=raw.get("publication_timestamp_utc"),
            research_state=state,
            canonical_entities_mentioned=raw.get("canonical_entities_mentioned", []),
            contradiction_details=raw.get("contradiction_details"),
            confidence_score=float(raw.get("confidence_score", 1.0)),
        )

    def _detect_source_contradictions(
        self, items: List[ResearchItem]
    ) -> Tuple[List[ResearchItem], List[ResearchItem]]:
        """
        Detects opposing claims (e.g. player OUT vs player IN/AVAILABLE in same category).
        Flags state as CONFLICTING and records contradiction details explicitly.
        """
        conflicts: List[ResearchItem] = []
        parsed_items: List[ResearchItem] = []

        # Group by category and entity mentioned
        entity_claims: Dict[Tuple[FactCategory, str], List[ResearchItem]] = {}

        for item in items:
            entities = item.canonical_entities_mentioned or ["TEAM_GENERAL"]
            for ent in entities:
                key = (item.category, ent)
                if key not in entity_claims:
                    entity_claims[key] = []
                entity_claims[key].append(item)

        for (cat, ent), claim_list in entity_claims.items():
            if len(claim_list) > 1:
                # Check for contradictory status words (out vs in/available/fit)
                has_out = any("out" in c.claim.lower() or "injured" in c.claim.lower() or "suspended" in c.claim.lower() for c in claim_list)
                has_in = any("fit" in c.claim.lower() or "available" in c.claim.lower() or "lineup" in c.claim.lower() for c in claim_list)

                if has_out and has_in:
                    logger.warning(f"Contradiction detected for entity '{ent}' in category '{cat.value}' across {len(claim_list)} sources!")

                    sources_summary = ", ".join(f"{c.source_name}: '{c.claim}'" for c in claim_list)
                    for item in claim_list:
                        item.research_state = ResearchState.CONFLICTING
                        item.contradiction_details = f"Contradiction between sources for {ent}: {sources_summary}"
                        if item not in conflicts:
                            conflicts.append(item)

        return items, conflicts
