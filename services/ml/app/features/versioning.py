"""
Stage 9 Feature Dataset Versioning Module

Exports metadata and summary reports for STAGE9_FEATURE_DATASET_v1.0.0.
Provides feature-level coverage reporting across all target fixtures.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY

logger = logging.getLogger("football_ml.features.versioning")

STAGE9_FEATURE_DATASET_VERSION_LABEL = "STAGE9_FEATURE_DATASET_v1.0.0"


def compute_feature_level_coverage_report(
    vectors: List[MatchFeatureVector],
) -> Dict[str, Dict[str, Any]]:
    """
    Calculates detailed feature-level coverage metrics across all target fixtures.
    Distinguishes PRESENT, MISSING_SOURCE_DATA, INSUFFICIENT_HISTORY, INVALID, UNAVAILABLE.
    """
    total_fixtures = len(vectors)
    coverage_report: Dict[str, Dict[str, Any]] = {}

    for fid, defn in STAGE9_FEATURE_REGISTRY.items():
        present_cnt = 0
        missing_src_cnt = 0
        insufficient_hist_cnt = 0
        invalid_cnt = 0
        unavailable_cnt = 0

        for vec in vectors:
            st = vec.feature_availability.get(fid, "UNAVAILABLE")
            if st == "PRESENT":
                present_cnt += 1
            elif st == "MISSING_SOURCE_DATA":
                missing_src_cnt += 1
            elif st == "INSUFFICIENT_HISTORY":
                insufficient_hist_cnt += 1
            elif st == "INVALID":
                invalid_cnt += 1
            else:
                unavailable_cnt += 1

        coverage_pct = (
            round((present_cnt / total_fixtures) * 100.0, 2)
            if total_fixtures > 0
            else 0.0
        )

        coverage_report[fid] = {
            "feature_id": fid,
            "feature_name": defn.name,
            "family": defn.family,
            "total_target_fixtures": total_fixtures,
            "PRESENT": present_cnt,
            "MISSING_SOURCE_DATA": missing_src_cnt,
            "INSUFFICIENT_HISTORY": insufficient_hist_cnt,
            "INVALID": invalid_cnt,
            "UNAVAILABLE": unavailable_cnt,
            "coverage_percentage": coverage_pct,
        }

    return coverage_report


def generate_stage9_feature_dataset_artifact(
    vectors: List[MatchFeatureVector], output_dir: str
) -> Dict[str, Any]:
    """
    Generates versioned metadata artifact for STAGE9_FEATURE_DATASET_v1.0.0.
    """
    os.makedirs(output_dir, exist_ok=True)

    total_fixtures = len(vectors)
    sample_feats = list(STAGE9_FEATURE_REGISTRY.keys())
    coverage_report = compute_feature_level_coverage_report(vectors)

    artifact_metadata = {
        "feature_dataset_version": STAGE9_FEATURE_DATASET_VERSION_LABEL,
        "input_entity_mapping_version": "STAGE8_ENTITY_MAPPING_v1.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_fixtures_processed": total_fixtures,
        "feature_count": len(sample_feats),
        "feature_list": sample_feats,
        "feature_coverage_report": coverage_report,
        "leakage_safeguards": [
            "STRICT_PRE_MATCH_CHRONOLOGICAL_CUTOFF",
            "TARGET_MATCH_OUTCOME_EXCLUDED_FROM_OWN_FEATURES",
            "ODDS_EXCLUDED_REJECTED_ODDS",
            "SYNTHETIC_XG_EXCLUDED_REJECTED_UNVERIFIED",
            "CLUSTER_LABELS_EXCLUDED_REJECTED_LEAKAGE",
            "RAW_FORM_EXCLUDED_RECALCULATED_FROM_CANONICAL_RESULTS",
            "STAGE7_QUARANTINED_MATCHES_EXCLUDED",
        ],
    }

    meta_path = os.path.join(output_dir, "stage9_feature_dataset_version.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(artifact_metadata, f, indent=2)

    logger.info(f"Stage 9 feature dataset metadata written to {meta_path}")
    return artifact_metadata
