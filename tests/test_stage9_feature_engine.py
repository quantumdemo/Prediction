import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.ml.app.features.engine import Stage9FeatureEngine


class TestStage9FeatureEngine(unittest.TestCase):
    def test_required_stage9_documentation_exists(self):
        required_docs = [
            "STAGE9_FEATURE_ENGINEERING_SPECIFICATION.md",
            "STAGE9_FEATURE_REGISTRY.md",
            "STAGE9_FEATURE_QUALITY_REPORT.md",
            "STAGE9_LEAKAGE_AUDIT.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 9 documentation file '{filename}' must exist in docs/",
            )

    def test_zero_future_data_leakage_and_first_match_behavior(self):
        engine = Stage9FeatureEngine()
        vectors = engine.calculate_features_for_all_fixtures()

        # Vector 0 (first chronological match) MUST have INSUFFICIENT_HISTORY for Form3 and Form5
        first_vec = vectors[0]
        self.assertIsNone(first_vec.features["FEAT_FORM3_HOME"])
        self.assertEqual(first_vec.feature_availability["FEAT_FORM3_HOME"], "INSUFFICIENT_HISTORY")

        # Target match outcome MUST NOT be present in its own feature dictionary
        self.assertNotIn("full_time_result", first_vec.features)
        self.assertNotIn("full_time_home_goals", first_vec.features)

        # Targets MUST be isolated in the separate targets dictionary
        self.assertIn("full_time_result", first_vec.targets)
        self.assertIn("full_time_home_goals", first_vec.targets)

    def test_restricted_fields_completely_isolated(self):
        engine = Stage9FeatureEngine()
        vectors = engine.calculate_features_for_all_fixtures()
        first_vec = vectors[0]

        # Verify prohibited fields are absent from feature vector
        prohibited_keys = ["OddHome", "OddDraw", "OddAway", "ExpectedGoalsHome", "ClusterLabel", "ClusterProb"]
        for key in prohibited_keys:
            self.assertNotIn(key, first_vec.features)

    def test_no_stage10_or_ml_models_in_stage9(self):
        """
        Guard test: Ensure Stage 9 does NOT train statistical/ML models or generate prediction probabilities.
        """
        import services.ml.app.features.engine as engine_mod
        with open(engine_mod.__file__, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertNotIn("train_model", code)
            self.assertNotIn("predict_proba", code)
            self.assertNotIn("DixonColes", code)


if __name__ == "__main__":
    unittest.main()
