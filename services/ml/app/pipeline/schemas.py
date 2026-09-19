"""
Stage 16 Feature Update & Forecasting Pipeline Schemas

Defines Pydantic models for current feature provenance, feature update results,
and structured CurrentMatchForecastContainer output schemas.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.ml.app.models.base import ForecastOutput
from services.ml.app.research.schemas import FixtureVerification, ResearchState


class CurrentFeatureProvenance(BaseModel):
    feature_id: str
    updated_value: Optional[float] = None
    original_historical_value: Optional[float] = None
    source_fact_id: str
    source_name: str
    source_url: str
    evidence_state: ResearchState
    update_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    transformation_rule: str
    missingness_state: str = "PRESENT"  # PRESENT, INSUFFICIENT_HISTORY, MISSING_SOURCE_DATA, PRESERVE_NULL


class FeatureUpdateResult(BaseModel):
    fixture_id: str
    prediction_timestamp_utc: str
    updated_features: Dict[str, Optional[float]] = Field(default_factory=dict)
    feature_provenance_records: List[CurrentFeatureProvenance] = Field(default_factory=list)
    quarantined_reasons: List[str] = Field(default_factory=list)
    is_prediction_time_safe: bool = True


class CurrentMatchForecastContainer(BaseModel):
    container_id: str
    fixture: FixtureVerification
    prediction_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_feature_vector: Dict[str, Optional[float]] = Field(default_factory=dict)
    feature_provenance: List[CurrentFeatureProvenance] = Field(default_factory=list)
    model_name: str = "XGBoostForecaster"
    model_version: str = "1.0.0_platt"
    calibration_method: str = "platt_sigmoid"
    forecast_output: Optional[ForecastOutput] = None
    validation_status: str = "READY"  # READY, BLOCKED_NO_FORECAST, QUARANTINED
    blocked_reason: Optional[str] = None
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pipeline_version: str = "STAGE16_FEATURE_UPDATE_PIPELINE_v1.0.0"
