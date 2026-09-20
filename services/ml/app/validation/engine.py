"""
Stage 22 Shadow Validation Engine Implementation

Executes controlled historical shadow validation across real pre-match feature vectors (Stage 9)
and approved production forecaster (`xgboost_platt` from Stage 13).
Guarantees strict temporal separation: PREDICTION INPUT DATA is kept completely isolated
from POST-PREDICTION EVALUATION DATA (actual outcomes).
Tracks model provenance and statistical interpretation when evaluation overlaps Stage 13 selection dates.
"""

import json
import logging
import math
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.evaluation.metrics import (
    calculate_1x2_brier_score,
    calculate_1x2_log_loss,
    calculate_1x2_rps,
    calculate_btts_metrics,
    calculate_goal_mae_and_rmse,
    calculate_over_under_2_5_metrics,
)
from services.ml.app.features.engine import MatchFeatureVector, Stage9FeatureEngine
from services.ml.app.integration.pipeline import EndToEndPredictionPipeline
from services.ml.app.integration.schemas import PredictionPipelineRequest
from services.ml.app.models.base import ForecastOutput
from services.ml.app.models.xgboost_model import XGBoostForecaster
from services.ml.app.risk.schemas import DecisionStatus
from services.ml.app.selection.selector import ModelSelector
from services.ml.app.validation.schemas import (
    ActualMatchOutcome,
    DataQualityValidationSummary,
    FixtureEvaluationRecord,
    ShadowPredictionRecord,
    ShadowValidationArtifact,
    ValidationAggregateMetrics,
)

logger = logging.getLogger("football_ml.validation.engine")


class OutcomeLeakageError(Exception):
    """Raised when actual match outcome data leaks into pre-match prediction input."""

    pass


