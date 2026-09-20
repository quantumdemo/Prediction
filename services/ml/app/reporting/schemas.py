"""
Stage 19 Auditable Reporting & History Pydantic Schemas

Defines schemas for complete auditable prediction reports, prediction chain provenance,
historical query filters, and report retrieval payloads.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PredictionChainProvenance(BaseModel):
    fixture_id: str
    fixture_verification_method: str
    evidence_items_evaluated_count: int
    validated_evidence_count: int
    updated_features_count: int
    feature_provenance_records_count: int
    model_name: str
    model_version: str
    calibration_method: str
    supported_markets_count: int
    unsupported_markets_count: int
    evaluated_risk_flags_count: int


class AuditablePredictionReport(BaseModel):
    report_id: str
    prediction_id: str
    fixture_id: str
    prediction_timestamp_utc: str
    fixture_summary: Dict[str, Any]
    model_name: str
    model_version: str
    calibration_method: str
    forecast_probabilities: Dict[str, Any] = Field(default_factory=dict)
    market_probabilities: Dict[str, Any] = Field(default_factory=dict)
    confidence_metrics: Dict[str, Any] = Field(default_factory=dict)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    final_decision_status: str  # ELIGIBLE, LOW_CONFIDENCE, HIGH_RISK, INSUFFICIENT_EVIDENCE, BLOCKED
    decision_reasons: List[str] = Field(default_factory=list)
    blocked_reasons: Optional[List[str]] = None
    provenance_chain: PredictionChainProvenance
    audit_hash: str
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reporting_engine_version: str = "STAGE19_AUDITABLE_REPORTING_v1.0.0"


class PredictionHistoryFilter(BaseModel):
    prediction_id: Optional[str] = None
    fixture_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    market_id: Optional[str] = None
    decision_status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
