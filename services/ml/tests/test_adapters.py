import os
import sys
import unittest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.ml.app.data.adapters.football_data_uk import (  # noqa: E402
    FootballDataUKAdapter,
)
from services.ml.app.data.adapters.openfootball_reference import (  # noqa: E402
    OpenFootballReferenceAdapter,
)


class TestAdapters(unittest.TestCase):
    def test_football_data_uk_url_building(self):
        adapter = FootballDataUKAdapter()
        url = adapter.build_csv_url("2425", "E0")
        self.assertEqual(url, "https://www.football-data.co.uk/mmz4281/2425/E0.csv")

    def test_football_data_uk_csv_parsing(self):
        adapter = FootballDataUKAdapter()
        sample_csv = (
            "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST,HC,AC,HF,AF,HY,AY,HR,AR\n"
            "E0,18/08/2024,Arsenal,Wolverhampton,2,0,H,18,3,6,2,8,2,9,11,1,2,0,0\n"
            "E0,18/08/2024,Chelsea,Man City,0,2,A,10,11,3,5,4,6,12,8,2,2,0,0\n"
        )
        records = adapter.parse_csv_content(sample_csv)
        self.assertEqual(len(records), 2)

        match1 = records[0]
        self.assertEqual(match1["home_team"], "Arsenal")
        self.assertEqual(match1["away_team"], "Wolverhampton")
        self.assertEqual(match1["home_score"], 2)
        self.assertEqual(match1["away_score"], 0)
        self.assertEqual(match1["stats"]["home_shots"], 18.0)
        self.assertEqual(match1["stats"]["home_shots_on_target"], 6.0)

    def test_base_adapter_raw_payload_and_provenance(self):
        adapter = FootballDataUKAdapter()
        raw = adapter.create_raw_payload_entry(
            source_id="src-123",
            entity_type="MATCH_BATCH",
            external_identifier="E0-2425",
            raw_payload_json="{}",
            ingestion_run_id="run-456",
        )
        self.assertEqual(raw["source_id"], "src-123")
        self.assertEqual(raw["external_identifier"], "E0-2425")

        prov = adapter.create_provenance_entry(
            entity_type="MATCH",
            entity_id="match-789",
            source_id="src-123",
            source_url="https://example.com/test.csv",
        )
        self.assertEqual(prov["entity_id"], "match-789")
        self.assertEqual(prov["validation_state"], "VERIFIED")

    def test_openfootball_reference_adapter(self):
        adapter = OpenFootballReferenceAdapter()
        refs = adapter.load_reference_clubs()
        self.assertGreater(len(refs), 0)
        self.assertEqual(refs[0]["canonical_name"], "Arsenal FC")


if __name__ == "__main__":
    unittest.main()
