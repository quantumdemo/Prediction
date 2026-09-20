"""
Stage 20 End-to-End Prediction Pipeline Pydantic Schemas

Defines schemas for end-to-end prediction requests and structured end-to-end responses.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.ml.app.reporting.schemas import AuditablePredictionReport


class PredictionPipelineRequest(BaseModel):
    fixture_id: str
    home_team: str
    away_team: str
    competition: str
    season: str
    match_date: str
    kickoff_time: Optional[str] = None
    venue: Optional[str] = None
    prediction_timestamp_utc: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_research_inputs: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    base_features: Optional[Dict[str, Optional[float]]] = Field(default_factory=dict)


class EndToEndPredictionResponse(BaseModel):
    prediction_id: str
    report_id: str
    audit_hash: str
    fixture_summary: Dict[str, Any]
    research_status_summary: Dict[str, Any]
    feature_status_summary: Dict[str, Any]
    model_attribution: Dict[str, str]
    forecast_summary: Optional[Dict[str, Any]] = None
    supported_markets: Dict[str, Any] = Field(default_factory=dict)
    confidence_summary: Dict[str, Any] = Field(default_factory=dict)
    risk_flags: Dict[str, List[str]] = Field(default_factory=dict)
    decision_status: str  # ELIGIBLE, LOW_CONFIDENCE, HIGH_RISK, INSUFFICIENT_EVIDENCE, BLOCKED
    blocked_reasons: Optional[List[str]] = None
    auditable_report: AuditablePredictionReport
    is_persisted: bool = True
    pipeline_version: str = "STAGE20_E2E_PREDICTION_PIPELINE_v1.0.0"
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
