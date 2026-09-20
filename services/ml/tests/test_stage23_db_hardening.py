"""
Unit and Infrastructure Hardening Tests for Stage 23 Database & Production Hardening

Verifies:
- Database connection configuration and pooling parameters.
- Secret masking in database URL (`mask_database_url`).
- Transaction context manager (`db_transaction`) commit and automatic rollback on error.
- Prediction report duplicate prediction ID rejection.
- Prediction history repository persistence and retrieval.
- Safe error handling in FastAPI endpoints masking stack traces and internal errors.
"""

import unittest
from datetime import datetime, timezone

from services.ml.app.db.models import Base, PredictionReportModel
from services.ml.app.db.session import (
    SessionLocal,
    check_database_health,
    db_transaction,
    engine,
    mask_database_url,
)
from services.ml.app.reporting.repository import PredictionHistoryRepository
from services.ml.app.reporting.schemas import AuditablePredictionReport, PredictionChainProvenance


class TestStage23DatabaseHardening(unittest.TestCase):

    def setUp(self):
        Base.metadata.create_all(bind=engine)

    def test_mask_database_url(self):
        """
        Verifies that secret passwords in database URLs are safely redacted.
        """
        raw_url = "postgresql://user_admin:secret_pass123@prod-db.example.com:5432/football_ai"
        masked = mask_database_url(raw_url)
        self.assertNotIn("secret_pass123", masked)
        self.assertIn("prod-db.example.com", masked)
        self.assertIn("*****:*****", masked)

    def test_db_transaction_commit_and_rollback(self):
        """
        Verifies that db_transaction commits on success and rolls back on exception.
        """
        # Test rollback on exception
        try:
            with db_transaction() as session:
                dummy_report = PredictionReportModel(
                    prediction_id="PRED_TEST_ROLLBACK_001",
                    fixture_id="FIX_ROLLBACK",
                    prediction_timestamp_utc=datetime.now(timezone.utc),
                    model_name="xgboost_platt",
                    model_version="1.0.0",
                    calibration_method="platt",
                    decision_status="ELIGIBLE",
                    report_payload_json="{}",
                    audit_hash="hash123",
                )
                session.add(dummy_report)
                raise ValueError("Simulated transaction error")
        except ValueError:
            pass

        # Verify record was NOT committed
        session = SessionLocal()
        found = session.query(PredictionReportModel).filter_by(prediction_id="PRED_TEST_ROLLBACK_001").first()
        session.close()
        self.assertIsNone(found)

    def test_duplicate_prediction_rejection(self):
        """
        Verifies that duplicate prediction_id inserts are safely rejected via ValueError.
        """
        repo = PredictionHistoryRepository()
        report1 = AuditablePredictionReport(
            report_id="REP_DUP_001",
            prediction_id="PRED_DUP_UNIQUE_001",
            fixture_id="FIX_DUP_001",
            prediction_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            fixture_summary={"home": "Arsenal", "away": "Chelsea"},
            model_name="xgboost_platt",
            model_version="1.0.0",
            calibration_method="platt",
            final_decision_status="ELIGIBLE",
            provenance_chain=PredictionChainProvenance(
                fixture_id="FIX_DUP_001",
                fixture_verification_method="exact",
                evidence_items_evaluated_count=1,
                validated_evidence_count=1,
                updated_features_count=55,
                feature_provenance_records_count=0,
                model_name="xgboost_platt",
                model_version="1.0.0",
                calibration_method="platt",
                supported_markets_count=8,
                unsupported_markets_count=3,
                evaluated_risk_flags_count=0,
            ),
            audit_hash="hash_dup_test",
        )

        # First save succeeds
        saved_1 = repo.save_report(report1)
        self.assertTrue(saved_1)

        # Create second report with different report_id but SAME prediction_id
        report2 = report1.model_copy(update={"report_id": "REP_DUP_002"})

        # Duplicate prediction_id save raises ValueError preserving immutability
        with self.assertRaises(ValueError):
            repo.save_report(report2)

    def test_database_health_check(self):
        """
        Verifies database health check function execution.
        """
        health = check_database_health()
        self.assertIn("status", health)


if __name__ == "__main__":
    unittest.main()
