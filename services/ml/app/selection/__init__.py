"""
Stage 13 Model Selection & Forecaster Registry Package

Ranks uncalibrated and calibrated forecasters on out-of-sample Log Loss, Brier Score, and ECE,
and exports the canonical STAGE13_CALIBRATION_ARTIFACT_v1.0.0 report.
"""

from services.ml.app.selection.selector import ModelSelector

__all__ = ["ModelSelector"]
