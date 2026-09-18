"""
Stage 10 Statistical Baseline Models Pipeline Engine

Orchestrates chronological data splitting, model training, forecasting,
evaluation metric calculation, and artifact creation for Stage 10 baseline models.
Ensures zero data leakage and strict reproducibility.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.ml.app.evaluation.metrics import evaluate_forecast_performance
from services.ml.app.features.engine import MatchFeatureVector, Stage9FeatureEngine
from services.ml.app.models.base import ModelMetadata
from services.ml.app.models.benchmark import EmpiricalBaselineModel
from services.ml.app.models.dixon_coles import DixonColesGoalModel
from services.ml.app.models.poisson import PoissonGoalModel
from services.ml.app.models.versioning import generate_model_artifact

logger = logging.getLogger("football_ml.models.pipeline")


class Stage10StatisticalPipelineEngine:
    """
    Chronological Pipeline Engine for Stage 10 Statistical Baseline Models.
    """

    def __init__(self, artifact_output_dir: str = "/tmp/stage10_artifacts"):
        self.feature_engine = Stage9FeatureEngine()
        self.artifact_output_dir = artifact_output_dir

    def run_stage10_pipeline(
        self,
        vectors: Optional[List[MatchFeatureVector]] = None,
        train_ratio: float = 0.80,
    ) -> Dict[str, Any]:
        """
        Executes full Stage 10 training, evaluation, and artifact generation pipeline.
        """
        logger.info("Starting Stage 10 Statistical Baseline Pipeline...")

        if vectors is None:
            logger.info("Calculating Stage 9 pre-match feature vectors...")
            vectors = self.feature_engine.calculate_features_for_all_fixtures()

        # Sort vectors strictly chronologically
        sorted_vectors = sorted(vectors, key=lambda v: v.match_date)

        # Chronological Train / Test Split
        split_idx = int(len(sorted_vectors) * train_ratio)
        train_vectors = sorted_vectors[:split_idx]
        test_vectors = sorted_vectors[split_idx:]

        train_start = train_vectors[0].match_date if train_vectors else ""
        train_end = train_vectors[-1].match_date if train_vectors else ""
        test_start = test_vectors[0].match_date if test_vectors else ""
        test_end = test_vectors[-1].match_date if test_vectors else ""

        logger.info(
            f"Chronological split: {len(train_vectors)} train ({train_start} to {train_end}), "
            f"{len(test_vectors)} test ({test_start} to {test_end})."
        )

        results = {}

        # 1. Poisson Goal Model
        logger.info("Training Poisson Goal Model...")
        poisson_model = PoissonGoalModel()
        poisson_model.fit(train_vectors)
        poisson_forecasts = poisson_model.predict_batch(test_vectors)
        poisson_eval = evaluate_forecast_performance(poisson_forecasts, test_vectors)

        poisson_meta = ModelMetadata(
            model_name=poisson_model.model_name,
            model_version=poisson_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={
                "mu_home": poisson_model.mu_home,
                "mu_away": poisson_model.mu_away,
                "home_advantage": poisson_model.home_advantage,
                "num_teams_modeled": len(poisson_model.teams_list),
            },
            configuration={"max_goals": poisson_model.max_goals},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=poisson_eval,
        )
        poisson_artifact = generate_model_artifact(poisson_meta, self.artifact_output_dir)
        results["poisson_goal_model"] = poisson_artifact

        # 2. Dixon-Coles Goal Model
        logger.info("Training Dixon-Coles Goal Model...")
        dc_model = DixonColesGoalModel()
        dc_model.fit(train_vectors)
        dc_forecasts = dc_model.predict_batch(test_vectors)
        dc_eval = evaluate_forecast_performance(dc_forecasts, test_vectors)

        dc_meta = ModelMetadata(
            model_name=dc_model.model_name,
            model_version=dc_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={
                "mu_home": dc_model.mu_home,
                "mu_away": dc_model.mu_away,
                "home_advantage": dc_model.home_advantage,
                "rho": dc_model.rho,
                "num_teams_modeled": len(dc_model.teams_list),
            },
            configuration={"max_goals": dc_model.max_goals},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=dc_eval,
        )
        dc_artifact = generate_model_artifact(dc_meta, self.artifact_output_dir)
        results["dixon_coles_goal_model"] = dc_artifact

        # 3. Empirical Baseline Model
        logger.info("Fitting Empirical Baseline Benchmark...")
        emp_model = EmpiricalBaselineModel()
        emp_model.fit(train_vectors)
        emp_forecasts = emp_model.predict_batch(test_vectors)
        emp_eval = evaluate_forecast_performance(emp_forecasts, test_vectors)

        emp_meta = ModelMetadata(
            model_name=emp_model.model_name,
            model_version=emp_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={
                "p_home": emp_model.p_home,
                "p_draw": emp_model.p_draw,
                "p_away": emp_model.p_away,
                "mu_home": emp_model.mu_home,
                "mu_away": emp_model.mu_away,
                "btts_rate": emp_model.btts_rate,
            },
            configuration={"max_goals": emp_model.max_goals},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=emp_eval,
        )
        emp_artifact = generate_model_artifact(emp_meta, self.artifact_output_dir)
        results["empirical_baseline_model"] = emp_artifact

        pipeline_summary = {
            "dataset_version": "STAGE9_FEATURE_DATASET_v1.0.0",
            "total_fixtures": len(sorted_vectors),
            "train_size": len(train_vectors),
            "test_size": len(test_vectors),
            "training_period": f"{train_start} to {train_end}",
            "evaluation_period": f"{test_start} to {test_end}",
            "models": results,
        }

        logger.info("Stage 10 Statistical Baseline Pipeline completed successfully.")
        return pipeline_summary
