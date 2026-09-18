"""
Empirical Statistical Baseline Benchmark Model

Serves as an unconditioned benchmark estimating global empirical outcome frequencies from training data.
Provides a reference line for evaluating skill scores (Log Loss, Brier, RPS) of parametric models.
"""

import math
from typing import List

import numpy as np

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import BaseStatisticalModel, ForecastOutput


class EmpiricalBaselineModel(BaseStatisticalModel):
    """
    Empirical League Baseline Model.
    Forecasts constant empirical frequencies based on historical match averages.
    """

    def __init__(self, max_goals: int = 10):
        super().__init__(model_name="EmpiricalBaselineModel", model_version="1.0.0")
        self.max_goals = max_goals
        self.p_home: float = 0.45
        self.p_draw: float = 0.26
        self.p_away: float = 0.29
        self.mu_home: float = 1.50
        self.mu_away: float = 1.10
        self.btts_rate: float = 0.52
        self.totals_rates = {
            "0_5": 0.92,
            "1_5": 0.74,
            "2_5": 0.49,
            "3_5": 0.27,
            "4_5": 0.12,
        }

    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        """
        Fits global empirical outcome probabilities across all valid historical training matches.
        """
        if not training_vectors:
            self.is_fitted = True
            return

        valid_matches = [
            v for v in training_vectors if "full_time_result" in v.targets and v.targets["full_time_result"] is not None
        ]

        n = len(valid_matches)
        if n == 0:
            self.is_fitted = True
            return

        n_home_wins = sum(1 for v in valid_matches if v.targets["full_time_result"] == "H")
        n_draws = sum(1 for v in valid_matches if v.targets["full_time_result"] == "D")
        n_away_wins = sum(1 for v in valid_matches if v.targets["full_time_result"] == "A")

        self.p_home = float(n_home_wins / n)
        self.p_draw = float(n_draws / n)
        self.p_away = float(n_away_wins / n)

        # Normalize 1X2 probabilities
        total_p = self.p_home + self.p_draw + self.p_away
        if total_p > 0:
            self.p_home /= total_p
            self.p_draw /= total_p
            self.p_away /= total_p

        total_home_goals = sum(v.targets["full_time_home_goals"] for v in valid_matches)
        total_away_goals = sum(v.targets["full_time_away_goals"] for v in valid_matches)
        self.mu_home = float(total_home_goals / n)
        self.mu_away = float(total_away_goals / n)

        # BTTS rate
        n_btts = sum(1 for v in valid_matches if v.targets["btts"] is True)
        self.btts_rate = float(n_btts / n)

        # Totals rates
        for threshold, val in [("0_5", 0.5), ("1_5", 1.5), ("2_5", 2.5), ("3_5", 3.5), ("4_5", 4.5)]:
            n_over = sum(1 for v in valid_matches if v.targets["total_goals"] > val)
            self.totals_rates[threshold] = float(n_over / n)

        self.is_fitted = True

    def calculate_empirical_score_matrix(self) -> np.ndarray:
        """
        Calculates score matrix using Poisson distribution on overall average goal rates.
        """
        h_p = np.array([self._poisson_pmf(k, self.mu_home) for k in range(self.max_goals + 1)])
        a_p = np.array([self._poisson_pmf(k, self.mu_away) for k in range(self.max_goals + 1)])

        matrix = np.outer(h_p, a_p)
        total_p = np.sum(matrix)
        if total_p > 0:
            matrix /= total_p
        return matrix

    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        matrix = self.calculate_empirical_score_matrix()

        totals = {}
        for threshold in ["0_5", "1_5", "2_5", "3_5", "4_5"]:
            over_p = self.totals_rates[threshold]
            under_p = max(0.0, 1.0 - over_p)
            totals[f"over_{threshold}"] = over_p
            totals[f"under_{threshold}"] = under_p

        btts = {"btts_yes": self.btts_rate, "btts_no": max(0.0, 1.0 - self.btts_rate)}

        score_matrix_dict = {}
        for h_g in range(self.max_goals + 1):
            score_matrix_dict[h_g] = {}
            for a_g in range(self.max_goals + 1):
                score_matrix_dict[h_g][a_g] = float(matrix[h_g, a_g])

        output = ForecastOutput(
            fixture_id=vector.fixture_id,
            match_date=vector.match_date,
            model_name=self.model_name,
            model_version=self.model_version,
            expected_home_goals=self.mu_home,
            expected_away_goals=self.mu_away,
            probabilities_1x2={
                "home": self.p_home,
                "draw": self.p_draw,
                "away": self.p_away,
            },
            probabilities_totals=totals,
            probabilities_btts=btts,
            correct_score_matrix=score_matrix_dict,
            data_quality_status="GLOBAL_EMPIRICAL_BENCHMARK",
        )

        val_errors = output.validate()
        if val_errors:
            raise ValueError(f"Empirical Baseline Forecast Output validation failed: {val_errors}")

        return output

    @staticmethod
    def _poisson_pmf(k: int, mu: float) -> float:
        return (mu**k) * math.exp(-mu) / math.factorial(k)
