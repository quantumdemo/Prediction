"""
Stage 9 Feature Dataset Versioning Module

Exports metadata and summary reports for STAGE9_FEATURE_DATASET_v1.0.0.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.ml.app.features.engine import MatchFeatureVector

logger = logging.getLogger("football_ml.features.versioning")

STAGE9_FEATURE_DATASET_VERSION_LABEL = "STAGE9_FEATURE_DATASET_v1.0.0"


def generate_stage9_feature_dataset_artifact(
    vectors: List[MatchFeatureVector], output_dir: str
) -> Dict[str, Any]:
    """
    Generates versioned metadata artifact for STAGE9_FEATURE_DATASET_v1.0.0.
    """
    os.makedirs(output_dir, exist_ok=True)

    total_fixtures = len(vectors)
    sample_feats = list(vectors[0].features.keys()) if vectors else []

    artifact_metadata = {
        "feature_dataset_version": STAGE9_FEATURE_DATASET_VERSION_LABEL,
        "input_entity_mapping_version": "STAGE8_ENTITY_MAPPING_v1.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_fixtures_processed": total_fixtures,
        "feature_count": len(sample_feats),
        "feature_list": sample_feats,
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
