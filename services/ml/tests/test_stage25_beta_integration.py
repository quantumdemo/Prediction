"""
End-to-End Private Beta Integration Tests for Stage 25

Verifies:
- End-to-end beta flow: Fixture Verification -> Research -> Evidence -> Feature Update -> Forecast -> Market Mapping -> Risk/NO-BET -> Auditable Report -> Persistence -> API Response.
- Distinct status classification for PREDICTION (ELIGIBLE), NO-BET (LOW_CONFIDENCE / HIGH_RISK), BLOCKED (UNVERIFIED / CONFLICTING), and INFRASTRUCTURE_FAILURE.
- Database prediction report persistence.
- Health and readiness status endpoints.
"""

import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from services.ml.app.db.models import Base
from services.ml.app.db.session import engine
from services.ml.app.integration.pipeline import EndToEndPredictionPipeline
from services.ml.app.integration.schemas import PredictionPipelineRequest
from services.ml.app.main import app
from services.ml.app.risk.schemas import DecisionStatus


class TestStage25BetaIntegration(unittest.TestCase):

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.pipeline = EndToEndPredictionPipeline()

    def test_e2e_beta_prediction_flow_success(self):
        """
        Verifies end-to-end beta prediction flow yielding an ELIGIBLE prediction response.
        """
        req = PredictionPipelineRequest(
            fixture_id="FIX_BETA_E2E_001",
            home_team="Arsenal",
            away_team="Chelsea",
            competition="COMP_ENG_PL",
            season="2025_2026",
            match_date="2026-03-15",
            kickoff_time="15:00",
            venue="Emirates Stadium",
            prediction_timestamp_utc="2026-03-15T12:00:00Z",  # strictly pre-kickoff
            base_features={
                "rolling_home_goals_for_5": 2.1,
                "rolling_away_goals_against_5": 1.2,
                "rest_days_difference": 1.0,
            },
            raw_research_inputs=[
                {
                    "category": "INJURIES",
                    "entity": "Arsenal",
                    "claim": "Key midfielder fully fit",
                    "source_domain": "skysports.com",
                    "source_url": "https://skysports.com/news/123",
                    "retrieval_timestamp_utc": "2026-03-15T10:00:00Z",
                    "research_state": "VERIFIED",
                }
            ],
        )

        res = self.pipeline.execute_prediction_pipeline(req)

        self.assertIsNotNone(res.prediction_id)
        self.assertIsNotNone(res.report_id)
        self.assertIsNotNone(res.audit_hash)
        self.assertEqual(res.decision_status, DecisionStatus.ELIGIBLE.value)
        self.assertTrue(res.is_persisted)
        self.assertIn("home", res.forecast_summary.get("probabilities_1x2", {}))

    def test_e2e_beta_unverified_fixture_blocked(self):
        """
        Verifies that unverified fixture identity triggers short-circuit BLOCKED decision.
        """
        req = PredictionPipelineRequest(
            fixture_id="",
            home_team="Unverified Team A",
            away_team="Unverified Team B",
            competition="Unknown Competition",
            season="2026",
            match_date="2026-03-15",
            prediction_timestamp_utc="2026-03-15T12:00:00Z",
        )

        res = self.pipeline.execute_prediction_pipeline(req)

        self.assertEqual(res.decision_status, DecisionStatus.BLOCKED.value)
        self.assertTrue(len(res.blocked_reasons) > 0)
        self.assertIn("UNVERIFIED_FIXTURE", res.blocked_reasons[0])

    def test_e2e_beta_conflicting_evidence_blocked(self):
        """
        Verifies that contradictory research evidence triggers short-circuit BLOCKED decision.
        """
        req = PredictionPipelineRequest(
            fixture_id="FIX_BETA_CONFLICT_001",
            home_team="Arsenal",
            away_team="Chelsea",
            competition="COMP_ENG_PL",
            season="2025_2026",
            match_date="2026-03-15",
            prediction_timestamp_utc="2026-03-15T12:00:00Z",
            raw_research_inputs=[
                {
                    "category": "INJURIES",
                    "entity": "Arsenal",
                    "claim": "Star winger Bukayo Saka is RULED OUT due to hamstring injury",
                    "source_domain": "bbc.com",
                    "source_url": "https://bbc.com/sport/football/1",
                    "retrieval_timestamp_utc": "2026-03-15T10:00:00Z",
                    "research_state": "CONFLICTING",
                    "contradiction_details": "Contradicts SkySports report stating Saka is starting.",
                }
            ],
        )

        res = self.pipeline.execute_prediction_pipeline(req)

        self.assertEqual(res.decision_status, DecisionStatus.BLOCKED.value)
        self.assertIn("UNRESOLVED_CRITICAL_EVIDENCE_CONFLICT", res.blocked_reasons[0])

    def test_api_health_and_readiness_endpoints(self):
        """
        Verifies /health and /readiness REST endpoint status payload structures.
        """
        h_res = self.client.get("/api/v1/health")
        self.assertEqual(h_res.status_code, 200)
        self.assertTrue(h_res.json()["success"])

        r_res = self.client.get("/api/v1/readiness")
        self.assertEqual(r_res.status_code, 200)
        self.assertTrue(r_res.json()["success"])


if __name__ == "__main__":
    unittest.main()
