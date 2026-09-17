import os
import sys
import unittest
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.ml.app.data.pipeline import HistoricalIngestionPipeline  # noqa: E402
from services.ml.app.db.models import (  # noqa: E402
    Base,
    DatasetVersionModel,
    IngestionRunModel,
    MatchModel,
    MatchStatisticModel,
    ProvenanceRecordModel,
    RawSourcePayloadModel,
)


class TestStage6HistoricalData(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.pipeline = HistoricalIngestionPipeline(self.session)

        # Seed sample ingestion run
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
        self.pipeline.run_historical_ingestion(
            competitions=["EPL"], seasons=["2024/2025"]
        )

    def tearDown(self):
        self.session.close()

    def test_required_stage6_documentation_exists(self):
        required_docs = [
            "HISTORICAL_DATA_ACQUISITION.md",
            "DATA_INGESTION_PIPELINE.md",
            "DATASET_VERSIONING.md",
            "DATA_QUALITY_REPORT.md",
            "ENTITY_MAPPING_STAGE6.md",
            "DATA_ACQUISITION_RUNBOOK.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 6 documentation file '{filename}' must exist in docs/",
            )

    def test_database_populated_with_real_data_pipeline(self):
        match_count = self.session.query(MatchModel).count()
        stat_count = self.session.query(MatchStatisticModel).count()
        raw_count = self.session.query(RawSourcePayloadModel).count()
        prov_count = self.session.query(ProvenanceRecordModel).count()
        runs_count = self.session.query(IngestionRunModel).count()
        version_count = self.session.query(DatasetVersionModel).count()

        self.assertGreaterEqual(match_count, 1)
        self.assertGreaterEqual(stat_count, 12)
        self.assertGreaterEqual(raw_count, 1)
        self.assertGreaterEqual(prov_count, 1)
        self.assertGreaterEqual(runs_count, 1)
        self.assertGreaterEqual(version_count, 1)

    def test_no_future_feature_engineering_or_ml_models_in_stage6(self):
        """
        Guard test: Verify Stage 6 does NOT implement feature extraction or forecasting models.
        """
        pipeline_file = os.path.abspath(
            os.path.join(ROOT_DIR, "services/ml/app/data/pipeline.py")
        )
        with open(pipeline_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertNotIn("calculate_feature_vector", content)
            self.assertNotIn("run_model_inference", content)


if __name__ == "__main__":
    unittest.main()
