"""
Stage 19 Auditable Report Generator Implementation

Constructs complete, immutable, structured prediction reports for every prediction attempt
from Stage 16 forecast containers, Stage 17 market reports, and Stage 18 risk reports.
Calculates deterministic SHA256 audit hashes and preserves full provenance traces.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.ml.app.markets.schemas import MappedMarketReport
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer
from services.ml.app.reporting.schemas import AuditablePredictionReport, PredictionChainProvenance
from services.ml.app.risk.schemas import DecisionStatus, RiskEngineReport

logger = logging.getLogger("football_ml.reporting.generator")


class AuditableReportGenerator:
    """
    Deterministic Auditable Prediction Report Generator.
    """

    def generate_report(
        self,
        forecast_container: CurrentMatchForecastContainer,
        market_report: MappedMarketReport,
        risk_report: RiskEngineReport,
    ) -> AuditablePredictionReport:
        logger.info(f"Generating auditable prediction report for fixture {forecast_container.fixture.fixture_id}...")

        prediction_id = f"PRED_{forecast_container.fixture.fixture_id}_{uuid.uuid4().hex[:8]}"
        report_id = f"AUDIT_REP_{forecast_container.fixture.fixture_id}_{uuid.uuid4().hex[:6]}"

        # 1. Fixture Summary
        fixture_summary = {
            "fixture_id": forecast_container.fixture.fixture_id,
            "home_team": forecast_container.fixture.home_team,
            "away_team": forecast_container.fixture.away_team,
            "home_canonical_id": forecast_container.fixture.home_canonical_id,
            "away_canonical_id": forecast_container.fixture.away_canonical_id,
            "competition": forecast_container.fixture.competition,
            "competition_canonical_id": forecast_container.fixture.competition_canonical_id,
            "season": forecast_container.fixture.season,
            "match_date": forecast_container.fixture.match_date,
            "kickoff_time": forecast_container.fixture.kickoff_time,
            "venue": forecast_container.fixture.venue,
            "is_verified": forecast_container.fixture.is_verified,
        }

        # 2. Extract Forecast Probabilities
        forecast_probs = {}
        if forecast_container.forecast_output:
            fc = forecast_container.forecast_output
            forecast_probs = {
                "expected_home_goals": fc.expected_home_goals,
                "expected_away_goals": fc.expected_away_goals,
                "probabilities_1x2": fc.probabilities_1x2,
                "probabilities_totals": fc.probabilities_totals,
                "probabilities_btts": fc.probabilities_btts,
                "correct_score_matrix": fc.correct_score_matrix,
            }

        # 3. Extract Market Probabilities
        market_probs = {}
        for mkt_id, mkt in market_report.mapped_markets.items():
            market_probs[mkt_id] = {
                "market_name": mkt.market_name,
                "market_type": mkt.market_type,
                "is_supported": mkt.is_supported,
                "unsupported_reason": mkt.unsupported_reason,
                "outcomes": [
                    {"outcome_id": o.outcome_id, "name": o.outcome_name, "probability": o.probability}
                    for o in mkt.outcomes
                ],
            }

        # 4. Extract Confidence & Risk Assessment
        overall_decision = DecisionStatus.ELIGIBLE.value
        all_reasons: List[str] = []
        all_blocked_reasons: List[str] = []
        confidence_summary: Dict[str, Any] = {}
        risk_summary: Dict[str, Any] = {}

        if forecast_container.validation_status != "READY":
            overall_decision = DecisionStatus.BLOCKED.value
            if forecast_container.blocked_reason:
                all_blocked_reasons.append(forecast_container.blocked_reason)

        for mkt_id, dec in risk_report.market_decisions.items():
            confidence_summary[mkt_id] = {
                "score": dec.confidence_score,
                "level": dec.confidence_level.value,
            }
            risk_summary[mkt_id] = {
                "risk_flags": [f.value for f in dec.risk_flags],
                "decision_status": dec.decision_status.value,
                "decision_reasons": dec.decision_reasons,
            }
            all_reasons.extend(dec.decision_reasons)

        if overall_decision != DecisionStatus.BLOCKED.value:
            if risk_report.eligible_markets_count > 0:
                overall_decision = DecisionStatus.ELIGIBLE.value
            elif risk_report.no_bet_markets_count > 0:
                overall_decision = DecisionStatus.LOW_CONFIDENCE.value

        # 5. Build Provenance Chain
        provenance_chain = PredictionChainProvenance(
            fixture_id=forecast_container.fixture.fixture_id,
            fixture_verification_method=forecast_container.fixture.verification_method,
            evidence_items_evaluated_count=len(forecast_container.feature_provenance),
            validated_evidence_count=len(forecast_container.feature_provenance),
            updated_features_count=len(forecast_container.updated_feature_vector),
            feature_provenance_records_count=len(forecast_container.feature_provenance),
            model_name=forecast_container.model_name,
            model_version=forecast_container.model_version,
            calibration_method=forecast_container.calibration_method,
            supported_markets_count=market_report.supported_markets_count,
            unsupported_markets_count=market_report.unsupported_markets_count,
            evaluated_risk_flags_count=sum(len(d["risk_flags"]) for d in risk_summary.values()),
        )

        # 6. Calculate Deterministic SHA256 Audit Hash
        audit_payload = {
            "fixture_id": forecast_container.fixture.fixture_id,
            "prediction_timestamp_utc": forecast_container.prediction_timestamp_utc,
            "model_name": forecast_container.model_name,
            "model_version": forecast_container.model_version,
            "calibration_method": forecast_container.calibration_method,
            "forecast_probabilities": forecast_probs,
            "market_probabilities": market_probs,
            "overall_decision": overall_decision,
        }
        audit_hash = hashlib.sha256(json.dumps(audit_payload, sort_keys=True).encode("utf-8")).hexdigest()

        report = AuditablePredictionReport(
            report_id=report_id,
            prediction_id=prediction_id,
            fixture_id=forecast_container.fixture.fixture_id,
            prediction_timestamp_utc=forecast_container.prediction_timestamp_utc,
            fixture_summary=fixture_summary,
            model_name=forecast_container.model_name,
            model_version=forecast_container.model_version,
            calibration_method=forecast_container.calibration_method,
            forecast_probabilities=forecast_probs,
            market_probabilities=market_probs,
            confidence_metrics=confidence_summary,
            risk_assessment=risk_summary,
            final_decision_status=overall_decision,
            decision_reasons=sorted(list(set(all_reasons))),
            blocked_reasons=all_blocked_reasons if all_blocked_reasons else None,
            provenance_chain=provenance_chain,
            audit_hash=audit_hash,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            reporting_engine_version="STAGE19_AUDITABLE_REPORTING_v1.0.0",
        )

        logger.info(f"Auditable report successfully created: Report ID={report_id}, Audit Hash={audit_hash[:12]}...")
        return report
