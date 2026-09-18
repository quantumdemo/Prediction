"""
Stage 11 ML Base Forecaster & Feature Extraction Framework

Handles extraction, feature filtering, missing-data imputation, and contract validation
for supervised machine learning models in Stage 11.
Strictly excludes targets, bookmaker odds, synthetic xG, and cluster labels.
Fits imputation transformers exclusively on training data to prevent temporal data leakage.
"""

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.impute import SimpleImputer

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.models.base import BaseStatisticalModel, ForecastOutput

# Stage 9 features used as numerical predictor inputs
ML_FEATURE_NAMES: List[str] = sorted(list(STAGE9_FEATURE_REGISTRY.keys()))

# Explicit Exclusions Record
EXCLUDED_FIELDS_RECORD: Dict[str, str] = {
    "fixture_id": "Non-numeric string identifier",
    "match_date": "Temporal metadata; chronological split key",
    "competition_id": "Categorical string ID",
    "season_id": "Categorical string ID",
    "home_club_id": "Categorical string ID",
    "away_club_id": "Categorical string ID",
    "full_time_home_goals": "Target variable (Strict Leakage Exclusion)",
    "full_time_away_goals": "Target variable (Strict Leakage Exclusion)",
    "full_time_result": "Target variable (Strict Leakage Exclusion)",
    "total_goals": "Target variable (Strict Leakage Exclusion)",
    "btts": "Target variable (Strict Leakage Exclusion)",
    "bookmaker_odds": "Prohibited predictive input per Master Specification",
    "synthetic_xg": "Unverified raw provider data (Rejected)",
    "ClusterLabel": "Post-match/unverified cluster label (Leakage Exclusion)",
    "ClusterProb": "Post-match/unverified cluster probability (Leakage Exclusion)",
}


class MLFeatureProcessor:
    """
    Extracts and imputes numeric feature matrices from Stage 9 MatchFeatureVectors.
    Fits imputer strictly on training vectors to guarantee zero temporal data leakage.
    """

    def __init__(self):
        self.feature_names = ML_FEATURE_NAMES
        self.imputer = SimpleImputer(strategy="median", add_indicator=True)
        self.is_fitted = False

    def extract_raw_feature_matrix(self, vectors: List[MatchFeatureVector]) -> np.ndarray:
        """
        Extracts raw numerical feature matrix X (n_samples x n_features) from Stage 9 vectors.
        Missing values are represented as np.nan.
        """
        matrix = []
        for vec in vectors:
            row = []
            for fname in self.feature_names:
                val = vec.features.get(fname)
                row.append(val if val is not None else np.nan)
            matrix.append(row)
        return np.array(matrix, dtype=float)

    def fit_transform(self, training_vectors: List[MatchFeatureVector]) -> np.ndarray:
        """
        Fits imputer strictly on training vectors and returns transformed feature matrix.
        """
        raw_X = self.extract_raw_feature_matrix(training_vectors)
        if raw_X.size == 0:
            return raw_X
        X_imputed = self.imputer.fit_transform(raw_X)
        self.is_fitted = True
        return X_imputed

    def transform(self, test_vectors: List[MatchFeatureVector]) -> np.ndarray:
        """
        Transforms test vectors using the fitted training imputer.
        """
        if not self.is_fitted:
            raise ValueError("MLFeatureProcessor must be fitted on training data before transforming test data.")
        raw_X = self.extract_raw_feature_matrix(test_vectors)
        if raw_X.size == 0:
            return raw_X
        return self.imputer.transform(raw_X)

    @staticmethod
    def extract_targets(vectors: List[MatchFeatureVector]) -> Dict[str, np.ndarray]:
        """
        Extracts target arrays for 1X2, BTTS, Over/Under 2.5, and Home/Away Goals.
        """
        y_1x2 = []
        y_btts = []
        y_over25 = []
        y_home_goals = []
        y_away_goals = []

        for vec in vectors:
            t = vec.targets
            y_1x2.append(t.get("full_time_result", "D"))
            y_btts.append(1 if t.get("btts") is True else 0)
            y_over25.append(1 if t.get("total_goals", 0) > 2.5 else 0)
            y_home_goals.append(float(t.get("full_time_home_goals", 0)))
            y_away_goals.append(float(t.get("full_time_away_goals", 0)))

        return {
            "1x2": np.array(y_1x2),
            "btts": np.array(y_btts, dtype=int),
            "over25": np.array(y_over25, dtype=int),
            "home_goals": np.array(y_home_goals, dtype=float),
            "away_goals": np.array(y_away_goals, dtype=float),
        }


