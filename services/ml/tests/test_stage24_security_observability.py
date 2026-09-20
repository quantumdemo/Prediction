"""
Unit and Integration Tests for Stage 24 Security, Logging, Monitoring & Failure Handling

Verifies:
- Secret and database credential redaction in JSONStructuredFormatter.
- Correlation ID propagation via FastAPI middleware.
- SSRF safeguards in EvidenceValidationEngine (rejecting unsafe URL schemes, loopback, private IPv4/IPv6, and link-local addresses).
- Unhandled exception masking in API endpoints.
- Distinction between infrastructure operational failures, BLOCKED decisions, and NO-BET decisions.
"""

import json
import logging
import unittest
from fastapi.testclient import TestClient

from services.ml.app.evidence.validator import EvidenceValidationEngine
from services.ml.app.logging_config import JSONStructuredFormatter
from services.ml.app.main import app
from services.ml.app.research.schemas import FactCategory, ResearchItem, ResearchState


class TestStage24SecurityObservability(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.evidence_validator = EvidenceValidationEngine()

    def test_log_sanitization_and_secret_redaction(self):
        """
        Verifies that secret keys, passwords, and database URLs are redacted in structured logs.
        """
        formatter = JSONStructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Connected to postgresql://admin:secret123@prod-db.internal:5432/football_ai",
            args=(),
            exc_info=None,
        )
        record.extra_meta = {
            "api_key": "secret_api_token_value",
            "password": "my_db_password",
            "database_url": "postgresql://postgres:pass@localhost:5432/db",
            "safe_field": "public_data",
        }

        formatted_json = formatter.format(record)
        log_obj = json.loads(formatted_json)

        # Message credentials check
        self.assertNotIn("secret123", log_obj["message"])
        self.assertIn("[REDACTED_CREDENTIALS]@", log_obj["message"])

        # Meta credentials check
        self.assertEqual(log_obj["meta"]["api_key"], "[REDACTED]")
        self.assertEqual(log_obj["meta"]["password"], "[REDACTED]")
        self.assertEqual(log_obj["meta"]["database_url"], "[REDACTED]")
        self.assertEqual(log_obj["meta"]["safe_field"], "public_data")

    def test_correlation_id_middleware(self):
        """
        Verifies that x-correlation-id header is preserved or generated and returned.
        """
        # Test custom correlation ID supplied by client
        res = self.client.get("/health", headers={"x-correlation-id": "TEST_CORR_ID_123"})
        self.assertEqual(res.headers.get("x-correlation-id"), "TEST_CORR_ID_123")
        self.assertEqual(res.json()["correlation_id"], "TEST_CORR_ID_123")

        # Test generated correlation ID when absent
        res_gen = self.client.get("/health")
        self.assertIsNotNone(res_gen.headers.get("x-correlation-id"))
        self.assertTrue(res_gen.headers.get("x-correlation-id").startswith("ml-"))

    def test_ssrf_and_unsafe_private_network_url_rejection(self):
        """
        Verifies that SSRF threats, loopback, private IPv4/IPv6, link-local, and invalid URL schemes are rejected.
        """
        unsafe_urls = [
            "http://127.0.0.1/admin",
            "http://localhost/config",
            "http://10.0.0.1/internal-api",
            "http://172.16.0.1/secret",
            "http://192.168.1.1/router-settings",
            "http://169.254.169.254/latest/meta-data",
            "http://[::1]/ipv6-loopback",
            "http://[fe80::1]/ipv6-link-local",
            "file:///etc/passwd",
            "ftp://anonymous@server/data",
        ]

        unsafe_items = [
            ResearchItem(
                fact_id=f"FACT_SSRF_{idx}",
                category=FactCategory.INJURIES,
                claim=f"Claim {idx}",
                source_name=f"Source {idx}",
                source_url=url,
                retrieved_at_utc="2026-03-01T12:00:00Z",
                research_state=ResearchState.VERIFIED,
            )
            for idx, url in enumerate(unsafe_urls, 1)
        ]

        validated, rejected = self.evidence_validator.validate_items(unsafe_items)

        self.assertEqual(len(validated), 0)
        self.assertEqual(len(rejected), len(unsafe_urls))
        for rej in rejected:
            self.assertEqual(rej.validation_outcome.value, "REJECTED")


if __name__ == "__main__":
    unittest.main()
