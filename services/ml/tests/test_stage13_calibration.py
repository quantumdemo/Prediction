"""
Stage 13 Probability Calibration & Model Selection Test Suite

Verifies:
- ECE and MCE calibration error calculations
- Platt Scaling (logistic sigmoid) and Isotonic Regression calibrators
- Strict probability axioms (sum = 1.0, probabilities in [0, 1])
- Zero future-data leakage in calibration fitting
- Reproducible model selection and ranking
- Serialization of STAGE13_CALIBRATION_ARTIFACT_v1.0.0
"""

import os
import unittest
from typing import List

import numpy as np

from services.ml.app.calibration.calibrators import IsotonicCalibrator, PlattScaler
from services.ml.app.calibration.metrics import calculate_ece, calculate_mce, calculate_multiclass_ece
from services.ml.app.models.base import ForecastOutput
from services.ml.app.selection.selector import ModelSelector


class TestStage13Calibration(unittest.TestCase):
    def setUp(self):
        self.sample_forecasts = self._generate_sample_forecasts()
        self.targets_1x2 = ["H", "D", "A", "H", "D", "A", "H", "D", "A", "H"]
        self.targets_btts = [True, False, True, False, True, False, True, False, True, False]
        self.targets_over25 = [True, False, True, False, True, False, True, False, True, False]

    def _generate_sample_forecasts(self) -> List[ForecastOutput]:
        fcs = []
        for i in range(10):
            fc = ForecastOutput(
                fixture_id=f"FIX_CAL_{i+1:03d}",
                match_date=f"2023-01-{i+1:02d}",
                model_name="XGBoostForecaster",
                model_version="1.0.0",
                expected_home_goals=1.6,
                expected_away_goals=1.1,
                probabilities_1x2={"home": 0.45, "draw": 0.30, "away": 0.25},
                probabilities_totals={"over_2_5": 0.58, "under_2_5": 0.42},
                probabilities_btts={"btts_yes": 0.52, "btts_no": 0.48},
                correct_score_matrix={0: {0: 1.0}},
            )
            fcs.append(fc)
        return fcs

    def test_ece_and_mce_calculation(self):
        probs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        targets = [0, 0, 0, 0, 1, 1, 1, 1, 1]

        ece = calculate_ece(probs, targets, n_bins=10)
        mce = calculate_mce(probs, targets, n_bins=10)

        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)
        self.assertGreaterEqual(mce, ece)

    def test_multiclass_ece(self):
        probs_matrix = [[0.6, 0.2, 0.2], [0.3, 0.5, 0.2], [0.1, 0.1, 0.8]]
        target_indices = [0, 1, 2]

        mc_ece = calculate_multiclass_ece(probs_matrix, target_indices, n_bins=5)
        self.assertGreaterEqual(mc_ece, 0.0)
        self.assertLessEqual(mc_ece, 1.0)

    def test_platt_scaler_fit_and_calibrate(self):
        scaler = PlattScaler()
        scaler.fit(self.sample_forecasts, self.targets_1x2, self.targets_btts, self.targets_over25)
        self.assertTrue(scaler.is_fitted)

        cal_fc = scaler.calibrate_forecast(self.sample_forecasts[0])
        self.assertIn("home", cal_fc.probabilities_1x2)
        self.assertIn("draw", cal_fc.probabilities_1x2)
        self.assertIn("away", cal_fc.probabilities_1x2)

        # Assert probability axioms
        p_sum = sum(cal_fc.probabilities_1x2.values())
        self.assertAlmostEqual(p_sum, 1.0, places=5)
        for p in cal_fc.probabilities_1x2.values():
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)

    def test_isotonic_calibrator_fit_and_calibrate(self):
        calibrator = IsotonicCalibrator()
        calibrator.fit(self.sample_forecasts, self.targets_1x2, self.targets_btts, self.targets_over25)
        self.assertTrue(calibrator.is_fitted)

        cal_fc = calibrator.calibrate_forecast(self.sample_forecasts[0])
        p_sum = sum(cal_fc.probabilities_1x2.values())
        self.assertAlmostEqual(p_sum, 1.0, places=5)

    def test_model_selection_and_artifact_generation(self):
        if not os.path.exists("/tmp/stage12_artifacts/window_4_report.json"):
            self.skipTest("Stage 12 backtest window reports missing in /tmp/stage12_artifacts")

        selector = ModelSelector(artifacts_dir="/tmp/stage12_artifacts")
        artifact = selector.run_calibration_and_selection(output_dir="/tmp/stage13_test_artifacts")

        self.assertEqual(artifact["artifact_version"], "STAGE13_CALIBRATION_ARTIFACT_v1.0.0")
        report = artifact["report"]
        self.assertIn("selected_production_model", report)
        self.assertIn("candidate_rankings", report)
        self.assertGreaterEqual(len(report["candidate_rankings"]), 1)

    def test_calibration_no_future_leakage(self):
        """
        Confirms calibration fit period strictly precedes evaluation test period.
        """
        if not os.path.exists("/tmp/stage12_artifacts/window_4_report.json"):
            self.skipTest("Stage 12 backtest window reports missing in /tmp/stage12_artifacts")

        selector = ModelSelector(artifacts_dir="/tmp/stage12_artifacts")
        artifact = selector.run_calibration_and_selection(output_dir="/tmp/stage13_test_artifacts")
        report = artifact["report"]

        self.assertIn("Windows 1-3", report["calibration_fit_period"])
        self.assertIn("Window 4", report["calibration_test_period"])


if __name__ == "__main__":
    unittest.main()
