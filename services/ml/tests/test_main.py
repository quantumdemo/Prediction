import unittest
from fastapi.testclient import TestClient

from services.ml.app.main import app

class TestMainAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

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
