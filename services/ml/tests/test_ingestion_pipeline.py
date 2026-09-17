import os
import sys
import unittest
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.ml.app.data.pipeline import (  # noqa: E402
    HistoricalIngestionPipeline,
)
from services.ml.app.db.models import (  # noqa: E402
    Base,
    ClubSeasonMembershipModel,
    DatasetVersionModel,
    IngestionRunModel,
    MatchModel,
    ProvenanceRecordModel,
    RawSourcePayloadModel,
)


class TestIngestionPipeline(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.pipeline = HistoricalIngestionPipeline(self.session)

    def tearDown(self):
        self.session.close()

    def test_sources_and_reference_entities_registration(self):
        source_map = self.pipeline.ensure_sources_registered()
        self.assertIn("FOOTBALL_DATA_UK", source_map)
        self.assertIn("OPENFOOTBALL", source_map)

        country_map, comp_map, season_map = (
            self.pipeline.ensure_reference_entities(source_map)
        )
        self.assertIn("ENG", country_map)
        self.assertIn("EPL", comp_map)
        self.assertIn(("EPL", "2024/2025"), season_map)

    def test_pipeline_idempotency_and_persistence(self):
        sample_csv = (
            "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST,HC,AC,HF,AF,HY,AY,HR,AR\n"
            "E0,18/08/2024,Arsenal,Wolverhampton,2,0,H,18,3,6,2,8,2,9,11,1,2,0,0\n"
        )

        self.pipeline.fd_adapter.fetch_season_league_data = MagicMock(
            return_value=(
                True,
                "OK",
                self.pipeline.fd_adapter.parse_csv_content(sample_csv),
                "https://example.com/E0.csv",
            )
        )

        # First ingestion run
        run_id_1, summary1 = self.pipeline.run_historical_ingestion(
            competitions=["EPL"], seasons=["2024/2025"]
        )
        self.assertEqual(summary1["total_accepted"], 1)
        self.assertEqual(summary1["total_duplicates"], 0)

        # Check DB records
        matches = self.session.query(MatchModel).all()
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 0)

        memberships = self.session.query(ClubSeasonMembershipModel).all()
        self.assertEqual(len(memberships), 2)  # Home & away club memberships

        raw_payloads = self.session.query(RawSourcePayloadModel).all()
        self.assertGreater(len(raw_payloads), 0)

        provenance = self.session.query(ProvenanceRecordModel).all()
        self.assertGreater(len(provenance), 0)

        runs = self.session.query(IngestionRunModel).all()
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0].status, "COMPLETED")

        datasets = self.session.query(DatasetVersionModel).all()
        self.assertEqual(len(datasets), 1)

        # Second ingestion run on same data (must be idempotent)
        run_id_2, summary2 = self.pipeline.run_historical_ingestion(
            competitions=["EPL"], seasons=["2024/2025"]
        )
        self.assertEqual(summary2["total_accepted"], 0)
        self.assertEqual(summary2["total_duplicates"], 1)

        # Total matches count in DB remains 1
        matches_after = self.session.query(MatchModel).all()
        self.assertEqual(len(matches_after), 1)

        # Membership count remains 2
        memberships_after = self.session.query(ClubSeasonMembershipModel).all()
        self.assertEqual(len(memberships_after), 2)


if __name__ == "__main__":
    unittest.main()