class ShadowValidationEngine:
    """
    Stage 22 Controlled Historical Shadow Testing & Validation Engine.
    """

    def __init__(
        self,
        evaluation_period_start: str = "2023-07-01",
        evaluation_period_end: str = "2024-06-30",
        training_cutoff_date: str = "2023-06-30",
    ):
        self.evaluation_period_start = evaluation_period_start
        self.evaluation_period_end = evaluation_period_end
        self.training_cutoff_date = training_cutoff_date
        self.feature_engine = Stage9FeatureEngine()

        # Initialize production forecaster xgboost_platt from Stage 13
        selector = ModelSelector()
        self.production_model = selector.get_production_forecaster()

        self.pipeline = EndToEndPredictionPipeline(production_model=self.production_model)

    def run_shadow_validation(
        self,
        vectors: Optional[List[MatchFeatureVector]] = None,
        artifact_output_dir: str = "/tmp/stage22_artifacts",
    ) -> ShadowValidationArtifact:
        """
        Executes historical shadow testing over post-training evaluation period.
        """
        run_id = f"STAGE22_RUN_{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Starting Stage 22 Shadow Validation Run '{run_id}' ({self.evaluation_period_start} to {self.evaluation_period_end})...")

        if vectors is None:
            vectors = self.feature_engine.calculate_features_for_all_fixtures()

        # Filter vectors chronologically for evaluation period
        total_considered = len(vectors)
        eval_vectors = [
            v for v in vectors if self.evaluation_period_start <= v.match_date <= self.evaluation_period_end
        ]

        exclusion_reasons: Dict[str, int] = {
            "outside_evaluation_period": total_considered - len(eval_vectors),
            "missing_targets": 0,
            "invalid_dates": 0,
        }

        records: List[FixtureEvaluationRecord] = []
        forecast_outputs_for_metrics: List[ForecastOutput] = []
        matching_eval_vectors: List[MatchFeatureVector] = []

        no_bet_count = 0
        blocked_count = 0
        eligible_count = 0

        for vec in eval_vectors:
            # Audit fixture eligibility
            t = vec.targets
            if "full_time_result" not in t or t["full_time_result"] is None:
                exclusion_reasons["missing_targets"] += 1
                continue

            # STEP 1: PREDICTION INPUT ISOLATION
            # Construct prediction request using ONLY pre-match features and fixture metadata
            pre_match_request = self._build_pre_match_request(vec)

            # LEAKAGE GUARD: Ensure result/goals are strictly excluded from input request
            self._verify_no_leakage_in_request(pre_match_request)

            # STEP 2: GENERATE SHADOW PREDICTION via Pipeline
            pipeline_response = self.pipeline.execute_prediction_pipeline(pre_match_request)

            # Record shadow prediction
            audit = pipeline_response.auditable_report
            probabilities_1x2 = audit.forecast_probabilities.get("probabilities_1x2")
            probabilities_totals = audit.forecast_probabilities.get("probabilities_totals")
            probabilities_btts = audit.forecast_probabilities.get("probabilities_btts")
            raw_cs_matrix = audit.forecast_probabilities.get("correct_score_matrix")
            probabilities_correct_score = None
            if raw_cs_matrix and isinstance(raw_cs_matrix, dict):
                probabilities_correct_score = {
                    str(k): ({str(subk): subv for subk, subv in v.items()} if isinstance(v, dict) else v)
                    for k, v in raw_cs_matrix.items()
                }

            if "MKT_MATCH_RESULT_1X2" in audit.market_probabilities:
                mkt = audit.market_probabilities["MKT_MATCH_RESULT_1X2"]
                outcomes_dict = {o["id"].replace("1X2_", "").lower(): o["probability"] for o in mkt.get("outcomes", [])}
                if outcomes_dict:
                    probabilities_1x2 = outcomes_dict

            if "MKT_TOTAL_GOALS_OVER_UNDER" in audit.market_probabilities:
                mkt = audit.market_probabilities["MKT_TOTAL_GOALS_OVER_UNDER"]
                outcomes_dict = {o["id"].replace("TOTALS_", "").lower(): o["probability"] for o in mkt.get("outcomes", [])}
                if outcomes_dict:
                    probabilities_totals = outcomes_dict

            if "MKT_BOTH_TEAMS_TO_SCORE" in audit.market_probabilities:
                mkt = audit.market_probabilities["MKT_BOTH_TEAMS_TO_SCORE"]
                outcomes_dict = {o["id"].replace("BTTS_", "").lower(): o["probability"] for o in mkt.get("outcomes", [])}
                if outcomes_dict:
                    probabilities_btts = outcomes_dict

            if "MKT_CORRECT_SCORE_GRID" in audit.market_probabilities:
                mkt = audit.market_probabilities["MKT_CORRECT_SCORE_GRID"]
                outcomes_dict = {o["id"].replace("CS_", ""): o["probability"] for o in mkt.get("outcomes", [])}
                if outcomes_dict:
                    probabilities_correct_score = outcomes_dict

            decision_st = audit.final_decision_status
            if decision_st == DecisionStatus.BLOCKED.value:
                blocked_count += 1
            elif decision_st in (DecisionStatus.INSUFFICIENT_EVIDENCE.value, DecisionStatus.LOW_CONFIDENCE.value, DecisionStatus.HIGH_RISK.value):
                no_bet_count += 1
            else:
                eligible_count += 1

            shadow_rec = ShadowPredictionRecord(
                prediction_id=audit.prediction_id,
                fixture_id=vec.fixture_id,
                match_date=vec.match_date,
                home_team=vec.home_club_id,
                away_team=vec.away_club_id,
                competition=vec.competition_id,
                season=vec.season_id,
                cutoff_timestamp_utc=f"{vec.match_date}T00:00:00Z",
                prediction_timestamp_utc=audit.created_at_utc,
                model_name=audit.model_name,
                model_version=audit.model_version,
                calibration_method=audit.calibration_method,
                probabilities_1x2=probabilities_1x2,
                probabilities_totals=probabilities_totals,
                probabilities_btts=probabilities_btts,
                probabilities_correct_score=probabilities_correct_score,
                expected_home_goals=audit.forecast_probabilities.get("expected_home_goals", 1.2),
                expected_away_goals=audit.forecast_probabilities.get("expected_away_goals", 1.0),
                confidence_score=audit.confidence_metrics.get("overall_score", 0.8),
                confidence_level=audit.confidence_metrics.get("overall_level", "MEDIUM"),
                decision_status=decision_st,
                is_blocked=decision_st == DecisionStatus.BLOCKED.value,
                blocked_reasons=audit.blocked_reasons or [],
                risk_flags=[f for f_list in audit.risk_assessment.values() if isinstance(f_list, list) for f in f_list],
                audit_hash=audit.audit_hash,
            )

            # STEP 3: POST-PREDICTION OUTCOME RECORDING
            # Actual match outcome is strictly created separately AFTER prediction generation
            actual_outcome = ActualMatchOutcome(
                fixture_id=vec.fixture_id,
                match_date=vec.match_date,
                full_time_result=t.get("full_time_result"),
                full_time_home_goals=t.get("full_time_home_goals"),
                full_time_away_goals=t.get("full_time_away_goals"),
                total_goals=t.get("total_goals"),
                btts=t.get("btts"),
            )

            eval_record = FixtureEvaluationRecord(
                fixture_id=vec.fixture_id,
                shadow_prediction=shadow_rec,
                actual_outcome=actual_outcome,
                evaluated=True,
            )
            records.append(eval_record)

            # Accumulate forecast objects for evaluation metric calculation
            if probabilities_1x2 and not shadow_rec.is_blocked:
                fc_out = ForecastOutput(
                    fixture_id=vec.fixture_id,
                    match_date=vec.match_date,
                    model_name=shadow_rec.model_name,
                    model_version="STAGE13_XGBOOST_PLATT_v1.0.0",
                    probabilities_1x2=probabilities_1x2,
                    probabilities_totals=probabilities_totals or {"over_2_5": 0.5, "under_2_5": 0.5},
                    probabilities_btts=probabilities_btts or {"btts_yes": 0.5, "btts_no": 0.5},
                    correct_score_matrix={0: {0: 1.0}},
                    expected_home_goals=shadow_rec.expected_home_goals or 1.2,
                    expected_away_goals=shadow_rec.expected_away_goals or 1.0,
                )
                forecast_outputs_for_metrics.append(fc_out)
                matching_eval_vectors.append(vec)

        eligible_fixtures = len(records)
        excluded_fixtures = total_considered - eligible_fixtures

        # STEP 4: CALCULATE AGGREGATE METRICS
        agg_metrics = self._calculate_aggregate_metrics(
            forecast_outputs=forecast_outputs_for_metrics,
            test_vectors=matching_eval_vectors,
            total_eligible=eligible_fixtures,
            eligible_count=eligible_count,
            no_bet_count=no_bet_count,
            blocked_count=blocked_count,
        )

        data_summary = DataQualityValidationSummary(
            total_fixtures_considered=total_considered,
            eligible_fixtures=eligible_fixtures,
            excluded_fixtures=excluded_fixtures,
            exclusion_reasons=exclusion_reasons,
            no_bet_count=no_bet_count,
            blocked_count=blocked_count,
            eligible_count=eligible_count,
        )

        # Audit Stage 13 model selection overlap
        stage13_selection_end = "2024-05-28"
        has_selection_overlap = self.evaluation_period_start <= stage13_selection_end

        stat_interp = (
            "HISTORICAL_SELECTION_SET_REPLAY (Metrics represent selection-set replay performance and NOT an unbiased out-of-sample performance estimate)."
            if has_selection_overlap
            else "UNSEEN_OUT_OF_SAMPLE_VALIDATION (Metrics represent unbiased out-of-sample performance on fixtures strictly after Stage 13 model selection)."
        )

        artifact = ShadowValidationArtifact(
            run_id=run_id,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            model_name="xgboost_platt",
            model_version="STAGE13_XGBOOST_PLATT_v1.0.0",
            calibration_method="platt_scaling",
            evaluation_period_start=self.evaluation_period_start,
            evaluation_period_end=self.evaluation_period_end,
            training_cutoff_date=self.training_cutoff_date,
            test_cutoff_date=self.evaluation_period_end,
            random_seed=42,
            data_quality=data_summary,
            aggregate_metrics=agg_metrics,
            records=records,
            pre_match_input_leakage_status="VERIFIED_NO_INPUT_LEAKAGE",
            is_unseen_out_of_sample=not has_selection_overlap,
            model_selection_overlap_period="Window 4 (2023-07-01 to 2024-05-28)",
            statistical_interpretation=stat_interp,
        )

        # Export artifact to disk
        self._export_artifact(artifact, output_dir=artifact_output_dir)

        logger.info(f"Stage 22 Shadow Validation Run '{run_id}' completed successfully across {eligible_fixtures} fixtures.")
        return artifact

    def _build_pre_match_request(self, vec: MatchFeatureVector) -> PredictionPipelineRequest:
        """
        Builds a PredictionPipelineRequest using ONLY pre-match feature vectors and fixture metadata.
        """
        return PredictionPipelineRequest(
            fixture_id=vec.fixture_id,
            home_team=vec.home_club_id,
            away_team=vec.away_club_id,
            competition=vec.competition_id,
            season=vec.season_id,
            match_date=vec.match_date,
            kickoff_time="15:00",
            venue="Historical Stadium",
            base_features=dict(vec.features),
            prediction_timestamp_utc=f"{vec.match_date}T12:00:00Z",  # strictly pre-kickoff
        )

    def _verify_no_leakage_in_request(self, request: PredictionPipelineRequest) -> None:
        """
        Guarantees that outcome fields (full_time_result, goals, etc.) are NOT present in request payload.
        """
        leakage_keys = ["full_time_result", "full_time_home_goals", "full_time_away_goals", "total_goals", "btts"]
        for key in leakage_keys:
            if hasattr(request, key):
                raise OutcomeLeakageError(f"Leakage detected: Prediction request contains outcome field '{key}'.")
            if request.base_features and key in request.base_features:
                raise OutcomeLeakageError(f"Leakage detected: Feature dictionary contains outcome field '{key}'.")

    def _calculate_aggregate_metrics(
        self,
        forecast_outputs: List[ForecastOutput],
        test_vectors: List[MatchFeatureVector],
        total_eligible: int,
        eligible_count: int,
        no_bet_count: int,
        blocked_count: int,
    ) -> ValidationAggregateMetrics:
        """
        Computes aggregate metrics post-prediction.
        """
        if not forecast_outputs or total_eligible == 0:
            return ValidationAggregateMetrics(
                total_fixtures_evaluated=0,
                coverage_rate=0.0,
                no_bet_rate=0.0,
                blocked_rate=0.0,
                eligible_rate=0.0,
            )

        ll_1x2 = calculate_1x2_log_loss(forecast_outputs, test_vectors)
        bs_1x2 = calculate_1x2_brier_score(forecast_outputs, test_vectors)
        rps_1x2 = calculate_1x2_rps(forecast_outputs, test_vectors)
        goals_metrics = calculate_goal_mae_and_rmse(forecast_outputs, test_vectors)
        btts_metrics = calculate_btts_metrics(forecast_outputs, test_vectors)
        ou_metrics = calculate_over_under_2_5_metrics(forecast_outputs, test_vectors)

        return ValidationAggregateMetrics(
            total_fixtures_evaluated=len(forecast_outputs),
            log_loss_1x2=round(ll_1x2, 5),
            brier_score_1x2=round(bs_1x2, 5),
            rps_1x2=round(rps_1x2, 5),
            home_goals_mae=round(goals_metrics.get("home_goals_mae", 0.0), 5),
            away_goals_mae=round(goals_metrics.get("away_goals_mae", 0.0), 5),
            total_goals_mae=round(goals_metrics.get("total_goals_mae", 0.0), 5),
            over_2_5_log_loss=round(ou_metrics.get("over_2_5_log_loss", 0.0), 5),
            over_2_5_brier_score=round(ou_metrics.get("over_2_5_brier_score", 0.0), 5),
            btts_log_loss=round(btts_metrics.get("btts_log_loss", 0.0), 5),
            btts_brier_score=round(btts_metrics.get("btts_brier_score", 0.0), 5),
            coverage_rate=round(eligible_count / total_eligible, 4),
            no_bet_rate=round(no_bet_count / total_eligible, 4),
            blocked_rate=round(blocked_count / total_eligible, 4),
            eligible_rate=round(eligible_count / total_eligible, 4),
        )

    def _export_artifact(self, artifact: ShadowValidationArtifact, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "stage22_shadow_validation_artifact.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(artifact.model_dump_json(indent=2))
        logger.info(f"Exported Stage 22 Validation Artifact to '{file_path}'.")
