import subprocess
import sys
import unittest
from fastapi.testclient import TestClient

from api.index import app


class TestVercelEntryPoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_vercel_entrypoint_app_import(self):
        self.assertIsNotNone(app)
        self.assertEqual(app.title, "Football AI Platform — Python ML Service")

    def test_vercel_bundle_no_heavy_ml_imports(self):
        """
        Guarantees that importing the Vercel API entry point in a fresh Python process does NOT pull
        heavyweight ML C++ binaries (xgboost, sklearn, scipy, nvidia-nccl-cu13) into sys.modules.
        This prevents the Vercel serverless function bundle from exceeding 500 MB.
        """
        cmd = [
            sys.executable,
            "-c",
            "import sys; import api.index; heavy = ['xgboost', 'sklearn', 'scipy', 'nvidia']; "
            "loaded = [m for m in heavy if m in sys.modules]; print(loaded)",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertIn("[]", res.stdout.strip())

    def test_health_endpoint_via_entrypoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_predict_endpoint_via_entrypoint(self):
        payload = {
            "fixture_id": "FIX_VERCEL_TEST_001",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "competition": "COMP_ENG_PL",
            "season": "2025_2026",
            "match_date": "2026-03-15",
            "raw_research_inputs": [],
            "base_features": {}
        }
        response = self.client.post("/api/v1/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("report_id", data)
        self.assertIn("audit_hash", data)

    def test_history_endpoint_via_entrypoint(self):
        response = self.client.get("/api/v1/history?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)


if __name__ == "__main__":
    unittest.main()
