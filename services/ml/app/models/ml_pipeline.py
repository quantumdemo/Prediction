"""
Stage 11 ML Forecasting Pipeline Engine

Orchestrates chronological training, evaluation, comparison against Stage 10 baselines,
and artifact generation for Stage 11 ML models.
Guarantees zero future-data leakage and reproducible model training.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.ml.app.evaluation.metrics import evaluate_forecast_performance
from services.ml.app.features.engine import MatchFeatureVector, Stage9FeatureEngine
from services.ml.app.models.base import ModelMetadata
from services.ml.app.models.benchmark import EmpiricalBaselineModel
from services.ml.app.models.dixon_coles import DixonColesGoalModel
from services.ml.app.models.logistic_regression import LogisticRegressionForecaster
from services.ml.app.models.ml_base import EXCLUDED_FIELDS_RECORD, ML_FEATURE_NAMES
from services.ml.app.models.poisson import PoissonGoalModel
from services.ml.app.models.random_forest import RandomForestForecaster
from services.ml.app.models.versioning import generate_model_artifact
from services.ml.app.models.xgboost_model import XGBoostForecaster

logger = logging.getLogger("football_ml.models.ml_pipeline")


class Stage11MLPipelineEngine:
    """
    Pipeline Engine for Stage 11 ML Forecasting Models and Baseline Comparison.
    """

    def __init__(self, artifact_output_dir: str = "/tmp/stage11_artifacts"):
        self.feature_engine = Stage9FeatureEngine()
        self.artifact_output_dir = artifact_output_dir

    def run_stage11_pipeline(
        self,
        vectors: Optional[List[MatchFeatureVector]] = None,
        train_ratio: float = 0.80,
    ) -> Dict[str, Any]:
        logger.info("Starting Stage 11 ML Forecasting Pipeline Engine...")

        if vectors is None:
            logger.info("Calculating Stage 9 pre-match feature vectors...")
            vectors = self.feature_engine.calculate_features_for_all_fixtures()

        # Sort strictly chronologically
        sorted_vectors = sorted(vectors, key=lambda v: v.match_date)

        # Chronological split
        split_idx = int(len(sorted_vectors) * train_ratio)
        train_vectors = sorted_vectors[:split_idx]
        test_vectors = sorted_vectors[split_idx:]

        train_start = train_vectors[0].match_date if train_vectors else ""
        train_end = train_vectors[-1].match_date if train_vectors else ""
        test_start = test_vectors[0].match_date if test_vectors else ""
        test_end = test_vectors[-1].match_date if test_vectors else ""

        results = {}

        # 1. Logistic Regression Forecaster
        logger.info("Training Logistic Regression Forecaster...")
        lr_model = LogisticRegressionForecaster()
        lr_model.fit(train_vectors)
        lr_forecasts = lr_model.predict_batch(test_vectors)
        lr_eval = evaluate_forecast_performance(lr_forecasts, test_vectors)

        lr_meta = ModelMetadata(
            model_name=lr_model.model_name,
            model_version=lr_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={"features_used": ML_FEATURE_NAMES, "exclusions": EXCLUDED_FIELDS_RECORD},
            configuration={"solver": "lbfgs", "max_iter": 500},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=lr_eval,
        )
        results["logistic_regression"] = generate_model_artifact(lr_meta, self.artifact_output_dir)

        # 2. Random Forest Forecaster
        logger.info("Training Random Forest Forecaster...")
        rf_model = RandomForestForecaster()
        rf_model.fit(train_vectors)
        rf_forecasts = rf_model.predict_batch(test_vectors)
        rf_eval = evaluate_forecast_performance(rf_forecasts, test_vectors)

        rf_meta = ModelMetadata(
            model_name=rf_model.model_name,
            model_version=rf_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={"features_used": ML_FEATURE_NAMES, "exclusions": EXCLUDED_FIELDS_RECORD},
            configuration={"n_estimators": 100, "max_depth": 8},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=rf_eval,
        )
        results["random_forest"] = generate_model_artifact(rf_meta, self.artifact_output_dir)

        # 3. XGBoost Forecaster
        logger.info("Training XGBoost Forecaster...")
        xgb_model = XGBoostForecaster()
        xgb_model.fit(train_vectors)
        xgb_forecasts = xgb_model.predict_batch(test_vectors)
        xgb_eval = evaluate_forecast_performance(xgb_forecasts, test_vectors)

        xgb_meta = ModelMetadata(
            model_name=xgb_model.model_name,
            model_version=xgb_model.model_version,
            dataset_version="STAGE9_FEATURE_DATASET_v1.0.0",
            feature_version="STAGE9_FEATURE_DATASET_v1.0.0",
            training_period_start=train_start,
            training_period_end=train_end,
            evaluation_period_start=test_start,
            evaluation_period_end=test_end,
            parameters={"features_used": ML_FEATURE_NAMES, "exclusions": EXCLUDED_FIELDS_RECORD},
            configuration={"n_estimators": 100, "max_depth": 5, "learning_rate": 0.05},
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            evaluation_results=xgb_eval,
        )
        results["xgboost"] = generate_model_artifact(xgb_meta, self.artifact_output_dir)

        # 4. Stage 10 Statistical Baselines Comparison
        logger.info("Evaluating Stage 10 Baselines for Comparison...")
        poisson = PoissonGoalModel()
        poisson.fit(train_vectors)
        poisson_eval = evaluate_forecast_performance(poisson.predict_batch(test_vectors), test_vectors)

        dc = DixonColesGoalModel()
        dc.fit(train_vectors)
        dc_eval = evaluate_forecast_performance(dc.predict_batch(test_vectors), test_vectors)

        emp = EmpiricalBaselineModel()
        emp.fit(train_vectors)
        emp_eval = evaluate_forecast_performance(emp.predict_batch(test_vectors), test_vectors)

        summary = {
            "dataset_version": "STAGE9_FEATURE_DATASET_v1.0.0",
            "total_fixtures": len(sorted_vectors),
            "train_size": len(train_vectors),
            "test_size": len(test_vectors),
            "training_period": f"{train_start} to {train_end}",
            "evaluation_period": f"{test_start} to {test_end}",
            "features_used_count": len(ML_FEATURE_NAMES),
            "ml_models": results,
            "stage10_baselines": {
                "poisson": poisson_eval,
                "dixon_coles": dc_eval,
                "empirical": emp_eval,
            },
        }

        logger.info("Stage 11 ML Pipeline Engine completed successfully.")
        return summary
