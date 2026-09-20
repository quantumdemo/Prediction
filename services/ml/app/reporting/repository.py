"""
Stage 19 & 20 Prediction History Repository Implementation

Handles immutable storage, PostgreSQL persistence via SQLAlchemy session, and multi-criteria
historical retrieval for prediction reports by prediction ID, fixture ID, date range,
model/version, market, and decision status.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.ml.app.db.models import PredictionReportModel
from services.ml.app.reporting.schemas import AuditablePredictionReport, PredictionHistoryFilter

logger = logging.getLogger("football_ml.reporting.repository")


class PredictionHistoryRepository:
    """
    Prediction History Repository supporting PostgreSQL ORM and in-memory persistence.
    """

    def __init__(self, db_session: Optional[Any] = None):
        self.db_session = db_session
        self._in_memory_store: Dict[str, AuditablePredictionReport] = {}

    def save_report(self, report: AuditablePredictionReport) -> bool:
        """
        Saves an immutable prediction report. Rejects duplicate prediction/report IDs to preserve immutability.
        """
        # In-memory check
        if report.report_id in self._in_memory_store:
            raise ValueError(f"Immutability Violation: Report ID {report.report_id} already exists in history repository.")

        for r in self._in_memory_store.values():
            if r.prediction_id == report.prediction_id:
                raise ValueError(f"Immutability Violation: Prediction ID {report.prediction_id} already exists in history repository.")

        # Database check and ORM persistence if session available
        if self.db_session is not None:
            existing_orm = (
                self.db_session.query(PredictionReportModel)
                .filter(
                    (PredictionReportModel.prediction_id == report.prediction_id)
                    | (PredictionReportModel.audit_hash == report.audit_hash)
                )
                .first()
            )
            if existing_orm:
                raise ValueError(f"Immutability Violation: Prediction ID {report.prediction_id} already exists in database.")

            pred_dt = self._parse_iso_dt(report.prediction_timestamp_utc)
            created_dt = self._parse_iso_dt(report.created_at_utc)

            orm_record = PredictionReportModel(
                prediction_id=report.prediction_id,
                fixture_id=report.fixture_id,
                prediction_timestamp_utc=pred_dt,
                model_name=report.model_name,
                model_version=report.model_version,
                calibration_method=report.calibration_method,
                decision_status=report.final_decision_status,
                report_payload_json=json.dumps(report.model_dump(), sort_keys=True),
                audit_hash=report.audit_hash,
                created_at_utc=created_dt,
            )
            self.db_session.add(orm_record)
            self.db_session.commit()
            logger.info(f"Report {report.report_id} persisted to database table 'prediction_reports'.")

        self._in_memory_store[report.report_id] = report
        logger.info(f"Report {report.report_id} saved to history store.")
        return True

    def get_by_report_id(self, report_id: str) -> Optional[AuditablePredictionReport]:
        if report_id in self._in_memory_store:
            return self._in_memory_store[report_id]

        if self.db_session is not None:
            orm_record = (
                self.db_session.query(PredictionReportModel)
                .filter(PredictionReportModel.id == report_id)
                .first()
            )
            if orm_record:
                return self._orm_to_schema(orm_record)

        return None

    def get_by_prediction_id(self, prediction_id: str) -> Optional[AuditablePredictionReport]:
        for r in self._in_memory_store.values():
            if r.prediction_id == prediction_id:
                return r

        if self.db_session is not None:
            orm_record = (
                self.db_session.query(PredictionReportModel)
                .filter(PredictionReportModel.prediction_id == prediction_id)
                .first()
            )
            if orm_record:
                return self._orm_to_schema(orm_record)

        return None

    def query_history(self, query_filter: PredictionHistoryFilter) -> List[AuditablePredictionReport]:
        """
        Queries historical prediction reports by multi-criteria filter across DB and memory.
        """
        if self.db_session is not None:
            query = self.db_session.query(PredictionReportModel)

            if query_filter.prediction_id:
                query = query.filter(PredictionReportModel.prediction_id == query_filter.prediction_id)
            if query_filter.fixture_id:
                query = query.filter(PredictionReportModel.fixture_id == query_filter.fixture_id)
            if query_filter.model_name:
                query = query.filter(PredictionReportModel.model_name == query_filter.model_name)
            if query_filter.model_version:
                query = query.filter(PredictionReportModel.model_version == query_filter.model_version)
            if query_filter.decision_status:
                query = query.filter(PredictionReportModel.decision_status == query_filter.decision_status)
            if query_filter.start_date:
                start_dt = self._parse_iso_dt(query_filter.start_date)
                query = query.filter(PredictionReportModel.prediction_timestamp_utc >= start_dt)
            if query_filter.end_date:
                end_dt = self._parse_iso_dt(query_filter.end_date)
                query = query.filter(PredictionReportModel.prediction_timestamp_utc <= end_dt)

            orm_records = query.order_by(PredictionReportModel.created_at_utc.desc()).limit(query_filter.limit).all()
            return [self._orm_to_schema(r) for r in orm_records]

        # In-memory query fallback
        results: List[AuditablePredictionReport] = []
        for r in self._in_memory_store.values():
            if query_filter.prediction_id and r.prediction_id != query_filter.prediction_id:
                continue
            if query_filter.fixture_id and r.fixture_id != query_filter.fixture_id:
                continue
            if query_filter.model_name and r.model_name != query_filter.model_name:
                continue
            if query_filter.model_version and r.model_version != query_filter.model_version:
                continue
            if query_filter.decision_status and r.final_decision_status != query_filter.decision_status:
                continue
            if query_filter.market_id and query_filter.market_id not in r.market_probabilities:
                continue
            if query_filter.start_date and r.prediction_timestamp_utc < query_filter.start_date:
                continue
            if query_filter.end_date and r.prediction_timestamp_utc > query_filter.end_date:
                continue

            results.append(r)
            if len(results) >= query_filter.limit:
                break

        return results

    @staticmethod
    def _orm_to_schema(orm_record: PredictionReportModel) -> AuditablePredictionReport:
        payload_dict = json.loads(orm_record.report_payload_json)
        return AuditablePredictionReport(**payload_dict)

    @staticmethod
    def _parse_iso_dt(ts_str: str) -> datetime:
        try:
            ts_clean = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(ts_clean)
        except Exception:
            return datetime.now()
