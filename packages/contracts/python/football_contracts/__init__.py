from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ValidationState(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    LIKELY = "LIKELY"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"
    UNAVAILABLE = "UNAVAILABLE"
    REJECTED = "REJECTED"
    PENDING_EVIDENCE = "PENDING_EVIDENCE"


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    ABANDONED = "ABANDONED"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"


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


class IngestionStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


# Domain Entities

class SourceRef(BaseModel):
    id: str
    code: str
    name: str
    source_type: str
    base_url: Optional[str] = None
    license_notes: Optional[str] = None
    reliability_notes: Optional[str] = None
    is_active: bool = True


class Country(BaseModel):
    id: str
    code: str
    name: str
    region: Optional[str] = None
    is_active: bool = True


class Competition(BaseModel):
    id: str
    country_id: Optional[str] = None
    code: str
    name: str
    competition_type: str
    governing_body: Optional[str] = None
    is_active: bool = True


class Season(BaseModel):
    id: str
    competition_id: str
    label: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False


class Venue(BaseModel):
    id: str
    country_id: Optional[str] = None
    canonical_name: str
    city: Optional[str] = None
    capacity: Optional[int] = None
    is_active: bool = True


class Club(BaseModel):
    id: str
    country_id: str
    canonical_name: str
    short_name: Optional[str] = None
    city: Optional[str] = None
    venue_id: Optional[str] = None
    is_active: bool = True


class ClubAlias(BaseModel):
    id: str
    club_id: str
    alias_name: str
    source_id: Optional[str] = None


class ClubExternalId(BaseModel):
    id: str
    club_id: str
    source_id: str
    external_id: str
    source_club_name: Optional[str] = None


class ClubSeasonMembership(BaseModel):
    id: str
    club_id: str
    competition_id: str
    season_id: str


class Player(BaseModel):
    id: str
    country_id: Optional[str] = None
    canonical_name: str
    date_of_birth: Optional[str] = None
    position: Optional[str] = None
    is_active: bool = True


class PlayerClubMembership(BaseModel):
    id: str
    player_id: str
    club_id: str
    season_id: str
    shirt_number: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class MatchEntity(BaseModel):
    id: str
    competition_id: str
    season_id: str
    home_club_id: str
    away_club_id: str
    venue_id: Optional[str] = None
    scheduled_kickoff_utc: str
    actual_kickoff_utc: Optional[str] = None
    status: MatchStatus = MatchStatus.SCHEDULED
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    validation_state: ValidationState = ValidationState.UNVERIFIED


class MatchExternalId(BaseModel):
    id: str
    match_id: str
    source_id: str
    external_match_id: str


class MatchStatistic(BaseModel):
    id: str
    match_id: str
    club_id: Optional[str] = None
    stat_type: str
    stat_value: float
    period: str = "FULL_TIME"
    source_id: Optional[str] = None
    validation_state: ValidationState = ValidationState.VERIFIED


class MatchEvent(BaseModel):
    id: str
    match_id: str
    club_id: str
    player_id: Optional[str] = None
    event_category: str
    minute: int
    extra_minute: Optional[int] = None
    source_id: Optional[str] = None
    validation_state: ValidationState = ValidationState.VERIFIED


class MatchLineup(BaseModel):
    id: str
    match_id: str
    club_id: str
    player_id: str
    role: str = "STARTING"
    position: Optional[str] = None
    shirt_number: Optional[int] = None
    source_id: Optional[str] = None


class RawSourcePayload(BaseModel):
    id: str
    source_id: str
    entity_type: str
    external_identifier: str
    raw_payload_json: str
    retrieved_at_utc: str
    ingestion_run_id: Optional[str] = None


class ProvenanceRecord(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    source_id: str
    source_url: Optional[str] = None
    retrieved_at_utc: str
    validation_state: ValidationState = ValidationState.UNVERIFIED
    notes: Optional[str] = None


class DatasetVersion(BaseModel):
    id: str
    version_label: str
    cutoff_timestamp_utc: str
    record_count: int = 0
    notes: Optional[str] = None


class IngestionRun(BaseModel):
    id: str
    source_id: str
    status: IngestionStatus = IngestionStatus.STARTED
    records_ingested: int = 0
    error_log: Optional[str] = None
    started_at_utc: str
    completed_at_utc: Optional[str] = None


# References for lightweight rendering

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
