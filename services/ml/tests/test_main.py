import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from services.ml.app.main import app
from services.ml.app.db.session import normalize_database_url

class TestMainAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_database_url_normalization_psycopg3(self):
        # Verify postgresql:// and postgres:// are normalized to postgresql+psycopg:// (psycopg3)
        raw_postgres = "postgresql://user:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"
        normalized = normalize_database_url(raw_postgres)
        self.assertEqual(normalized, "postgresql+psycopg://user:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require")

        raw_legacy = "postgres://user:password@host:5432/db"
        normalized_legacy = normalize_database_url(raw_legacy)
        self.assertEqual(normalized_legacy, "postgresql+psycopg://user:password@host:5432/db")

        # Verify sqlite and pre-dialect URLs remain unchanged
        sqlite_url = "sqlite:///:memory:"
        self.assertEqual(normalize_database_url(sqlite_url), "sqlite:///:memory:")

    def test_sqlalchemy_engine_dialect_resolution(self):
        # Regression test: Verify create_engine resolves psycopg (psycopg3) driver and cannot select psycopg2
        raw_postgres = "postgresql://user:password@host:5432/football_ai_db"
        normalized_url = normalize_database_url(raw_postgres)
        engine = create_engine(normalized_url)

        self.assertEqual(engine.dialect.name, "postgresql")
        self.assertEqual(engine.dialect.driver, "psycopg")

    def test_create_engine_fails_without_psycopg_driver(self):
        # Regression test: Verify create_engine FAILS with ModuleNotFoundError for psycopg2 when given raw postgresql:// without +psycopg
        raw_unnormalized_postgres = "postgresql://user:password@host:5432/football_ai_db"
        with self.assertRaises((ModuleNotFoundError, Exception)) as ctx:
            create_engine(raw_unnormalized_postgres)
        self.assertIn("psycopg2", str(ctx.exception))

    def test_exact_production_style_environment_value(self):
        # Regression test: Verify exact production environment string normalization and dialect resolution
        prod_env_value = "postgresql://<user>:<password>@<host>:5432/<database>"
        normalized_url = normalize_database_url(prod_env_value)
        self.assertTrue(normalized_url.startswith("postgresql+psycopg://"))

        engine = create_engine(normalized_url)
        self.assertEqual(engine.dialect.name, "postgresql")
        self.assertEqual(engine.dialect.driver, "psycopg")

    def test_session_engine_uses_normalized_url(self):
        from services.ml.app.db.session import RAW_DATABASE_URL, DATABASE_URL, engine
        self.assertEqual(DATABASE_URL, normalize_database_url(RAW_DATABASE_URL))
        self.assertTrue(DATABASE_URL.startswith("postgresql+psycopg://") or DATABASE_URL.startswith("sqlite://"))

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("status", data["data"])

    def test_api_v1_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_readiness_endpoint(self):
        response = self.client.get("/readiness")
        self.assertIn(response.status_code, [200, 530, 503])
        data = response.json()
        self.assertIn("success", data)

    def test_predict_endpoint_valid_request(self):
        payload = {
            "fixture_id": "FIX_MAIN_TEST_001",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "competition": "COMP_ENG_PL",
            "season": "2025_2026",
            "match_date": "2026-03-15",
            "raw_research_inputs": [],
            "base_features": {}
        }
        response = self.client.post("/api/v1/predict", json=payload, headers={"x-correlation-id": "test-predict-corr-123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-correlation-id"), "test-predict-corr-123")
        data = response.json()
        self.assertIn("report_id", data)
        self.assertIn("audit_hash", data)
        self.assertIn("decision_status", data)
        self.assertIn(data["decision_status"], ["ELIGIBLE", "NO_BET", "LOW_CONFIDENCE", "HIGH_RISK", "INSUFFICIENT_EVIDENCE", "BLOCKED"])

    def test_predict_endpoint_invalid_request(self):
        # Missing required field 'home_team'
        payload = {
            "fixture_id": "FIX_INVALID_001",
            "away_team": "Chelsea",
        }
        response = self.client.post("/api/v1/predict", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_history_endpoint_empty_and_query(self):
        response = self.client.get("/api/v1/history?limit=10&offset=0", headers={"x-correlation-id": "test-history-corr-456"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-correlation-id"), "test-history-corr-456")
        data = response.json()
        self.assertIsInstance(data, list)

    def test_history_endpoint_filtering(self):
        response = self.client.get("/api/v1/history?status=ELIGIBLE&fixture_id=FIX_MAIN_TEST_001")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

if __name__ == "__main__":
    unittest.main()
