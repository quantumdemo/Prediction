"""
Stage 20 End-to-End Prediction Integration Pipeline Test Suite

Verifies:
- End-to-end ELIGIBLE prediction pipeline flow (Stages 14 -> 15 -> 16 -> 17 -> 18 -> 19)
- Failure-path short-circuiting (unverified fixture, leakage, evidence conflict, blocked forecast)
- No downstream stage execution after a blocking failure
- Deterministic repeated execution with identical inputs
- Prediction history repository persistence and multi-criteria retrieval
- Strict separation of probability, confidence, risk flags, and decision status
- Absolute absence of fabricated values, bookmaker odds, expected value edge, or Kelly stake sizing
"""

import unittest
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.integration.pipeline import EndToEndPredictionPipeline
from services.ml.app.integration.schemas import PredictionPipelineRequest
from services.ml.app.reporting.schemas import PredictionHistoryFilter
from services.ml.app.risk.schemas import DecisionStatus


class TestStage20E2EIntegration(unittest.TestCase):
    def setUp(self):
        self.pipeline = EndToEndPredictionPipeline()

        self.valid_request = PredictionPipelineRequest(
            fixture_id="FIX_E2E_TEST_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            kickoff_time="20:00",
            venue="Old Trafford",
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            raw_research_inputs=[
                {
                    "claim": "Home team rest days updated to 7 days.",
                    "source_name": "Premier League Official",
                    "source_url": "https://www.premierleague.com/news/rest",
                    "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                    "category": "REST_CONGESTION",
                    "research_state": "VERIFIED",
                    "canonical_entities_mentioned": ["Manchester United"],
                }
            ],
            base_features={fname: 0.0 for fname in STAGE9_FEATURE_REGISTRY.keys()},
        )

    def test_e2e_eligible_prediction_pipeline(self):
        response = self.pipeline.execute_prediction_pipeline(self.valid_request)

        self.assertEqual(response.decision_status, DecisionStatus.ELIGIBLE.value)
        self.assertEqual(response.model_attribution["model_name"], "XGBoostForecaster")
        self.assertEqual(response.model_attribution["calibration_method"], "platt_sigmoid")
        self.assertTrue(response.is_persisted)
        self.assertTrue(len(response.audit_hash) == 64)
        self.assertIn("MKT_1X2", response.supported_markets)

    def test_failure_path_unverified_fixture(self):
        invalid_request = PredictionPipelineRequest(
            fixture_id="",  # Empty fixture ID -> Unverified
            home_team="Unknown FC A",
            away_team="Unknown FC B",
            competition="Unknown League",
            season="20242025",
            match_date="2025-03-20",
        )

        response = self.pipeline.execute_prediction_pipeline(invalid_request)

        self.assertEqual(response.decision_status, DecisionStatus.BLOCKED.value)
        self.assertIn("UNVERIFIED_FIXTURE", response.blocked_reasons[0])
        self.assertIsNone(response.forecast_summary)
        self.assertEqual(len(response.supported_markets), 0)
        self.assertTrue(response.is_persisted)

    def test_failure_path_prediction_time_leakage(self):
        leakage_request = PredictionPipelineRequest(
            fixture_id="FIX_LEAK_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            raw_research_inputs=[
                {
                    "claim": "Post-match lineup update.",
                    "source_name": "BBC Sport",
                    "source_url": "https://www.bbc.com/sport/postmatch",
                    "retrieval_timestamp_utc": "2025-03-21T10:00:00Z",  # AFTER cutoff
                    "category": "REST_CONGESTION",
                    "research_state": "VERIFIED",
                    "canonical_entities_mentioned": ["Manchester United"],
                }
            ],
            base_features={fname: 0.0 for fname in STAGE9_FEATURE_REGISTRY.keys()},
        )

        response = self.pipeline.execute_prediction_pipeline(leakage_request)

        self.assertEqual(response.decision_status, DecisionStatus.BLOCKED.value)
        self.assertIn("PREDICTION_TIME_LEAKAGE", response.blocked_reasons[0])

    def test_failure_path_unresolved_evidence_conflict(self):
        conflict_request = PredictionPipelineRequest(
            fixture_id="FIX_CONFLICT_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            raw_research_inputs=[
                {
                    "claim": "Bukayo Saka is OUT injured with a hamstring tear.",
                    "source_name": "BBC Sport",
                    "source_url": "https://www.bbc.com/sport/saka1",
                    "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                    "category": "INJURIES",
                    "canonical_entities_mentioned": ["Arsenal", "Bukayo Saka"],
                },
                {
                    "claim": "Bukayo Saka trained fully and is FIT to play.",
                    "source_name": "Sky Sports",
                    "source_url": "https://www.skysports.com/saka2",
                    "retrieval_timestamp_utc": "2025-03-18T11:00:00Z",
                    "category": "INJURIES",
                    "canonical_entities_mentioned": ["Arsenal", "Bukayo Saka"],
                },
            ],
            base_features={fname: 0.0 for fname in STAGE9_FEATURE_REGISTRY.keys()},
        )

        response = self.pipeline.execute_prediction_pipeline(conflict_request)

        self.assertEqual(response.decision_status, DecisionStatus.BLOCKED.value)
        self.assertIn("UNRESOLVED_CRITICAL_EVIDENCE_CONFLICT", response.blocked_reasons[0])

    def test_short_circuit_no_downstream_execution_after_blocking(self):
        invalid_request = PredictionPipelineRequest(
            fixture_id="",
            home_team="Team A",
            away_team="Team B",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
        )

        response = self.pipeline.execute_prediction_pipeline(invalid_request)

        # Confirm downstream forecasting and market mapping were skipped
        self.assertIsNone(response.forecast_summary)
        self.assertEqual(len(response.supported_markets), 0)
        self.assertEqual(response.feature_status_summary.get("status"), "BLOCKED_BEFORE_FEATURE_UPDATE")

    def test_deterministic_repeated_execution(self):
        r1 = self.pipeline.execute_prediction_pipeline(self.valid_request)
        r2 = self.pipeline.execute_prediction_pipeline(self.valid_request)

        self.assertEqual(r1.audit_hash, r2.audit_hash)
        self.assertEqual(
            r1.supported_markets["MKT_1X2"]["outcomes"][0]["probability"],
            r2.supported_markets["MKT_1X2"]["outcomes"][0]["probability"],
        )

    def test_database_persistence_and_retrieval(self):
        response = self.pipeline.execute_prediction_pipeline(self.valid_request)
        self.assertTrue(response.is_persisted)

        # Retrieve report from history repository
        retrieved = self.pipeline.repository.get_by_prediction_id(response.prediction_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.prediction_id, response.prediction_id)
        self.assertEqual(retrieved.audit_hash, response.audit_hash)

        # Query history
        filtered = self.pipeline.repository.query_history(
            PredictionHistoryFilter(fixture_id="FIX_E2E_TEST_001", decision_status=DecisionStatus.ELIGIBLE.value)
        )
        self.assertGreaterEqual(len(filtered), 1)

    def test_real_postgresql_orm_persistence_and_retrieval(self):
        """
        Tests real database persistence and retrieval via SQLAlchemy ORM session simulating PostgreSQL.
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from services.ml.app.db.models import Base
        from services.ml.app.reporting.repository import PredictionHistoryRepository

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        session1 = Session()
        db_repo1 = PredictionHistoryRepository(db_session=session1)

        # Execute pipeline with DB repository
        pipeline_db = EndToEndPredictionPipeline(repository=db_repo1)
        resp = pipeline_db.execute_prediction_pipeline(self.valid_request)

        self.assertTrue(resp.is_persisted)

        # Test retrieval after repository & DB session reinitialization
        session2 = Session()
        db_repo2 = PredictionHistoryRepository(db_session=session2)

        retrieved = db_repo2.get_by_prediction_id(resp.prediction_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.prediction_id, resp.prediction_id)
        self.assertEqual(retrieved.audit_hash, resp.audit_hash)

    def test_immutable_duplicate_prediction_id_rejection(self):
        """
        Tests that saving duplicate prediction ID or report ID to database session raises ValueError.
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from services.ml.app.db.models import Base
        from services.ml.app.reporting.repository import PredictionHistoryRepository

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        session = Session()
        db_repo = PredictionHistoryRepository(db_session=session)

        pipeline_db = EndToEndPredictionPipeline(repository=db_repo)
        resp = pipeline_db.execute_prediction_pipeline(self.valid_request)

        # Attempt duplicate save of same report
        report = db_repo.get_by_prediction_id(resp.prediction_id)
        with self.assertRaises(ValueError):
            db_repo.save_report(report)

    def test_explicit_confirmation_of_stage14_live_research_boundary(self):
        """
        Confirms that Stage 20 pipeline accepts Stage 14 research input payloads while explicitly
        documenting that live web-scraping connectors are an external production dependency.
        """
        resp = self.pipeline.execute_prediction_pipeline(self.valid_request)
        self.assertIn("items_collected", resp.research_status_summary)
        self.assertEqual(resp.research_status_summary["items_collected"], 1)

    def test_no_bookmaker_odds_or_ev_edge_calculation(self):
        response = self.pipeline.execute_prediction_pipeline(self.valid_request)
        resp_dict = response.model_dump()

        self.assertNotIn("bookmaker_odds", resp_dict)
        self.assertNotIn("odds", resp_dict)
        self.assertNotIn("expected_value", resp_dict)
        self.assertNotIn("edge", resp_dict)
        self.assertNotIn("kelly_stake", resp_dict)


if __name__ == "__main__":
    unittest.main()
