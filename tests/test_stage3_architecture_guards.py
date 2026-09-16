import os
import sys
import unittest

from fastapi.testclient import TestClient

# Path setup
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
contracts_dir = os.path.join(ROOT_DIR, "packages/contracts/python")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if contracts_dir not in sys.path:
    sys.path.insert(0, contracts_dir)

import football_contracts as contracts  # noqa: E402

from services.ml.app.main import app  # noqa: E402


class TestStage3ArchitectureGuards(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_no_fake_football_fixtures_in_source_code(self):
        """
        Guard test: Ensure no fake clubs, fake probabilities, or fake match predictions
        are introduced into the codebase.
        """
        forbidden_terms = [
            "Real Madrid 3 - 0 Barcelona",
            "Manchester United vs Liverpool prediction: 2-1",
            "win_probability = 0.85",
            "fake_match_id",
            "fabricated_xg",
        ]

        this_file = os.path.abspath(__file__)

        for root, dirs, files in os.walk(ROOT_DIR):
            if any(
                p in root
                for p in [".git", "node_modules", ".next", "__pycache__", "dist"]
            ):
                continue
            for file in files:
                if file.endswith((".py", ".ts", ".tsx", ".js", ".json", ".md")):
                    filepath = os.path.abspath(os.path.join(root, file))
                    if filepath == this_file:
                        continue
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for term in forbidden_terms:
                            self.assertNotIn(
                                term,
                                content,
                                f"Forbidden fake football term '{term}' found in {filepath}",
                            )

    def test_first_class_no_bet_contract_support(self):
        """
        Guard test: Verify that PredictionStatus enum explicitly contains NO_BET.
        """
        self.assertEqual(contracts.PredictionStatus.NO_BET.value, "NO_BET")
        self.assertEqual(
            contracts.PredictionStatus.INSUFFICIENT_EVIDENCE.value,
            "INSUFFICIENT_EVIDENCE",
        )

    def test_not_implemented_error_code(self):
        """
        Guard test: Verify ErrorCode enum contains NOT_IMPLEMENTED for Stage 4+ boundaries.
        """
        self.assertEqual(contracts.ErrorCode.NOT_IMPLEMENTED.value, "NOT_IMPLEMENTED")

    def test_fastapi_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "HEALTHY")

    def test_fastapi_readiness_endpoint(self):
        response = self.client.get("/readiness")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "READY")

    def test_database_and_jobs_boundaries(self):
        from infrastructure.database.connection import db_boundary
        from infrastructure.jobs.tasks import job_boundary

        db_status = db_boundary.check_connection()
        self.assertEqual(db_status["status"], "CONFIGURED")
        self.assertEqual(db_status["schema_state"], "NOT_IMPLEMENTED_STAGE3_BOUNDARY")

        job_status = job_boundary.check_worker_status()
        self.assertEqual(job_status["status"], "BOUNDARY_READY")

        dispatch_res = job_boundary.dispatch_job("test_ingestion", {})
        self.assertEqual(dispatch_res["status"], "NOT_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
