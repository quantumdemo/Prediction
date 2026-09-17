import unittest

from services.ml.app.data.stage7.pipeline import Stage7CleaningPipelineEngine
from services.ml.app.data.stage7.versioning import (
    STAGE7_DATASET_VERSION_LABEL,
    generate_stage7_dataset_artifact,
)


class TestStage7Pipeline(unittest.TestCase):
    def setUp(self):
        self.engine = Stage7CleaningPipelineEngine()

    def test_full_candidate_dataset_pipeline_execution(self):
        summary = self.engine.process_full_candidate_dataset()

        # Check Matches statistics
        self.assertEqual(summary["matches"]["total_raw"], 238858)
        self.assertEqual(summary["matches"]["accepted_valid"], 238837)
        self.assertEqual(summary["matches"]["quarantined"], 21)
        self.assertEqual(summary["matches"]["duplicate_count"], 0)
        self.assertEqual(summary["matches"]["earliest_date"], "2000-07-28")
        self.assertEqual(summary["matches"]["latest_date"], "2026-09-03")

        # Check Elo statistics
        self.assertEqual(summary["elo"]["total_raw"], 273972)
        self.assertEqual(summary["elo"]["accepted"], 273972)
        self.assertEqual(summary["elo"]["verified_historical"], 245033)
        self.assertEqual(summary["elo"]["provisional_estimates"], 28939)

        # Artifact generation check
        artifact = generate_stage7_dataset_artifact(self.engine, "/tmp/stage7_test_artifact")
        self.assertEqual(artifact["dataset_version"], STAGE7_DATASET_VERSION_LABEL)


if __name__ == "__main__":
    unittest.main()
