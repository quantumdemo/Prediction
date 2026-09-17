import unittest

from services.ml.app.features.engine import Stage9FeatureEngine
from services.ml.app.features.versioning import (
    STAGE9_FEATURE_DATASET_VERSION_LABEL,
    generate_stage9_feature_dataset_artifact,
)


class TestStage9Pipeline(unittest.TestCase):
    def setUp(self):
        self.engine = Stage9FeatureEngine()

    def test_full_feature_pipeline_execution_and_stability(self):
        vectors = self.engine.calculate_features_for_all_fixtures()

        # Check total vectors matches Stage 8 canonical fixtures (238,837)
        self.assertEqual(len(vectors), 238837)

        # Artifact generation check
        artifact = generate_stage9_feature_dataset_artifact(vectors, "/tmp/stage9_test_artifact")
        self.assertEqual(artifact["feature_dataset_version"], STAGE9_FEATURE_DATASET_VERSION_LABEL)


if __name__ == "__main__":
    unittest.main()
