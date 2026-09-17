import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.ml.app.data.stage7.ingestion import (
    ELO_EXPECTED_SHA256,
    MATCHES_EXPECTED_SHA256,
    SourceProvenance,
)
from services.ml.app.data.stage7.pipeline import (
    Stage7CleaningPipelineEngine,
    derive_canonical_season,
    normalize_team_string,
    parse_canonical_date,
    parse_canonical_time,
)


class TestStage7Cleaning(unittest.TestCase):
    def setUp(self):
        self.engine = Stage7CleaningPipelineEngine()

    def test_required_stage7_documentation_exists(self):
        required_docs = [
            "STAGE7_CLEANING_SPECIFICATION.md",
            "STAGE7_NORMALIZATION_RULES.md",
            "STAGE7_VALIDATION_RULES.md",
            "STAGE7_QUARANTINE_POLICY.md",
            "STAGE7_DATA_QUALITY_REPORT.md",
            "STAGE7_DATASET_VERSION.md",
            "STAGE7_TRANSFORMATION_LINEAGE.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 7 documentation file '{filename}' must exist in docs/",
            )

    def test_team_string_normalization(self):
        self.assertEqual(normalize_team_string("  Arsenal FC  "), "arsenal fc")
        self.assertEqual(normalize_team_string("Real   Madrid"), "real madrid")

    def test_date_and_time_normalization(self):
        parsed_d, err_d = parse_canonical_date("18/08/2024")
        self.assertIsNone(err_d)
        self.assertEqual(parsed_d, "2024-08-18")

        season = derive_canonical_season("2024-08-18")
        self.assertEqual(season, "2024/25")

        parsed_t, err_t = parse_canonical_time("15:00")
        self.assertIsNone(err_t)
        self.assertEqual(parsed_t, "15:00:00")

    def test_single_match_row_cleaning_and_field_isolation(self):
        raw_row = {
            "Division": "E0",
            "MatchDate": "18/08/2024",
            "MatchTime": "15:00",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Wolves",
            "FTHome": "2",
            "FTAway": "0",
            "FTResult": "H",
            "HomeShots": "15",
            "HomeTarget": "6",
            "OddHome": "1.45",
            "Form3Home": "9",
            "ExpectedGoalsHome": "1.85",
            "ClusterLabel": "2",
        }
        prov = SourceProvenance(source_file="Matches.csv", source_row_index=1, source_sha256=MATCHES_EXPECTED_SHA256)
        rec = self.engine.clean_single_match_row(1, raw_row, prov)

        self.assertEqual(rec.record_status, "ACCEPTED")
        self.assertEqual(rec.canonical_data["full_time_home_goals"], 2)
        self.assertEqual(rec.canonical_data["full_time_result"], "H")

        # Isolated fields check
        self.assertTrue(rec.field_states["source_odd_home"].startswith("REJECTED_ODDS"))
        self.assertTrue(rec.field_states["source_form3_home"].startswith("REQUIRES_RECALCULATION"))
        self.assertTrue(rec.field_states["source_expected_goals_home"].startswith("REJECTED_UNVERIFIED"))
        self.assertTrue(rec.field_states["source_cluster_label"].startswith("REJECTED_LEAKAGE"))

    def test_shots_on_target_exceeding_total_shots_quarantined(self):
        raw_row = {
            "Division": "E0",
            "MatchDate": "2024-08-18",
            "HomeTeam": "Arsenal",
            "AwayTeam": "Wolves",
            "FTHome": "2",
            "FTAway": "0",
            "FTResult": "H",
            "HomeShots": "3",
            "HomeTarget": "8",  # Invalid!
        }
        prov = SourceProvenance(source_file="Matches.csv", source_row_index=1, source_sha256=MATCHES_EXPECTED_SHA256)
        rec = self.engine.clean_single_match_row(1, raw_row, prov)
        self.assertEqual(rec.record_status, "QUARANTINED")
        self.assertTrue(any(i.rule == "HOME_SHOTS_ON_TARGET_EXCEEDS_SHOTS" for i in rec.validation_issues))

    def test_elo_provisional_classification(self):
        prov = SourceProvenance(source_file="EloRatings.csv", source_row_index=1, source_sha256=ELO_EXPECTED_SHA256)

        # Pre-June 2025 -> VERIFIED_HISTORICAL_ELO
        raw_hist = {"date": "2024-05-01", "club": "Arsenal", "country": "ENG", "elo": "1950.5"}
        rec_hist = self.engine.clean_single_elo_row(1, raw_hist, prov)
        self.assertEqual(rec_hist.classification, "VERIFIED_HISTORICAL_ELO")

        # Post-June 2025 -> PROVISIONAL_ESTIMATE
        raw_prov = {"date": "2025-09-01", "club": "Arsenal", "country": "ENG", "elo": "1960.0"}
        rec_prov = self.engine.clean_single_elo_row(2, raw_prov, prov)
        self.assertEqual(rec_prov.classification, "PROVISIONAL_ESTIMATE")

    def test_no_stage8_or_ml_prohibitions_violated(self):
        """
        Guard test: Ensure Stage 7 does NOT perform Stage 8 entity resolution or ML training.
        """
        import services.ml.app.data.stage7.pipeline as pipeline_mod
        with open(pipeline_mod.__file__, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertNotIn("canonical_club_id", code)
            self.assertNotIn("train_model", code)
            self.assertNotIn("predict", code)


if __name__ == "__main__":
    unittest.main()
