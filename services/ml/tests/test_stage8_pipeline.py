import unittest

from services.ml.app.data.stage8.pipeline import Stage8EntityResolutionPipelineEngine
from services.ml.app.data.stage8.versioning import (
    STAGE8_ENTITY_MAPPING_VERSION_LABEL,
    generate_stage8_entity_mapping_artifact,
)


class TestStage8Pipeline(unittest.TestCase):
    def setUp(self):
        self.engine = Stage8EntityResolutionPipelineEngine()

    def test_full_entity_resolution_pipeline_execution(self):
        summary = self.engine.process_full_entity_resolution()

        # Check Club resolution
        self.assertEqual(summary["clubs"]["canonical_clubs_created"], 1221)
        self.assertEqual(summary["clubs"]["review_queue_count"], 0)

        # Check Competition & Season resolution
        self.assertEqual(summary["competitions"]["canonical_competitions_created"], 38)
        self.assertEqual(summary["seasons"]["canonical_seasons_created"], 789)

        # Check Fixture resolution
        self.assertEqual(summary["fixtures"]["total_stage7_matches_processed"], 238837)
        self.assertEqual(summary["fixtures"]["canonical_fixtures_created"], 238837)
        self.assertEqual(summary["fixtures"]["stage6_baseline_reconciled"], 39)

        # Check Player status
        self.assertEqual(summary["players"]["player_entity_resolution_status"], "UNAVAILABLE")

        # Artifact generation check
        artifact = generate_stage8_entity_mapping_artifact(summary, "/tmp/stage8_test_artifact")
        self.assertEqual(artifact["entity_mapping_version"], STAGE8_ENTITY_MAPPING_VERSION_LABEL)


if __name__ == "__main__":
    unittest.main()
