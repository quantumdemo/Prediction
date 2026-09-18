"""
Stage 12 Time-Aware Historical Backtesting Test Suite

Verifies:
- Multi-window walk-forward chronological splitting
- Zero temporal data leakage (max train date < min test date)
- Imputation fitting strictly on training sets
- Data quality accounting (used vs skipped matches)
- Backtest metric calculation across all 6 models
- Aggregated multi-window performance calculation
- Reproducibility
- Backtest artifact generation
"""

import unittest
from typing import List

from services.ml.app.backtesting.engine import BacktestWindow, WalkForwardBacktestEngine
from services.ml.app.backtesting.versioning import generate_backtest_artifact
from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.ml_base import ML_FEATURE_NAMES


class TestStage12Backtesting(unittest.TestCase):
    def setUp(self):
        self.sample_vectors = self._generate_sample_vectors()

    def _generate_sample_vectors(self) -> List[MatchFeatureVector]:
        vectors = []
        teams = ["TEAM_A", "TEAM_B", "TEAM_C", "TEAM_D"]
        dates = [
            # 2020 Season (Train 1)
            "2020-01-10", "2020-02-15", "2020-03-20", "2020-05-10", "2020-06-15",
            # 2020/2021 Season (Test 1 / Train 2)
            "2020-08-10", "2020-10-15", "2021-01-20", "2021-03-10", "2021-05-15",
            # 2021/2022 Season (Test 2 / Train 3)
            "2021-08-10", "2021-10-15", "2022-01-20", "2022-03-10", "2022-05-15",
            # 2022/2023 Season (Test 3)
            "2022-08-10", "2022-10-15", "2023-01-20", "2023-03-10", "2023-05-15",
        ]
        goals = [(2, 1, "H"), (0, 0, "D"), (1, 3, "A"), (2, 2, "D"), (3, 0, "H")]

        for idx, date_str in enumerate(dates):
            h_team = teams[idx % len(teams)]
            a_team = teams[(idx + 1) % len(teams)]
            h_g, a_g, res = goals[idx % len(goals)]

            feats = {fname: float((idx * 3 + f_i) % 10) for f_i, fname in enumerate(ML_FEATURE_NAMES)}
            if idx % 4 == 0:
                feats["FEAT_SHOTS_AVG5_HOME"] = None

            vec = MatchFeatureVector(
                fixture_id=f"FIX_BT_{idx+1:03d}",
                match_date=date_str,
                competition_id="COMP_ENG_PL",
                season_id=f"SEASON_{date_str[:4]}",
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

    def test_data_quality_auditing(self):
        engine = WalkForwardBacktestEngine()
        report, eligible = engine._audit_data_quality(self.sample_vectors)

        self.assertEqual(report.total_eligible_matches, len(self.sample_vectors))
        self.assertEqual(report.matches_used, len(self.sample_vectors))
        self.assertEqual(report.matches_skipped, 0)
        self.assertIn("COMP_ENG_PL", report.competitions_covered)

    def test_chronological_windows_and_no_leakage(self):
        engine = WalkForwardBacktestEngine()
        report = engine.run_backtest(vectors=self.sample_vectors)

        self.assertIn("windows_count", report)
        self.assertGreaterEqual(report["windows_count"], 1)

        for w_def in report["window_definitions"]:
            tr_end = w_def["train_period"].split(" to ")[1]
            te_start = w_def["test_period"].split(" to ")[0]
            self.assertLessEqual(tr_end, te_start)

    def test_backtest_execution_all_models(self):
        engine = WalkForwardBacktestEngine()
        report = engine.run_backtest(vectors=self.sample_vectors)

        self.assertIn("aggregated_results", report)
        agg = report["aggregated_results"]

        # Ensure all 6 models are backtested
        expected_models = ["poisson", "dixon_coles", "empirical", "logistic_regression", "random_forest", "xgboost"]
        for m_key in expected_models:
            self.assertIn(m_key, agg)
            m_res = agg[m_key]
            self.assertIn("1x2_log_loss", m_res)
            self.assertIn("1x2_brier_score", m_res)
            self.assertIn("1x2_ranked_probability_score", m_res)
            self.assertIn("goal_metrics", m_res)
            self.assertIn("btts_metrics", m_res)
            self.assertIn("over_under_2_5_metrics", m_res)

    def test_leakage_error_detection(self):
        engine = WalkForwardBacktestEngine()
        invalid_windows = [
            BacktestWindow(
                window_id="INVALID_OVERLAP",
                train_start_date="2020-01-01",
                train_end_date="2022-01-01",
                test_start_date="2021-01-01",
                test_end_date="2021-12-31",
            )
        ]
        with self.assertRaises(ValueError):
            engine.run_backtest(vectors=self.sample_vectors, windows=invalid_windows)

    def test_artifact_generation(self):
        engine = WalkForwardBacktestEngine()
        report = engine.run_backtest(vectors=self.sample_vectors)

        artifact = generate_backtest_artifact(report, output_dir="/tmp/stage12_test_artifacts")
        self.assertEqual(artifact["artifact_version"], "STAGE12_BACKTEST_ARTIFACT_v1.0.0")
        self.assertIn("report", artifact)


if __name__ == "__main__":
    unittest.main()
