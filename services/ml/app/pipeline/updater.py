"""
Stage 16 Current Feature Updater Implementation

Maps Stage 15 validated evidence items to Stage 9 registered numerical features,
enforces prediction-time timestamp cutoff bounds, records provenance, and preserves missingness.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.evidence.schemas import EvidenceValidationReport, ValidatedEvidenceItem, ValidationOutcome
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.pipeline.schemas import CurrentFeatureProvenance, FeatureUpdateResult
from services.ml.app.research.schemas import FactCategory, ResearchState

logger = logging.getLogger("football_ml.pipeline.updater")


class CurrentFeatureUpdater:
    """
    Updates Stage 9 numerical feature vectors from Stage 15 validated current-match evidence.
    """

    def __init__(self):
        self.feature_registry = STAGE9_FEATURE_REGISTRY

    def update_feature_vector(
        self,
        fixture_id: str,
        base_features: Dict[str, Optional[float]],
        validation_report: Optional[EvidenceValidationReport],
        prediction_timestamp_utc: str,
    ) -> FeatureUpdateResult:
        logger.info(f"Updating feature vector for fixture {fixture_id} at cutoff {prediction_timestamp_utc}...")

        updated_feats = dict(base_features)
        provenance_records: List[CurrentFeatureProvenance] = []
        quarantine_reasons: List[str] = []
        is_safe = True

        if not validation_report or not validation_report.validated_items:
            logger.info("No validated evidence items provided. Returning base feature vector with preserved missingness.")
            return FeatureUpdateResult(
                fixture_id=fixture_id,
                prediction_timestamp_utc=prediction_timestamp_utc,
                updated_features=updated_feats,
                feature_provenance_records=[],
                quarantined_reasons=[],
                is_prediction_time_safe=True,
            )

        # Parse cutoff datetime
        prediction_dt = self._parse_iso_dt(prediction_timestamp_utc)

        for item in validation_report.validated_items:
            # 1. Reject invalid or rejected validation outcomes
            if item.validation_outcome == ValidationOutcome.REJECTED:
                quarantine_reasons.append(f"Skipped rejected item {item.fact_id}: Validation outcome REJECTED.")
                continue

            # 2. Reject conflicting evidence without deterministic resolution
            if item.validation_outcome == ValidationOutcome.FLAGGED_CONFLICT or item.adjusted_research_state == ResearchState.CONFLICTING:
                quarantine_reasons.append(f"Conflict in item {item.fact_id} ({item.category.value}): No deterministic resolution.")
                continue

            # 3. Enforce Prediction-Time Availability (Leakage Check)
            item_retrieval_dt = self._parse_iso_dt(item.retrieval_timestamp_utc)
            if item_retrieval_dt > prediction_dt:
                quarantine_reasons.append(
                    f"Leakage rejected for item {item.fact_id}: Retrieval timestamp ({item.retrieval_timestamp_utc}) > prediction cutoff ({prediction_timestamp_utc})."
                )
                is_safe = False
                continue

            # 4. Map Validated Item to Stage 9 Features
            feature_updates = self._map_evidence_to_stage9_features(item)
            for feat_id, (val, rule) in feature_updates.items():
                if feat_id not in self.feature_registry:
                    quarantine_reasons.append(f"Rejected unknown feature {feat_id}: Not in Stage 9 Feature Registry.")
                    continue

                orig_val = base_features.get(feat_id)
                updated_feats[feat_id] = val

                provenance_records.append(
                    CurrentFeatureProvenance(
                        feature_id=feat_id,
                        updated_value=val,
                        original_historical_value=orig_val,
                        source_fact_id=item.fact_id,
                        source_name=item.source_name,
                        source_url=item.source_url,
                        evidence_state=item.adjusted_research_state,
                        update_timestamp_utc=item.retrieval_timestamp_utc,
                        transformation_rule=rule,
                        missingness_state="PRESENT" if val is not None else "PRESERVE_NULL",
                    )
                )

        return FeatureUpdateResult(
            fixture_id=fixture_id,
            prediction_timestamp_utc=prediction_timestamp_utc,
            updated_features=updated_feats,
            feature_provenance_records=provenance_records,
            quarantined_reasons=quarantine_reasons,
            is_prediction_time_safe=is_safe,
        )

    def _map_evidence_to_stage9_features(self, item: ValidatedEvidenceItem) -> Dict[str, Tuple[Optional[float], str]]:
        updates: Dict[str, Tuple[Optional[float], str]] = {}
        claim_lower = item.claim.lower()

        # Extract numeric values from claims
        numbers = re.findall(r"\b\d+\.?\d*\b", claim_lower)
        num_val = float(numbers[0]) if numbers else None

        if item.category == FactCategory.REST_CONGESTION and num_val is not None:
            if "home" in claim_lower:
                updates["FEAT_REST_DAYS_HOME"] = (num_val, "Extracted home rest days from REST_CONGESTION evidence.")
            elif "away" in claim_lower:
                updates["FEAT_REST_DAYS_AWAY"] = (num_val, "Extracted away rest days from REST_CONGESTION evidence.")

        elif item.category == FactCategory.RECENT_FORM and num_val is not None:
            if "home" in claim_lower and "3" in claim_lower:
                updates["FEAT_FORM3_HOME"] = (num_val, "Updated home Form3 points from RECENT_FORM evidence.")
            elif "away" in claim_lower and "3" in claim_lower:
                updates["FEAT_FORM3_AWAY"] = (num_val, "Updated away Form3 points from RECENT_FORM evidence.")

        elif item.category == FactCategory.HEAD_TO_HEAD and num_val is not None:
            updates["FEAT_H2H_HOME_WINS"] = (num_val, "Updated H2H home wins count from HEAD_TO_HEAD evidence.")

        return updates

    @staticmethod
    def _parse_iso_dt(ts_str: str) -> datetime:
        try:
            ts_clean = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(ts_clean)
        except Exception:
            return datetime.now(timezone.utc)
