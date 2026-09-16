from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ValidationState(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    PENDING_EVIDENCE = "PENDING_EVIDENCE"

class PredictionStatus(str, Enum):
    VALID_PREDICTION = "VALID_PREDICTION"
    NO_BET = "NO_BET"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNSUPPORTED_FIXTURE = "UNSUPPORTED_FIXTURE"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    TIMEOUT = "TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

class EvidenceTier(str, Enum):
    OFFICIAL = "OFFICIAL"
    REPUTABLE_MEDIA = "REPUTABLE_MEDIA"
    UNVERIFIED_SEARCH = "UNVERIFIED_SEARCH"

class MarketType(str, Enum):
    MATCH_RESULT_1X2 = "1X2"
    TOTAL_GOALS_OVER_UNDER = "TOTAL_GOALS_OU"
    BOTH_TEAMS_TO_SCORE = "BTTS"

class CompetitionRef(BaseModel):
    id: str
    code: str
    name: str
    country: str

class TeamRef(BaseModel):
    id: str
    canonical_name: str
    country: str

class FixtureIdentification(BaseModel):
    fixture_id: str
    season: str
    competition: CompetitionRef
    home_team: TeamRef
    away_team: TeamRef
    scheduled_kickoff_utc: str
    validation_state: ValidationState = ValidationState.UNVERIFIED

class EvidenceItem(BaseModel):
    id: str
    tier: EvidenceTier
    source_url: str
    title: str
    extracted_at_utc: str
    snippet: Optional[str] = None
    reliability_score: float = Field(ge=0.0, le=1.0)

class ModelMetadata(BaseModel):
    model_id: str
    model_name: str
    version: str
    model_type: str
    trained_at_utc: str
    calibration_method: Optional[str] = None

class DatasetMetadata(BaseModel):
    dataset_id: str
    cutoff_timestamp_utc: str
    record_count: int

class PredictionRequest(BaseModel):
    fixture_id: str
    correlation_id: str
    requested_markets: Optional[List[MarketType]] = None
    force_fresh_research: bool = False

class ProbabilityDistribution(BaseModel):
    home_win_prob: Optional[float] = None
    draw_prob: Optional[float] = None
    away_win_prob: Optional[float] = None
    over_prob: Optional[float] = None
    under_prob: Optional[float] = None
    btts_yes_prob: Optional[float] = None
    btts_no_prob: Optional[float] = None

class PredictionResponse(BaseModel):
    prediction_id: str
    fixture: FixtureIdentification
    status: PredictionStatus
    no_bet_reason: Optional[str] = None
    probabilities: Optional[ProbabilityDistribution] = None
    recommended_market: Optional[MarketType] = None
    confidence_score: Optional[float] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    model_metadata: Optional[ModelMetadata] = None
    dataset_metadata: Optional[DatasetMetadata] = None
    generated_at_utc: str
    correlation_id: str

class StructuredErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    location: Optional[str] = None

class StructuredErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]
    timestamp_utc: str
    correlation_id: str

class StructuredSuccessResponse(BaseModel):
    success: bool = True
    data: Any
    timestamp_utc: str
    correlation_id: str
