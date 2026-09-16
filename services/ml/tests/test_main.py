import os
import sys
import unittest

from fastapi.testclient import TestClient

# Ensure root & packages path in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
contracts_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../packages/contracts/python")
)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if contracts_dir not in sys.path:
    sys.path.insert(0, contracts_dir)

from services.ml.app.main import app  # noqa: E402


class TestFastAPIService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "HEALTHY")
        self.assertEqual(data["data"]["service"], "ml-service")
        self.assertIn("correlation_id", data)

    def test_health_v1_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "HEALTHY")

    def test_readiness_endpoint(self):
        response = self.client.get("/readiness")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "READY")

    def test_correlation_id_propagation(self):
        custom_id = "test-corr-1234"
        response = self.client.get("/health", headers={"x-correlation-id": custom_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-correlation-id"), custom_id)
        data = response.json()
        self.assertEqual(data["correlation_id"], custom_id)

    def test_not_implemented_boundaries(self):
        from services.ml.app.data import process_raw_match_data
        from services.ml.app.errors import PlatformException
        from services.ml.app.features import calculate_feature_vector
        from services.ml.app.models import run_model_inference

        with self.assertRaises(PlatformException) as cm:
            process_raw_match_data()
        self.assertEqual(cm.exception.code.value, "NOT_IMPLEMENTED")

        with self.assertRaises(PlatformException) as cm:
            calculate_feature_vector()
        self.assertEqual(cm.exception.code.value, "NOT_IMPLEMENTED")

        with self.assertRaises(PlatformException) as cm:
            run_model_inference()
        self.assertEqual(cm.exception.code.value, "NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
