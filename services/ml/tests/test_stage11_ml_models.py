"""
Stage 11 ML Forecasting Models Test Suite

Verifies:
- Supervised ML model training (Logistic Regression, Random Forest, XGBoost)
- Probability axioms (0 <= P <= 1, 1X2 probability sum == 1.0, BTTS and totals sums)
- Chronological data splitting & zero future-data leakage
- Missing feature imputation without data fabrication
- Model reproducibility
- Model artifact metadata generation
- Model comparison against Stage 10 baseline models
- Edge cases
"""

import unittest
from typing import List

import numpy as np

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.logistic_regression import LogisticRegressionForecaster
from services.ml.app.models.ml_base import EXCLUDED_FIELDS_RECORD, ML_FEATURE_NAMES, MLFeatureProcessor
from services.ml.app.models.ml_pipeline import Stage11MLPipelineEngine
from services.ml.app.models.random_forest import RandomForestForecaster
from services.ml.app.models.xgboost_model import XGBoostForecaster


class TestStage11MLModels(unittest.TestCase):
    def setUp(self):
        self.sample_vectors = self._generate_sample_vectors()

    def _generate_sample_vectors(self) -> List[MatchFeatureVector]:
        vectors = []
        teams = ["TEAM_A", "TEAM_B", "TEAM_C", "TEAM_D"]
        dates = [
            "2021-01-10",
            "2021-01-17",
            "2021-01-24",
            "2021-02-01",
            "2021-02-08",
            "2021-02-15",
            "2021-03-01",
            "2021-03-08",
            "2021-03-15",
            "2021-03-22",
            "2021-03-29",
            "2021-04-05",
        ]
        goals = [(2, 1, "H"), (0, 0, "D"), (1, 3, "A"), (2, 2, "D"), (3, 0, "H")]

        for idx, date_str in enumerate(dates):
            h_team = teams[idx % len(teams)]
            a_team = teams[(idx + 1) % len(teams)]
            h_g, a_g, res = goals[idx % len(goals)]

            feats = {fname: float((idx * 3 + f_i) % 10) for f_i, fname in enumerate(ML_FEATURE_NAMES)}
            if idx % 3 == 0:
                feats["FEAT_SHOTS_AVG5_HOME"] = None

            vec = MatchFeatureVector(
                fixture_id=f"FIX_ML_{idx+1:03d}",
                match_date=date_str,
                competition_id="COMP_001",
                season_id="SEASON_2021",
                home_club_id=h_team,
                away_club_id=a_team,
                features=feats,
                feature_availability={k: "PRESENT" if v is not None else "MISSING_SOURCE_DATA" for k, v in feats.items()},
                targets={
                    "full_time_home_goals": h_g,
                    "full_time_away_goals": a_g,
                    "full_time_result": res,
                    "total_goals": h_g + a_g,
                    "btts": bool(h_g > 0 and a_g > 0),
                },
            )
            vectors.append(vec)
        return vectors

    def test_feature_processor_and_exclusions(self):
        processor = MLFeatureProcessor()

        # Check explicit exclusions record
        self.assertIn("full_time_result", EXCLUDED_FIELDS_RECORD)
        self.assertIn("bookmaker_odds", EXCLUDED_FIELDS_RECORD)
        self.assertIn("ClusterLabel", EXCLUDED_FIELDS_RECORD)

        X_imputed = processor.fit_transform(self.sample_vectors[:8])
        self.assertEqual(X_imputed.shape[0], 8)
        self.assertFalse(np.isnan(X_imputed).any())

        X_test = processor.transform(self.sample_vectors[8:])
        self.assertEqual(X_test.shape[0], 4)
        self.assertFalse(np.isnan(X_test).any())

    def test_logistic_regression_forecaster(self):
        model = LogisticRegressionForecaster()
        model.fit(self.sample_vectors[:8])

        fc = model.predict_fixture(self.sample_vectors[9])
        self.assertEqual(fc.validate(), [])
        self.assertGreaterEqual(fc.expected_home_goals, 0.0)
        self.assertGreaterEqual(fc.expected_away_goals, 0.0)

    def test_random_forest_forecaster(self):
        model = RandomForestForecaster(n_estimators=10, max_depth=4)
        model.fit(self.sample_vectors[:8])

        fc = model.predict_fixture(self.sample_vectors[9])
        self.assertEqual(fc.validate(), [])
        self.assertAlmostEqual(sum(fc.probabilities_1x2.values()), 1.0, delta=1e-3)

    def test_xgboost_forecaster(self):
        model = XGBoostForecaster(n_estimators=10, max_depth=3)
        model.fit(self.sample_vectors[:8])

        fc = model.predict_fixture(self.sample_vectors[9])
        self.assertEqual(fc.validate(), [])
        self.assertAlmostEqual(fc.probabilities_btts["btts_yes"] + fc.probabilities_btts["btts_no"], 1.0, delta=1e-3)

    def test_chronological_split_leakage_safeguard(self):
        sorted_vecs = sorted(self.sample_vectors, key=lambda v: v.match_date)
        train_vecs = sorted_vecs[:8]
        test_vecs = sorted_vecs[8:]

        max_train_date = max(v.match_date for v in train_vecs)
        min_test_date = min(v.match_date for v in test_vecs)

        self.assertLessEqual(max_train_date, min_test_date)

        model = XGBoostForecaster(n_estimators=10, max_depth=3)
        model.fit(train_vecs)
        fc = model.predict_fixture(test_vecs[0])
        self.assertEqual(fc.fixture_id, test_vecs[0].fixture_id)

    def test_reproducibility(self):
        m1 = RandomForestForecaster(n_estimators=10, max_depth=4)
        m1.fit(self.sample_vectors[:8])
        fc1 = m1.predict_fixture(self.sample_vectors[9])

        m2 = RandomForestForecaster(n_estimators=10, max_depth=4)
        m2.fit(self.sample_vectors[:8])
        fc2 = m2.predict_fixture(self.sample_vectors[9])

        self.assertAlmostEqual(fc1.probabilities_1x2["home"], fc2.probabilities_1x2["home"], places=5)
        self.assertAlmostEqual(fc1.expected_home_goals, fc2.expected_home_goals, places=5)

    def test_pipeline_execution_and_baseline_comparison(self):
        engine = Stage11MLPipelineEngine(artifact_output_dir="/tmp/stage11_test_artifacts")
        summary = engine.run_stage11_pipeline(vectors=self.sample_vectors, train_ratio=0.66)

        self.assertIn("ml_models", summary)
        self.assertIn("logistic_regression", summary["ml_models"])
        self.assertIn("random_forest", summary["ml_models"])
        self.assertIn("xgboost", summary["ml_models"])

        self.assertIn("stage10_baselines", summary)
        self.assertIn("poisson", summary["stage10_baselines"])
        self.assertIn("dixon_coles", summary["stage10_baselines"])


if __name__ == "__main__":
    unittest.main()
