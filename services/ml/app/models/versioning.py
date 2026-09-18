"""
Stage 10 Model Versioning and Artifact Management Module

Generates versioned artifacts and metadata for statistical baseline models.
Ensures full reproducibility, auditing, and metadata registration.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from services.ml.app.models.base import ModelMetadata

logger = logging.getLogger("football_ml.models.versioning")

STAGE10_MODEL_ARTIFACT_VERSION = "STAGE10_MODEL_ARTIFACT_v1.0.0"


def generate_model_artifact(metadata: ModelMetadata, output_dir: str) -> Dict[str, Any]:
    """
    Exports ModelMetadata to a versioned JSON artifact in output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    created_at = metadata.created_at_utc or datetime.now(timezone.utc).isoformat()

    artifact_payload = {
        "artifact_version": STAGE10_MODEL_ARTIFACT_VERSION,
        "model_name": metadata.model_name,
        "model_version": metadata.model_version,
        "dataset_version": metadata.dataset_version,
        "feature_version": metadata.feature_version,
        "training_period": {
            "start_date": metadata.training_period_start,
            "end_date": metadata.training_period_end,
        },
        "evaluation_period": {
            "start_date": metadata.evaluation_period_start,
            "end_date": metadata.evaluation_period_end,
        },
        "parameters": metadata.parameters,
        "configuration": metadata.configuration,
        "created_at_utc": created_at,
        "code_identifier": metadata.code_identifier,
        "evaluation_results": metadata.evaluation_results,
    }

    file_name = f"{metadata.model_name.lower()}_{metadata.model_version}_artifact.json"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(artifact_payload, f, indent=2)

    logger.info(f"Exported model artifact for {metadata.model_name} to {file_path}")
    return artifact_payload
