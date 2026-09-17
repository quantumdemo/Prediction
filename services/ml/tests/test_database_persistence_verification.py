import os
import sys
import unittest
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.ml.app.data.pipeline import HistoricalIngestionPipeline  # noqa: E402
from services.ml.app.db.models import (  # noqa: E402
    Base,
    ClubModel,
    MatchModel,
    MatchStatisticModel,
    ProvenanceRecordModel,
    RawSourcePayloadModel,
)


class TestDatabasePersistenceVerification(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.pipeline = HistoricalIngestionPipeline(self.session)

        # Populate sample data for persistence verification
        sample_csv = (
            "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST,HC,AC,HF,AF,HY,AY,HR,AR\n"
            "E0,18/08/2024,Arsenal,Wolverhampton,2,0,H,18,3,6,2,8,2,9,11,1,2,0,0\n"
            "E0,18/08/2024,Chelsea,Man City,0,2,A,10,11,3,5,4,6,12,8,2,2,0,0\n"
        )
        self.pipeline.fd_adapter.fetch_season_league_data = MagicMock(
            return_value=(
                True,
                "OK",
                self.pipeline.fd_adapter.parse_csv_content(sample_csv),
                "https://example.com/E0.csv",
            )
        )
        self.pipeline.run_historical_ingestion(
            competitions=["EPL"], seasons=["2024/2025"]
        )

    def tearDown(self):
        self.session.close()

    def test_database_records_exist_and_match(self):
        match_count = self.session.query(MatchModel).count()
        club_count = self.session.query(ClubModel).count()
        stat_count = self.session.query(MatchStatisticModel).count()
        raw_count = self.session.query(RawSourcePayloadModel).count()
        prov_count = self.session.query(ProvenanceRecordModel).count()

        self.assertEqual(match_count, 2)
        self.assertGreaterEqual(club_count, 4)
        self.assertEqual(stat_count, 24)
        self.assertGreaterEqual(raw_count, 1)
        self.assertGreaterEqual(prov_count, 1)

        # Check raw payload JSON preservation
        sample_raw = self.session.query(RawSourcePayloadModel).first()
        self.assertIsNotNone(sample_raw.raw_payload_json)
        self.assertIn("url", sample_raw.raw_payload_json)


if __name__ == "__main__":
    unittest.main()
