import unittest

from services.ml.app.features.engine import Stage9FeatureEngine
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.features.versioning import (
    STAGE9_FEATURE_DATASET_VERSION_LABEL,
    generate_stage9_feature_dataset_artifact,
)


class TestStage9Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Stage9FeatureEngine()
        cls.vectors = cls.engine.calculate_features_for_all_fixtures()

    def test_full_feature_pipeline_execution_and_stability(self):
        # Check total vectors matches Stage 8 canonical fixtures (238,837)
        self.assertEqual(len(self.vectors), 238837)

        # Artifact generation check
        artifact = generate_stage9_feature_dataset_artifact(
            self.vectors, "/tmp/stage9_test_artifact"
        )
        self.assertEqual(
            artifact["feature_dataset_version"],
            STAGE9_FEATURE_DATASET_VERSION_LABEL,
        )
        self.assertEqual(artifact["feature_count"], 55)
        self.assertIn("feature_coverage_report", artifact)

    def test_feature_registry_consistency(self):
        self.assertEqual(len(STAGE9_FEATURE_REGISTRY), 55)
        for vec in self.vectors[:10]:
            self.assertEqual(len(vec.features), 55)
            self.assertEqual(len(vec.feature_availability), 55)


if __name__ == "__main__":
    unittest.main()