class BaseMLForecaster(BaseStatisticalModel, ABC):
    """
    Abstract base interface for Stage 11 Supervised ML Forecasters.
    """

    def __init__(self, model_name: str, model_version: str = "1.0.0"):
        super().__init__(model_name=model_name, model_version=model_version)
        self.processor = MLFeatureProcessor()

    @abstractmethod
    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        """
        Fits ML models on training vectors.
        """
        pass

    @abstractmethod
    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        """
        Generates forecast output for a single target fixture.
        """
        pass

    def predict_batch(self, vectors: List[MatchFeatureVector]) -> List[ForecastOutput]:
        """
        Generates forecast outputs for a batch of fixtures.
        """
        if not vectors:
            return []
        return [self.predict_fixture(v) for v in vectors]

    def build_forecast_output(
        self,
        vector: MatchFeatureVector,
        p_home: float,
        p_draw: float,
        p_away: float,
        p_btts_yes: float,
        lambda_h: float,
        lambda_a: float,
        max_goals: int = 10,
    ) -> ForecastOutput:
        """
        Builds mathematically consistent ForecastOutput deriving score matrix
        and ALL total goals probabilities strictly from model expectations and joint distributions.
        Zero hardcoded offsets or hardcoded probabilities.
        """
        # Ensure 1X2 sum = 1.0
        sum_1x2 = p_home + p_draw + p_away
        if sum_1x2 > 0:
            p_home /= sum_1x2
            p_draw /= sum_1x2
            p_away /= sum_1x2

        p_btts_yes = max(0.0, min(1.0, p_btts_yes))
        p_btts_no = 1.0 - p_btts_yes

        # Construct Poisson joint score matrix from predicted lambda_h, lambda_a
        h_p = np.array([self._poisson_pmf(k, lambda_h) for k in range(max_goals + 1)])
        a_p = np.array([self._poisson_pmf(k, lambda_a) for k in range(max_goals + 1)])
        matrix = np.outer(h_p, a_p)
        total_p = np.sum(matrix)
        if total_p > 0:
            matrix /= total_p

        # Mathematically calculate Totals probabilities for ALL lines directly from joint score matrix
        grid_h, grid_a = np.indices(matrix.shape)
        totals = {}
        for threshold, val in [("0_5", 0.5), ("1_5", 1.5), ("2_5", 2.5), ("3_5", 3.5), ("4_5", 4.5)]:
            k = int(math.floor(val))
            p_over = float(np.sum(matrix[grid_h + grid_a > k]))
            p_under = max(0.0, 1.0 - p_over)
            totals[f"over_{threshold}"] = p_over
            totals[f"under_{threshold}"] = p_under

        score_matrix_dict = {}
        for h_g in range(max_goals + 1):
            score_matrix_dict[h_g] = {}
            for a_g in range(max_goals + 1):
                score_matrix_dict[h_g][a_g] = float(matrix[h_g, a_g])

        output = ForecastOutput(
            fixture_id=vector.fixture_id,
            match_date=vector.match_date,
            model_name=self.model_name,
            model_version=self.model_version,
            expected_home_goals=lambda_h,
            expected_away_goals=lambda_a,
            probabilities_1x2={"home": p_home, "draw": p_draw, "away": p_away},
            probabilities_totals=totals,
            probabilities_btts={"btts_yes": p_btts_yes, "btts_no": p_btts_no},
            correct_score_matrix=score_matrix_dict,
            data_quality_status="ML_PREDICTION",
        )

        val_errors = output.validate()
        if val_errors:
            raise ValueError(f"{self.model_name} output validation failed: {val_errors}")

        return output

    @staticmethod
    def _poisson_pmf(k: int, mu: float) -> float:
        return (mu**k) * math.exp(-mu) / math.factorial(k)
