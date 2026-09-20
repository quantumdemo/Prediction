"""
Stage 20 Complete End-to-End Prediction Integration Pipeline Implementation

Orchestrates Stages 14-19 sequentially:
Fixture Verification (Stage 14) -> Web Research (Stage 14) -> Evidence Validation (Stage 15) -> Feature Update (Stage 16) -> Forecast (Stage 16/13) -> Market Mapping (Stage 17) -> Risk/NO-BET (Stage 18) -> Auditable Report (Stage 19) -> History Persistence (Stage 19).
Short-circuits downstream stages upon blocking failures.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.ml.app.evidence.schemas import EvidenceValidationReport
from services.ml.app.evidence.validator import EvidenceValidationEngine
from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.markets.mapper import MarketMapper
from services.ml.app.markets.schemas import MappedMarketReport
from services.ml.app.pipeline.forecaster import CurrentMatchForecastingPipeline
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer
from services.ml.app.reporting.generator import AuditableReportGenerator
from services.ml.app.reporting.repository import PredictionHistoryRepository
from services.ml.app.reporting.schemas import AuditablePredictionReport
from services.ml.app.research.engine import CurrentMatchResearchEngine
from services.ml.app.research.schemas import FixtureVerification, ResearchReport
from services.ml.app.research.verification import FixtureVerifier
from services.ml.app.risk.engine import RiskEngine
from services.ml.app.risk.schemas import DecisionStatus, RiskEngineReport
from services.ml.app.integration.schemas import EndToEndPredictionResponse, PredictionPipelineRequest

logger = logging.getLogger("football_ml.integration.pipeline")


class EndToEndPredictionPipeline:
    """
    Production End-to-End Prediction Pipeline (Stages 14-19 Integration).
    """

    def __init__(
        self,
        repository: Optional[PredictionHistoryRepository] = None,
        production_model: Optional[Any] = None,
    ):
        self.verifier = FixtureVerifier()
        self.research_engine = CurrentMatchResearchEngine()
        self.evidence_validator = EvidenceValidationEngine()
        self.forecasting_pipeline = CurrentMatchForecastingPipeline(production_model=production_model)
        self.market_mapper = MarketMapper()
        self.risk_engine = RiskEngine()
        self.report_generator = AuditableReportGenerator()
        self.repository = repository or PredictionHistoryRepository()

    def execute_prediction_pipeline(
        self, request: PredictionPipelineRequest
    ) -> EndToEndPredictionResponse:
        pred_ts = request.prediction_timestamp_utc or datetime.now(timezone.utc).isoformat()
        logger.info(f"Executing End-to-End Prediction Pipeline for fixture '{request.home_team}' vs '{request.away_team}' ({request.match_date})...")

        # ---------------------------------------------------------------------
        # STAGE 14: Fixture Identity Verification & Alias Resolution
        # ---------------------------------------------------------------------
        try:
            verified_fixture: FixtureVerification = self.verifier.verify_fixture(
                fixture_id=request.fixture_id,
                home_team=request.home_team,
                away_team=request.away_team,
                competition=request.competition,
                season=request.season,
                match_date=request.match_date,
                kickoff_time=request.kickoff_time,
                venue=request.venue,
            )
        except Exception as e:
            logger.warning(f"Stage 14 Verification Failed: {e}")
            unverified_fixture = FixtureVerification(
                fixture_id=request.fixture_id or "UNVERIFIED_ID",
                home_team=request.home_team,
                away_team=request.away_team,
                home_canonical_id="CLUB_UNVERIFIED_HOME",
                away_canonical_id="CLUB_UNVERIFIED_AWAY",
                competition=request.competition,
                competition_canonical_id="COMP_UNVERIFIED",
                season=request.season,
                match_date=request.match_date or "1900-01-01",
                is_verified=False,
            )
            return self._handle_pipeline_blocking(
                fixture=unverified_fixture,
                prediction_ts=pred_ts,
                blocked_reason=f"UNVERIFIED_FIXTURE: {str(e)}",
                base_features=request.base_features or {},
            )

        # ---------------------------------------------------------------------
        # STAGE 14: Current-Match Research Collection
        # ---------------------------------------------------------------------
        research_report: ResearchReport = self.research_engine.research_fixture(
            fixture=verified_fixture,
            raw_evidence_inputs=request.raw_research_inputs,
        )

        # ---------------------------------------------------------------------
        # STAGE 15: Evidence Validation & Provenance
        # ---------------------------------------------------------------------
        validation_report: EvidenceValidationReport = self.evidence_validator.validate_research_report(
            research_report=research_report
        )

        # ---------------------------------------------------------------------
        # STAGE 16: Current Feature Update & Forecasting Pipeline
        # ---------------------------------------------------------------------
        base_feats = request.base_features or {fname: 0.0 for fname in STAGE9_FEATURE_REGISTRY.keys()}
        base_vector = MatchFeatureVector(
            fixture_id=verified_fixture.fixture_id,
            match_date=verified_fixture.match_date,
            competition_id=verified_fixture.competition_canonical_id,
            season_id=f"SEASON_{verified_fixture.season}",
            home_club_id=verified_fixture.home_canonical_id,
            away_club_id=verified_fixture.away_canonical_id,
            features=base_feats,
            feature_availability={k: "PRESENT" if v is not None else "INSUFFICIENT_HISTORY" for k, v in base_feats.items()},
            targets={"full_time_result": "H", "full_time_home_goals": 1, "full_time_away_goals": 0, "total_goals": 1, "btts": False},
        )

        forecast_container: CurrentMatchForecastContainer = self.forecasting_pipeline.generate_current_match_forecast(
            fixture=verified_fixture,
            validation_report=validation_report,
            base_feature_vector=base_vector,
            prediction_timestamp_utc=pred_ts,
        )

        # SHORT-CIRCUIT BLOCKING: If forecasting pipeline blocked, stop downstream mapping/risk
        if forecast_container.validation_status != "READY" or not forecast_container.forecast_output:
            logger.warning(f"Pipeline short-circuiting: Forecasting blocked ({forecast_container.blocked_reason}).")
            return self._handle_pipeline_blocking(
                fixture=verified_fixture,
                prediction_ts=pred_ts,
                blocked_reason=forecast_container.blocked_reason or "BLOCKED_NO_FORECAST",
                base_features=forecast_container.updated_feature_vector,
            )

        # ---------------------------------------------------------------------
        # STAGE 17: Market Catalogue & Mapping
        # ---------------------------------------------------------------------
        mapped_market_report: MappedMarketReport = self.market_mapper.map_forecast_container_to_markets(
            container=forecast_container
        )

        # ---------------------------------------------------------------------
        # STAGE 18: Risk, Confidence & NO-BET Engine
        # ---------------------------------------------------------------------
        risk_report: RiskEngineReport = self.risk_engine.evaluate_fixture_risk_and_confidence(
            market_report=mapped_market_report,
            forecast_container=forecast_container,
        )

        # ---------------------------------------------------------------------
        # STAGE 19: Auditable Report Generation & Persistence
        # ---------------------------------------------------------------------
        audit_report: AuditablePredictionReport = self.report_generator.generate_report(
            forecast_container=forecast_container,
            market_report=mapped_market_report,
            risk_report=risk_report,
        )

        # Persist to Prediction History Repository
        is_persisted = False
        try:
            is_persisted = self.repository.save_report(audit_report)
        except Exception as e:
            logger.error(f"Failed to persist prediction report to history repository: {e}")

        # Construct End-to-End Structured Response
        supported_mkts_summary = {
            mkt_id: {
                "name": mkt.market_name,
                "is_supported": mkt.is_supported,
                "outcomes": [{"id": o.outcome_id, "name": o.outcome_name, "probability": o.probability} for o in mkt.outcomes],
            }
            for mkt_id, mkt in mapped_market_report.mapped_markets.items()
            if mkt.is_supported
        }

        confidence_sum = {
            mkt_id: {"score": dec.confidence_score, "level": dec.confidence_level.value}
            for mkt_id, dec in risk_report.market_decisions.items()
        }

        risk_flags_sum = {
            mkt_id: [f.value for f in dec.risk_flags]
            for mkt_id, dec in risk_report.market_decisions.items()
        }

        return EndToEndPredictionResponse(
            prediction_id=audit_report.prediction_id,
            report_id=audit_report.report_id,
            audit_hash=audit_report.audit_hash,
            fixture_summary=audit_report.fixture_summary,
            research_status_summary={
                "items_collected": len(research_report.items),
                "items_validated": len(validation_report.validated_items),
                "items_rejected": len(validation_report.rejected_items),
                "conflicting_count": validation_report.conflicting_count,
            },
            feature_status_summary={
                "updated_features_count": len(forecast_container.updated_feature_vector),
                "feature_provenance_count": len(forecast_container.feature_provenance),
            },
            model_attribution={
                "model_name": forecast_container.model_name,
                "model_version": forecast_container.model_version,
                "calibration_method": forecast_container.calibration_method,
            },
            forecast_summary=audit_report.forecast_probabilities,
            supported_markets=supported_mkts_summary,
            confidence_summary=confidence_sum,
            risk_flags=risk_flags_sum,
            decision_status=audit_report.final_decision_status,
            blocked_reasons=audit_report.blocked_reasons,
            auditable_report=audit_report,
            is_persisted=is_persisted,
        )

    def _handle_pipeline_blocking(
        self,
        fixture: FixtureVerification,
        prediction_ts: str,
        blocked_reason: str,
        base_features: Dict[str, Optional[float]],
    ) -> EndToEndPredictionResponse:
        blocked_container = CurrentMatchForecastContainer(
            container_id=f"FC_CONT_BLOCKED_{fixture.fixture_id}_{uuid.uuid4().hex[:6]}",
            fixture=fixture,
            prediction_timestamp_utc=prediction_ts,
            updated_feature_vector=base_features,
            feature_provenance=[],
            validation_status="BLOCKED_NO_FORECAST",
            blocked_reason=blocked_reason,
        )

        unmapped_market_report = self.market_mapper.map_forecast_container_to_markets(blocked_container)
        risk_report = self.risk_engine.evaluate_fixture_risk_and_confidence(unmapped_market_report, blocked_container)
        audit_report = self.report_generator.generate_report(blocked_container, unmapped_market_report, risk_report)

        is_persisted = False
        try:
            is_persisted = self.repository.save_report(audit_report)
        except Exception as e:
            logger.error(f"Failed to persist blocked prediction report to history repository: {e}")

        return EndToEndPredictionResponse(
            prediction_id=audit_report.prediction_id,
            report_id=audit_report.report_id,
            audit_hash=audit_report.audit_hash,
            fixture_summary=audit_report.fixture_summary,
            research_status_summary={"status": "BLOCKED_BEFORE_RESEARCH"},
            feature_status_summary={"status": "BLOCKED_BEFORE_FEATURE_UPDATE"},
            model_attribution={
                "model_name": blocked_container.model_name,
                "model_version": blocked_container.model_version,
                "calibration_method": blocked_container.calibration_method,
            },
            forecast_summary=None,
            supported_markets={},
            confidence_summary={},
            risk_flags={},
            decision_status=DecisionStatus.BLOCKED.value,
            blocked_reasons=[blocked_reason],
            auditable_report=audit_report,
            is_persisted=is_persisted,
        )
