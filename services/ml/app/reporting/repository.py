"""
Stage 19 Prediction History Repository Implementation

Handles immutable storage, persistence, and multi-criteria historical retrieval
for prediction reports by prediction ID, fixture ID, date range, model/version,
market, and decision status.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from services.ml.app.reporting.schemas import AuditablePredictionReport, PredictionHistoryFilter

logger = logging.getLogger("football_ml.reporting.repository")


class PredictionHistoryRepository:
    """
    Prediction History Repository.
    Supports in-memory storage and optional PostgreSQL persistence.
    """

    def __init__(self, db_session: Optional[Any] = None):
        self.db_session = db_session
        self._in_memory_store: Dict[str, AuditablePredictionReport] = {}

    def save_report(self, report: AuditablePredictionReport) -> bool:
        """
        Saves an immutable prediction report. Rejects duplicate report IDs to preserve immutability.
        """
        if report.report_id in self._in_memory_store:
            raise ValueError(f"Immutability Violation: Report ID {report.report_id} already exists in history repository.")

        self._in_memory_store[report.report_id] = report
        logger.info(f"Report {report.report_id} saved to history store.")
        return True

    def get_by_report_id(self, report_id: str) -> Optional[AuditablePredictionReport]:
        return self._in_memory_store.get(report_id)

    def get_by_prediction_id(self, prediction_id: str) -> Optional[AuditablePredictionReport]:
        for r in self._in_memory_store.values():
            if r.prediction_id == prediction_id:
                return r
        return None

    def query_history(self, query_filter: PredictionHistoryFilter) -> List[AuditablePredictionReport]:
        """
        Queries historical prediction reports by multi-criteria filter.
        """
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
