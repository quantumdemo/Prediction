"""
Stage 20 Complete End-to-End Prediction Integration Pipeline Package

Orchestrates Stages 14 through 19 sequentially:
USER MATCH INPUT -> FIXTURE VERIFICATION -> RESEARCH -> EVIDENCE VALIDATION -> FEATURE UPDATE -> FORECAST -> MARKET MAPPING -> RISK / NO-BET -> AUDITABLE REPORT -> PREDICTION HISTORY.
"""

from services.ml.app.integration.pipeline import EndToEndPredictionPipeline
from services.ml.app.integration.schemas import EndToEndPredictionResponse, PredictionPipelineRequest

__all__ = [
    "EndToEndPredictionPipeline",
    "PredictionPipelineRequest",
    "EndToEndPredictionResponse",
]
