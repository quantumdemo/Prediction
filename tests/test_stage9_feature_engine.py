import hashlib
import json
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.ml.app.features.engine import Stage9FeatureEngine  # noqa: E402
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY  # noqa: E402
from services.ml.app.features.versioning import (  # noqa: E402
    compute_feature_level_coverage_report,
)

DOCS_DIR = os.path.join(ROOT_DIR, "docs")


class TestStage9FeatureEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Stage9FeatureEngine()
        cls.vectors = cls.engine.calculate_features_for_all_fixtures()

    def test_required_stage9_documentation_exists(self):
        required_docs = [
            "STAGE9_FEATURE_ENGINEERING_SPECIFICATION.md",
            "STAGE9_FEATURE_REGISTRY.md",
            "STAGE9_FEATURE_QUALITY_REPORT.md",
            "STAGE9_LEAKAGE_AUDIT.md",
            "STAGE9_FEATURE_DATASET.md",
            "STAGE9_IMPLEMENTATION.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 9 documentation file '{filename}' must exist in docs/",
            )

    def test_exact_feature_count_and_registry_match(self):
        self.assertEqual(len(STAGE9_FEATURE_REGISTRY), 55)
        first_vec = self.vectors[0]
        self.assertEqual(len(first_vec.features), 55)
        self.assertEqual(set(first_vec.features.keys()), set(STAGE9_FEATURE_REGISTRY.keys()))

    def test_complete_feature_metadata(self):
        for fid, defn in STAGE9_FEATURE_REGISTRY.items():
            self.assertEqual(defn.feature_id, fid)
            self.assertTrue(defn.name)
            self.assertTrue(defn.family)
            self.assertTrue(defn.description)
            self.assertTrue(defn.calculation_formula)
            self.assertTrue(defn.window_type)
            self.assertIsNotNone(defn.minimum_history_required)
            self.assertTrue(defn.source_fields)
            self.assertTrue(defn.missing_data_rule)
            self.assertEqual(defn.availability_cutoff, "STRICTLY_BEFORE_MATCH_KICKOFF")
            self.assertEqual(defn.leakage_status, "SAFE_PRE_MATCH")
            self.assertEqual(defn.version, "STAGE9_FEATURE_DATASET_v1.0.0")
            self.assertTrue(defn.prediction_time_available)

    def test_preservation_of_original_18_features(self):
        original_18 = [
            "FEAT_FORM3_HOME", "FEAT_FORM5_HOME", "FEAT_FORM3_AWAY", "FEAT_FORM5_AWAY",
            "FEAT_FORM3_DIFF", "FEAT_FORM5_DIFF",
            "FEAT_GOALS_SCORED_AVG5_HOME", "FEAT_GOALS_CONCEDED_AVG5_HOME",
            "FEAT_GOALS_SCORED_AVG5_AWAY", "FEAT_GOALS_CONCEDED_AVG5_AWAY",
            "FEAT_SHOTS_AVG5_HOME", "FEAT_SHOTS_TARGET_AVG5_HOME",
            "FEAT_REST_DAYS_HOME", "FEAT_REST_DAYS_AWAY",
            "FEAT_H2H_HOME_WINS",
            "FEAT_ELO_PRE_MATCH_HOME", "FEAT_ELO_PRE_MATCH_AWAY", "FEAT_ELO_PRE_MATCH_DIFF",
        ]
        first_vec = self.vectors[0]
        for fid in original_18:
            self.assertIn(fid, first_vec.features)

    def test_new_feature_families_presence(self):
        new_families_features = [
            "FEAT_CONGESTION_7_HOME", "FEAT_CONGESTION_14_HOME", "FEAT_CONGESTION_30_HOME",
            "FEAT_CONGESTION_7_AWAY", "FEAT_CONGESTION_14_AWAY", "FEAT_CONGESTION_30_AWAY",
            "FEAT_CONGESTION_7_DIFF", "FEAT_CONGESTION_14_DIFF", "FEAT_CONGESTION_30_DIFF",
            "FEAT_CORNERS_AVG5_HOME", "FEAT_CORNERS_AVG5_AWAY", "FEAT_CORNERS_AVG5_DIFF",
            "FEAT_FOULS_AVG5_HOME", "FEAT_FOULS_AVG5_AWAY", "FEAT_FOULS_AVG5_DIFF",
            "FEAT_YELLOW_CARDS_AVG5_HOME", "FEAT_YELLOW_CARDS_AVG5_AWAY",
            "FEAT_YELLOW_CARDS_AVG5_DIFF",
            "FEAT_RED_CARDS_AVG5_HOME", "FEAT_RED_CARDS_AVG5_AWAY", "FEAT_RED_CARDS_AVG5_DIFF",
            "FEAT_CLEAN_SHEET_RATE5_HOME", "FEAT_CLEAN_SHEET_RATE5_AWAY",
            "FEAT_CLEAN_SHEET_RATE5_DIFF",
            "FEAT_FAILED_TO_SCORE_RATE5_HOME", "FEAT_FAILED_TO_SCORE_RATE5_AWAY",
            "FEAT_FAILED_TO_SCORE_RATE5_DIFF",
            "FEAT_BTTS_RATE5_HOME", "FEAT_BTTS_RATE5_AWAY", "FEAT_BTTS_RATE5_DIFF",
            "FEAT_SHOTS_AVG5_AWAY", "FEAT_SHOTS_TARGET_AVG5_AWAY",
            "FEAT_SHOTS_AVG5_DIFF", "FEAT_SHOTS_TARGET_AVG5_DIFF",
        ]
        first_vec = self.vectors[0]
        for fid in new_families_features:
            self.assertIn(fid, first_vec.features)

    def test_zero_future_data_leakage_and_first_match_behavior(self):
        first_vec = self.vectors[0]
        self.assertIsNone(first_vec.features["FEAT_FORM3_HOME"])
        self.assertEqual(first_vec.feature_availability["FEAT_FORM3_HOME"], "INSUFFICIENT_HISTORY")

        # Target match outcomes MUST NOT be in feature vector
        target_keys = [
            "full_time_result", "full_time_home_goals", "full_time_away_goals",
            "total_goals", "btts",
        ]
        for target_key in target_keys:
            self.assertNotIn(target_key, first_vec.features)
            self.assertIn(target_key, first_vec.targets)

    def test_restricted_fields_completely_isolated(self):
        first_vec = self.vectors[0]
        prohibited_keys = [
            "OddHome", "OddDraw", "OddAway", "ExpectedGoalsHome", "ClusterLabel", "ClusterProb",
        ]
        for key in prohibited_keys:
            self.assertNotIn(key, first_vec.features)

    def test_feature_level_coverage_report(self):
        report = compute_feature_level_coverage_report(self.vectors)
        self.assertEqual(len(report), 55)
        for fid, stats in report.items():
            self.assertEqual(stats["total_target_fixtures"], 238837)
            self.assertIn("PRESENT", stats)
            self.assertIn("MISSING_SOURCE_DATA", stats)
            self.assertIn("INSUFFICIENT_HISTORY", stats)
            self.assertIn("coverage_percentage", stats)

    def test_quarantined_records_excluded(self):
        self.assertEqual(len(self.vectors), 238837)

    def test_deterministic_rerun_reproducibility(self):
        engine_sample1 = Stage9FeatureEngine()
        engine_sample1.stage8_engine.process_full_entity_resolution()
        all_fix = list(engine_sample1.stage8_engine.fixture_resolver.fixtures.values())
        sample_fixtures = sorted(all_fix, key=lambda f: f.match_date)[:5000]

        vecs1 = []
        for f in sample_fixtures:
            v = engine_sample1._generate_pre_match_features(f)
            vecs1.append(v.features)
            engine_sample1._update_chronological_state(f)

        engine_sample2 = Stage9FeatureEngine()
        engine_sample2.stage8_engine.process_full_entity_resolution()

        vecs2 = []
        for f in sample_fixtures:
            v = engine_sample2._generate_pre_match_features(f)
            vecs2.append(v.features)
            engine_sample2._update_chronological_state(f)

        hash1 = hashlib.sha256(json.dumps(vecs1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.sha256(json.dumps(vecs2, sort_keys=True).encode()).hexdigest()
        self.assertEqual(hash1, hash2)

    def test_no_stage10_or_ml_models_in_stage9(self):
        """
        Guard test: Ensure Stage 9 does NOT train statistical/ML models.
        """
        import services.ml.app.features.engine as engine_mod
        with open(engine_mod.__file__, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertNotIn("train_model", code)
            self.assertNotIn("predict_proba", code)
            self.assertNotIn("DixonColes", code)


if __name__ == "__main__":
    unittest.main()
