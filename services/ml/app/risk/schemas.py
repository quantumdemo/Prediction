"""
Stage 18 Risk & NO-BET Engine Pydantic Schemas

Defines decision statuses (ELIGIBLE, LOW_CONFIDENCE, HIGH_RISK, INSUFFICIENT_EVIDENCE, BLOCKED),
confidence levels (HIGH, MEDIUM, LOW), risk flags, market decision items, and complete risk reports.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DecisionStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    HIGH_RISK = "HIGH_RISK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    BLOCKED = "BLOCKED"


class RiskFlag(str, Enum):
    RISK_UNRESOLVED_EVIDENCE_CONFLICT = "RISK_UNRESOLVED_EVIDENCE_CONFLICT"
    RISK_MISSING_KEY_FEATURE = "RISK_MISSING_KEY_FEATURE"
    RISK_LOW_TOP_PROBABILITY = "RISK_LOW_TOP_PROBABILITY"
    RISK_UNSUPPORTED_MARKET = "RISK_UNSUPPORTED_MARKET"
    RISK_BLOCKED_FORECAST_CONTAINER = "RISK_BLOCKED_FORECAST_CONTAINER"
    RISK_UNSUPPORTED_MODEL_CALIBRATION = "RISK_UNSUPPORTED_MODEL_CALIBRATION"
    RISK_UNVERIFIED_FIXTURE = "RISK_UNVERIFIED_FIXTURE"
    RISK_STALE_EVIDENCE = "RISK_STALE_EVIDENCE"


class MarketDecision(BaseModel):
    market_id: str
    market_name: str
    decision_status: DecisionStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    top_outcome_id: Optional[str] = None
    top_outcome_name: Optional[str] = None
    top_probability: Optional[float] = None
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    decision_reasons: List[str] = Field(default_factory=list)
    provenance_summary: Dict[str, Any] = Field(default_factory=dict)


class RiskEngineReport(BaseModel):
    report_id: str
    fixture_id: str
    source_container_id: str
    source_market_report_id: str
    eligible_markets_count: int = 0
    no_bet_markets_count: int = 0
    blocked_markets_count: int = 0
    market_decisions: Dict[str, MarketDecision] = Field(default_factory=dict)
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_engine_version: str = "STAGE18_RISK_ENGINE_v1.0.0"
