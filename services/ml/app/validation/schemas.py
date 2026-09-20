"""
Stage 22 Shadow Validation & Historical Validation Schemas

Data contracts for shadow predictions, fixture evaluation records, aggregate metrics,
no-leakage guards, and machine-readable Stage 22 artifacts.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ShadowPredictionRecord(BaseModel):
    """
    Shadow prediction output generated using ONLY pre-match input data.
    """

    prediction_id: str
    fixture_id: str
    match_date: str
    home_team: str
    away_team: str
    competition: str
    season: str
    cutoff_timestamp_utc: str
    prediction_timestamp_utc: str
    model_name: str
    model_version: str
    calibration_method: str
    probabilities_1x2: Optional[Dict[str, float]] = None
    probabilities_totals: Optional[Dict[str, float]] = None
    probabilities_btts: Optional[Dict[str, float]] = None
    probabilities_correct_score: Optional[Dict[str, Any]] = None
    expected_home_goals: Optional[float] = None
    expected_away_goals: Optional[float] = None
    confidence_score: float
    confidence_level: str
    decision_status: str
    is_blocked: bool
    blocked_reasons: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    audit_hash: str


class ActualMatchOutcome(BaseModel):
    """
    Actual historical match outcome kept strictly isolated from prediction inputs.
    """

    fixture_id: str
    match_date: str
    full_time_result: Optional[str] = None  # 'H', 'D', 'A'
    full_time_home_goals: Optional[int] = None
    full_time_away_goals: Optional[int] = None
    total_goals: Optional[int] = None
    btts: Optional[bool] = None


class FixtureEvaluationRecord(BaseModel):
    """
    Combined evaluation record matching a pre-match shadow prediction with actual match outcome.
    """

    fixture_id: str
    shadow_prediction: ShadowPredictionRecord
    actual_outcome: ActualMatchOutcome
    evaluated: bool = True
    evaluation_error: Optional[str] = None


class ValidationAggregateMetrics(BaseModel):
    """
    Aggregate evaluation performance metrics calculated strictly post-prediction.
    """

    total_fixtures_evaluated: int
    log_loss_1x2: Optional[float] = None
    brier_score_1x2: Optional[float] = None
    rps_1x2: Optional[float] = None
    home_goals_mae: Optional[float] = None
    away_goals_mae: Optional[float] = None
    total_goals_mae: Optional[float] = None
    over_2_5_log_loss: Optional[float] = None
    over_2_5_brier_score: Optional[float] = None
    btts_log_loss: Optional[float] = None
    btts_brier_score: Optional[float] = None
    coverage_rate: float
    no_bet_rate: float
    blocked_rate: float
    eligible_rate: float


class DataQualityValidationSummary(BaseModel):
    """
    Data quality audit summary for Stage 22 shadow testing.
    """

    total_fixtures_considered: int
    eligible_fixtures: int
    excluded_fixtures: int
    exclusion_reasons: Dict[str, int]
    no_bet_count: int
    blocked_count: int
    eligible_count: int


class ShadowValidationArtifact(BaseModel):
    """
    Machine-readable Stage 22 Validation Artifact (STAGE22_VALIDATION_ARTIFACT_v1.0.0).
    """

    artifact_version: str = "STAGE22_VALIDATION_ARTIFACT_v1.0.0"
    run_id: str
    generated_at_utc: str
    dataset_version: str
    feature_dataset_version: str
    model_name: str
    model_version: str
    calibration_method: str
    evaluation_period_start: str
    evaluation_period_end: str
    training_cutoff_date: str
    test_cutoff_date: str
    random_seed: Optional[int] = 42
    data_quality: DataQualityValidationSummary
    aggregate_metrics: ValidationAggregateMetrics
    records: List[FixtureEvaluationRecord] = Field(default_factory=list)
    leakage_guard_status: str = "VERIFIED_NO_LEAKAGE"
