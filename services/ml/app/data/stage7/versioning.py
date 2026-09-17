"""
Stage 7 Dataset Staging & Versioning Artifact Exporter

Generates versioned dataset metadata, quality reports, and JSON staging artifacts
for STAGE7_VALIDATED_HISTORICAL_DATASET.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from services.ml.app.data.stage7.pipeline import Stage7CleaningPipelineEngine

logger = logging.getLogger("football_ml.data.stage7.versioning")

STAGE7_DATASET_VERSION_LABEL = "STAGE7_VALIDATED_HISTORICAL_DATASET_v1.0.0"


def generate_stage7_dataset_artifact(engine: Stage7CleaningPipelineEngine, output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)

    summary = engine.process_full_candidate_dataset()

    artifact_metadata = {
        "dataset_version": STAGE7_DATASET_VERSION_LABEL,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_dataset": "xgabora/club-football-match-data",
        "matches_sha256": "d724472b2022f71f77f218552660da5fc9f815450155bb6503b3000d5e3f868b",
        "elo_sha256": "e9f6020b2bca88ec5974aa934b5e1f3b59220729119c768404bd962a71da1343",
        "cleaning_pipeline_version": "v1.0.0-stage7",
        "summary": summary,
        "prohibitions_enforced": [
            "NO_STAGE_8_ENTITY_RESOLUTION",
            "NO_MODEL_TRAINING",
            "NO_PREDICTION_GENERATION",
            "ODDS_ISOLATED_REJECTED_ODDS",
            "PRECALCULATED_FORM_MARKED_REQUIRES_RECALCULATION",
            "SYNTHETIC_XG_ISOLATED_REJECTED_UNVERIFIED",
            "CLUSTERS_ISOLATED_REJECTED_LEAKAGE",
        ],
    }

    meta_path = os.path.join(output_dir, "stage7_dataset_version.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(artifact_metadata, f, indent=2)

    logger.info(f"Stage 7 dataset artifact metadata written to {meta_path}")
    return artifact_metadata
