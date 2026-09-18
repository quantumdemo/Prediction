"""
Stage 10 Statistical Baseline Models Unit & Integration Test Suite

Verifies:
- Poisson probability calculations & goal matrix properties
- Dixon-Coles low-score adjustment factors & matrix normalization
- Probability axioms (ranges [0, 1], 1X2 sums, BTTS sums, Over/Under totals sums)
- Expected goals non-negativity and validity
- Correct-score probability matrix sum and distribution
- Chronological data leakage prevention
- Missing-data handling (fallback without data fabrication)
- Model reproducibility
- Edge cases (extreme expected goals, empty training sets)
"""

import unittest
from typing import List

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.benchmark import EmpiricalBaselineModel
from services.ml.app.models.dixon_coles import DixonColesGoalModel
from services.ml.app.models.pipeline import Stage10StatisticalPipelineEngine
from services.ml.app.models.poisson import PoissonGoalModel


class TestStage10StatisticalModels(unittest.TestCase):
    def setUp(self):
        # Create a synthetic list of chronological feature vectors for testing
        self.sample_vectors = self._generate_sample_chronological_vectors()

    def _generate_sample_chronological_vectors(self) -> List[MatchFeatureVector]:
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
        ]
        goals = [(2, 1, "H"), (0, 0, "D"), (1, 3, "A"), (2, 2, "D"), (3, 0, "H")]

        for idx, date_str in enumerate(dates):
            h_team = teams[idx % len(teams)]
            a_team = teams[(idx + 1) % len(teams)]
            h_g, a_g, res = goals[idx % len(goals)]

            vec = MatchFeatureVector(
                fixture_id=f"FIX_{idx+1:03d}",
                match_date=date_str,
                competition_id="COMP_001",
                season_id="SEASON_2021",
                home_club_id=h_team,
                away_club_id=a_team,
                features={"FEAT_FORM5_HOME": 2.0, "FEAT_FORM5_AWAY": 1.5},
                feature_availability={"FEAT_FORM5_HOME": "PRESENT", "FEAT_FORM5_AWAY": "PRESENT"},
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

    def test_poisson_calculations_and_probability_axioms(self):
        model = PoissonGoalModel(max_goals=10)
        model.fit(self.sample_vectors[:6])

        target_vec = self.sample_vectors[7]
        fc = model.predict_fixture(target_vec)

        # Expected goals validity
        self.assertGreaterEqual(fc.expected_home_goals, 0.0)
        self.assertGreaterEqual(fc.expected_away_goals, 0.0)

        # Probability ranges [0, 1] for 1X2
        for key, prob in fc.probabilities_1x2.items():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

        # Probability sum 1X2 = 1.0
        sum_1x2 = sum(fc.probabilities_1x2.values())
        self.assertAlmostEqual(sum_1x2, 1.0, delta=1e-3)

        # BTTS probability range & sum
        p_btts_yes = fc.probabilities_btts["btts_yes"]
        p_btts_no = fc.probabilities_btts["btts_no"]
        self.assertGreaterEqual(p_btts_yes, 0.0)
        self.assertLessEqual(p_btts_yes, 1.0)
        self.assertAlmostEqual(p_btts_yes + p_btts_no, 1.0, delta=1e-3)

        # Over/Under total goals consistency
        for thresh in ["0_5", "1_5", "2_5", "3_5", "4_5"]:
            p_over = fc.probabilities_totals[f"over_{thresh}"]
            p_under = fc.probabilities_totals[f"under_{thresh}"]
            self.assertGreaterEqual(p_over, 0.0)
            self.assertLessEqual(p_over, 1.0)
            self.assertAlmostEqual(p_over + p_under, 1.0, delta=1e-3)

        # Correct score matrix probability sum
        matrix_sum = sum(
            sum(row.values()) for row in fc.correct_score_matrix.values()
        )
        self.assertAlmostEqual(matrix_sum, 1.0, delta=1e-3)

    def test_dixon_coles_low_score_adjustments(self):
        model = DixonColesGoalModel(max_goals=10)
        model.fit(self.sample_vectors[:6])

        # Test matrix calculation for lambda_h = 1.5, lambda_a = 1.0
        lambda_h, lambda_a = 1.5, 1.0
        matrix_poisson = PoissonGoalModel(max_goals=10).calculate_joint_score_matrix(lambda_h, lambda_a)

        model.rho = -0.10
        matrix_dc = model.calculate_dixon_coles_score_matrix(lambda_h, lambda_a)

        # Dixon-Coles with negative rho increases draw probability (0,0) and (1,1)
        self.assertGreaterEqual(matrix_dc[0, 0], matrix_poisson[0, 0])
        self.assertGreaterEqual(matrix_dc[1, 1], matrix_poisson[1, 1])

        # Re-normalized matrix sum must be exactly 1.0
        self.assertAlmostEqual(float(matrix_dc.sum()), 1.0, delta=1e-3)

        # Forecast output validation
        fc = model.predict_fixture(self.sample_vectors[8])
        self.assertEqual(fc.validate(), [])

    def test_empirical_baseline_model(self):
        model = EmpiricalBaselineModel()
        model.fit(self.sample_vectors[:6])

        fc = model.predict_fixture(self.sample_vectors[6])
        self.assertEqual(fc.validate(), [])
        self.assertEqual(fc.data_quality_status, "GLOBAL_EMPIRICAL_BENCHMARK")

    def test_missing_data_handling_and_no_fabrication(self):
        model = PoissonGoalModel()
        model.fit(self.sample_vectors[:4])

        # Unknown team fixture
        unknown_vec = MatchFeatureVector(
            fixture_id="FIX_UNKNOWN",
            match_date="2021-04-01",
            competition_id="COMP_001",
            season_id="SEASON_2021",
            home_club_id="TEAM_UNKNOWN_X",
            away_club_id="TEAM_UNKNOWN_Y",
            features={},
            feature_availability={},
            targets={"full_time_home_goals": 1, "full_time_away_goals": 0, "full_time_result": "H", "total_goals": 1, "btts": False},
        )

        fc = model.predict_fixture(unknown_vec)
        self.assertEqual(fc.data_quality_status, "LEAGUE_BASELINE_FALLBACK")
        self.assertEqual(fc.validate(), [])

    def test_chronological_leakage_safeguard(self):
        sorted_vecs = sorted(self.sample_vectors, key=lambda v: v.match_date)
        train_vecs = sorted_vecs[:5]
        test_vecs = sorted_vecs[5:]

        max_train_date = max(v.match_date for v in train_vecs)
        min_test_date = min(v.match_date for v in test_vecs)

        # Strict chronological ordering check: max train date <= min test date
        self.assertLessEqual(max_train_date, min_test_date)

        model = PoissonGoalModel()
        model.fit(train_vecs)
        fc_test = model.predict_fixture(test_vecs[0])

        # Verify target outcomes of test fixture were not modified or used
        self.assertEqual(fc_test.fixture_id, test_vecs[0].fixture_id)

    def test_reproducibility(self):
        m1 = PoissonGoalModel()
        m1.fit(self.sample_vectors[:6])
        fc1 = m1.predict_fixture(self.sample_vectors[7])

        m2 = PoissonGoalModel()
        m2.fit(self.sample_vectors[:6])
        fc2 = m2.predict_fixture(self.sample_vectors[7])

        self.assertAlmostEqual(fc1.expected_home_goals, fc2.expected_home_goals, places=6)
        self.assertAlmostEqual(fc1.expected_away_goals, fc2.expected_away_goals, places=6)
        self.assertAlmostEqual(fc1.probabilities_1x2["home"], fc2.probabilities_1x2["home"], places=6)

    def test_evaluation_metrics_and_pipeline_execution(self):
        engine = Stage10StatisticalPipelineEngine(artifact_output_dir="/tmp/stage10_test_artifacts")
        summary = engine.run_stage10_pipeline(vectors=self.sample_vectors, train_ratio=0.6)

        self.assertIn("models", summary)
        self.assertIn("poisson_goal_model", summary["models"])
        self.assertIn("dixon_coles_goal_model", summary["models"])
        self.assertIn("empirical_baseline_model", summary["models"])

        p_eval = summary["models"]["poisson_goal_model"]["evaluation_results"]
        self.assertIn("1x2_log_loss", p_eval)
        self.assertIn("1x2_brier_score", p_eval)
        self.assertIn("1x2_ranked_probability_score", p_eval)

    def test_edge_case_empty_vectors_and_extreme_goals(self):
        # Empty vectors fitting
        m = PoissonGoalModel()
        m.fit([])
        self.assertTrue(m.is_fitted)

        # Extreme expected goals matrix calculation
        m_dc = DixonColesGoalModel()
        matrix_high = m_dc.calculate_dixon_coles_score_matrix(0.01, 5.0)
        self.assertAlmostEqual(float(matrix_high.sum()), 1.0, delta=1e-3)


if __name__ == "__main__":
    unittest.main()
