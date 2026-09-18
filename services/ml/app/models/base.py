"""
Base Statistical Model Architecture & Data Contracts

Defines abstract model interface and standardized output schemas for Stage 10 models.
Guarantees strict mathematical validity (probability axioms, non-negative goals, score matrix normalization).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from services.ml.app.features.engine import MatchFeatureVector


@dataclass
class ForecastOutput:
    fixture_id: str
    match_date: str
    model_name: str
    model_version: str
    expected_home_goals: float
    expected_away_goals: float
    probabilities_1x2: Dict[str, float]  # {"home": float, "draw": float, "away": float}
    probabilities_totals: Dict[str, float]  # {"over_1_5": float, "under_1_5": float, ...}
    probabilities_btts: Dict[str, float]  # {"btts_yes": float, "btts_no": float}
    correct_score_matrix: Dict[int, Dict[int, float]]  # home_goals -> away_goals -> prob
    data_quality_status: str = "FULL_EVIDENCE"  # "FULL_EVIDENCE", "LEAGUE_BASELINE_FALLBACK", "INSUFFICIENT_HISTORY"

    def validate(self) -> List[str]:
        """
        Validates mathematical constraints on forecast outputs.
        Returns list of error messages (empty if valid).
        """
        errors = []

        # Non-negativity check for expected goals
        if self.expected_home_goals < 0.0:
            errors.append(f"Expected home goals < 0: {self.expected_home_goals}")
        if self.expected_away_goals < 0.0:
            errors.append(f"Expected away goals < 0: {self.expected_away_goals}")

        # Probability ranges [0, 1] for 1X2
        p_home = self.probabilities_1x2.get("home", 0.0)
        p_draw = self.probabilities_1x2.get("draw", 0.0)
        p_away = self.probabilities_1x2.get("away", 0.0)

        for name, p in [("home", p_home), ("draw", p_draw), ("away", p_away)]:
            if not (0.0 <= p <= 1.0):
                errors.append(f"1X2 probability {name} outside [0, 1]: {p}")

        # Sum of 1X2 probabilities must equal ~1.0
        sum_1x2 = p_home + p_draw + p_away
        if abs(sum_1x2 - 1.0) > 1e-3:
            errors.append(f"1X2 probabilities do not sum to 1.0 (sum={sum_1x2:.6f})")

        # BTTS probability range and sum
        p_btts_yes = self.probabilities_btts.get("btts_yes", 0.0)
        p_btts_no = self.probabilities_btts.get("btts_no", 0.0)
        if not (0.0 <= p_btts_yes <= 1.0) or not (0.0 <= p_btts_no <= 1.0):
            errors.append("BTTS probabilities outside [0, 1]")
        if abs((p_btts_yes + p_btts_no) - 1.0) > 1e-3:
            errors.append(f"BTTS probabilities do not sum to 1.0 (sum={p_btts_yes + p_btts_no:.6f})")

        # Over/Under totals ranges and complementary sums
        for threshold in ["0_5", "1_5", "2_5", "3_5", "4_5"]:
            p_over = self.probabilities_totals.get(f"over_{threshold}", 0.0)
            p_under = self.probabilities_totals.get(f"under_{threshold}", 0.0)
            if not (0.0 <= p_over <= 1.0) or not (0.0 <= p_under <= 1.0):
                errors.append(f"Totals {threshold} probabilities outside [0, 1]")
            if abs((p_over + p_under) - 1.0) > 1e-3:
                errors.append(f"Totals {threshold} probabilities do not sum to 1.0")

        # Correct score matrix probabilities must sum to ~1.0 and be non-negative
        total_score_p = 0.0
        for h_g, row in self.correct_score_matrix.items():
            for a_g, p in row.items():
                if p < 0.0 or p > 1.0:
                    errors.append(f"Score matrix probability at ({h_g},{a_g}) invalid: {p}")
                total_score_p += p

        if abs(total_score_p - 1.0) > 1e-3:
            errors.append(f"Correct score matrix does not sum to 1.0 (sum={total_score_p:.6f})")

        return errors


@dataclass
class ModelMetadata:
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    training_period_start: str
    training_period_end: str
    evaluation_period_start: str
    evaluation_period_end: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at_utc: str = ""
    code_identifier: str = "STAGE10_STATISTICAL_BASELINE_v1.0"
    evaluation_results: Dict[str, Any] = field(default_factory=dict)


class BaseStatisticalModel(ABC):
    """
    Abstract base interface for Stage 10 statistical models.
    """

    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        self.is_fitted = False
        self.metadata: Optional[ModelMetadata] = None

    @abstractmethod
    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        """
        Fits model parameters on historical training vectors strictly before evaluation period.
        """
        pass

    @abstractmethod
    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        """
        Generates forecast output for a single target fixture using pre-match features.
        """
        pass

    def predict_batch(self, vectors: List[MatchFeatureVector]) -> List[ForecastOutput]:
        """
        Generates forecast outputs for a list of fixtures.
        """
        return [self.predict_fixture(v) for v in vectors]
