import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.ml.app.data.stage8.club_resolver import ControlledClubResolver, is_non_senior_team
from services.ml.app.data.stage8.competition_season_resolver import CompetitionSeasonResolver
from services.ml.app.data.stage8.fixture_resolver import FixtureResolver
from services.ml.app.data.stage8.venue_player_resolver import VenuePlayerResolver


class TestStage8EntityResolution(unittest.TestCase):
    def setUp(self):
        self.club_resolver = ControlledClubResolver()
        self.comp_resolver = CompetitionSeasonResolver()
        self.fixture_resolver = FixtureResolver()
        self.vp_resolver = VenuePlayerResolver()

    def test_required_stage8_documentation_exists(self):
        required_docs = [
            "STAGE8_ENTITY_RESOLUTION_SPECIFICATION.md",
            "STAGE8_ENTITY_MAPPING_RULES.md",
            "STAGE8_CLUB_IDENTITY_REPORT.md",
            "STAGE8_COMPETITION_SEASON_REPORT.md",
            "STAGE8_FIXTURE_IDENTITY_REPORT.md",
            "STAGE8_UNRESOLVED_REVIEW_QUEUE.md",
            "STAGE8_PROVENANCE_AND_VERSIONING.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 8 documentation file '{filename}' must exist in docs/",
            )

    def test_multi_level_club_resolution(self):
        # Seed reference club with canonical name and distinct alias
        self.club_resolver.register_reference_club("Arsenal Football Club", "ENG", aliases=["Gunners"])

        # Level 1 Exact Match
        res1 = self.club_resolver.resolve_club_identity("Arsenal Football Club", "ENG")
        self.assertEqual(res1.status, "VERIFIED")
        self.assertEqual(res1.level, "LEVEL_1_EXACT_MATCH")

        # Level 2 Alias Match
        res2 = self.club_resolver.resolve_club_identity("Gunners", "ENG")
        self.assertEqual(res2.status, "VERIFIED")
        self.assertEqual(res2.level, "LEVEL_2_ALIAS_MATCH")

    def test_team_type_separation(self):
        is_non_sr, t_type = is_non_senior_team("Arsenal Women")
        self.assertTrue(is_non_sr)
        self.assertEqual(t_type, "WOMEN")

        is_non_sr_b, t_type_b = is_non_senior_team("Real Madrid B")
        self.assertTrue(is_non_sr_b)
        self.assertEqual(t_type_b, "RESERVE_B_TEAM")

    def test_player_resolution_unavailable_status(self):
        res = self.vp_resolver.get_player_resolution_status()
        self.assertEqual(res["player_entity_resolution_status"], "UNAVAILABLE")
        self.assertEqual(res["fabricated_player_records_count"], 0)

    def test_no_stage9_or_ml_prohibitions_violated(self):
        """
        Guard test: Ensure Stage 8 does NOT calculate Stage 9 features or train models.
        """
        import services.ml.app.data.stage8.pipeline as pipeline_mod
        with open(pipeline_mod.__file__, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertNotIn("calculate_form", code)
            self.assertNotIn("rolling_average", code)
            self.assertNotIn("train_model", code)
            self.assertNotIn("predict", code)


if __name__ == "__main__":
    unittest.main()
