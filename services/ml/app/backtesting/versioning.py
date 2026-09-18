"""
Stage 12 Backtest Versioning and Artifact Management Module

Serializes versioned backtest metadata artifacts (STAGE12_BACKTEST_ARTIFACT_v1.0.0).
Ensures full auditability, reproducibility, and metric tracking across historical windows.
"""

import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger("football_ml.backtesting.versioning")

STAGE12_BACKTEST_ARTIFACT_VERSION = "STAGE12_BACKTEST_ARTIFACT_v1.0.0"


def generate_backtest_artifact(report_data: Dict[str, Any], output_dir: str = "/tmp/stage12_artifacts") -> Dict[str, Any]:
    """
    Exports Backtest Report to a versioned JSON artifact.
    """
    os.makedirs(output_dir, exist_ok=True)

    artifact_payload = {
        "artifact_version": STAGE12_BACKTEST_ARTIFACT_VERSION,
        "report": report_data,
    }

    file_path = os.path.join(output_dir, "stage12_backtest_report.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(artifact_payload, f, indent=2)

    logger.info(f"Exported Stage 12 backtest artifact to {file_path}")
    return artifact_payload
