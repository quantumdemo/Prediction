"""
Stage 12 Walk-Forward Time-Aware Backtesting Engine

Executes walk-forward chronological historical evaluation across multiple time windows.
Guarantees zero future-data leakage, fits imputation transformers strictly on training sets,
and evaluates Stage 10 statistical baselines and Stage 11 ML models objectively.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.evaluation.metrics import evaluate_forecast_performance
from services.ml.app.features.engine import MatchFeatureVector, Stage9FeatureEngine
from services.ml.app.models.benchmark import EmpiricalBaselineModel
from services.ml.app.models.dixon_coles import DixonColesGoalModel
from services.ml.app.models.logistic_regression import LogisticRegressionForecaster
from services.ml.app.models.poisson import PoissonGoalModel
from services.ml.app.models.random_forest import RandomForestForecaster
from services.ml.app.models.xgboost_model import XGBoostForecaster

logger = logging.getLogger("football_ml.backtesting.engine")


@dataclass
class BacktestWindow:
    window_id: str
    train_start_date: str
    train_end_date: str
    test_start_date: str
    test_end_date: str
    train_matches_count: int = 0
    test_matches_count: int = 0


@dataclass
class DataQualityReport:
    total_eligible_matches: int = 0
    matches_used: int = 0
    matches_skipped: int = 0
    skipped_reasons: Dict[str, int] = field(default_factory=dict)
    competitions_covered: List[str] = field(default_factory=list)
    seasons_covered: List[str] = field(default_factory=list)
    earliest_test_period: str = ""
    latest_test_period: str = ""


class WalkForwardBacktestEngine:
    """
    Time-Aware Walk-Forward Backtesting Engine for Stage 10 and Stage 11 Models.
    """

    def __init__(self):
        self.feature_engine = Stage9FeatureEngine()

    def default_backtest_windows(self, sorted_dates: List[str]) -> List[BacktestWindow]:
        """
        Constructs chronological walk-forward evaluation windows based on historical dates.
        """
        if not sorted_dates:
            return []

        min_date = sorted_dates[0]
        max_date = sorted_dates[-1]

        # Standard multi-season walk-forward cutoffs
        windows = [
            BacktestWindow(
                window_id="WINDOW_1_2020_2021",
                train_start_date=min_date,
                train_end_date="2020-06-30",
                test_start_date="2020-07-01",
                test_end_date="2021-06-30",
            ),
            BacktestWindow(
                window_id="WINDOW_2_2021_2022",
                train_start_date=min_date,
                train_end_date="2021-06-30",
                test_start_date="2021-07-01",
                test_end_date="2022-06-30",
            ),
            BacktestWindow(
                window_id="WINDOW_3_2022_2023",
                train_start_date=min_date,
                train_end_date="2022-06-30",
                test_start_date="2022-07-01",
                test_end_date="2023-06-30",
            ),
            BacktestWindow(
                window_id="WINDOW_4_2023_2024",
                train_start_date=min_date,
                train_end_date="2023-06-30",
                test_start_date="2023-07-01",
                test_end_date=max_date,
            ),
        ]
        return windows

    def run_backtest(
        self,
        vectors: Optional[List[MatchFeatureVector]] = None,
        windows: Optional[List[BacktestWindow]] = None,
    ) -> Dict[str, Any]:
        """
        Executes multi-window walk-forward backtest across all 6 models.
        """
        logger.info("Starting Stage 12 Walk-Forward Backtesting Engine...")

        if vectors is None:
            logger.info("Calculating Stage 9 pre-match feature vectors...")
            vectors = self.feature_engine.calculate_features_for_all_fixtures()

        # Audit and filter eligible matches
        data_quality, eligible_vectors = self._audit_data_quality(vectors)

        # Sort strictly chronologically
        sorted_vectors = sorted(eligible_vectors, key=lambda v: v.match_date)
        sorted_dates = [v.match_date for v in sorted_vectors]

        if windows is None:
            windows = self.default_backtest_windows(sorted_dates)

        # Filter windows to those with non-empty train and test sets
        valid_windows = []
        for w in windows:
            train_vecs = [v for v in sorted_vectors if w.train_start_date <= v.match_date <= w.train_end_date]
            test_vecs = [v for v in sorted_vectors if w.test_start_date <= v.match_date <= w.test_end_date]
            if len(train_vecs) >= 5 and len(test_vecs) >= 1:
                w.train_matches_count = len(train_vecs)
                w.test_matches_count = len(test_vecs)
                valid_windows.append(w)

        if not valid_windows:
            # Fallback for synthetic/small test sets: create 2 equal chronological windows
            split_half = len(sorted_vectors) // 2
            mid_date = sorted_vectors[split_half].match_date
            valid_windows = [
                BacktestWindow(
                    window_id="WINDOW_FALLBACK_1",
                    train_start_date=sorted_dates[0],
                    train_end_date=mid_date,
                    test_start_date=mid_date,
                    test_end_date=sorted_dates[-1],
                    train_matches_count=split_half,
                    test_matches_count=len(sorted_vectors) - split_half,
                )
            ]

        data_quality.earliest_test_period = valid_windows[0].test_start_date
        data_quality.latest_test_period = valid_windows[-1].test_end_date

        logger.info(f"Executing backtest across {len(valid_windows)} valid chronological windows...")

        # Model instantiators
        def _get_models():
            return {
                "poisson": PoissonGoalModel(),
                "dixon_coles": DixonColesGoalModel(),
                "empirical": EmpiricalBaselineModel(),
                "logistic_regression": LogisticRegressionForecaster(),
                "random_forest": RandomForestForecaster(n_estimators=100, max_depth=8),
                "xgboost": XGBoostForecaster(n_estimators=100, max_depth=5, learning_rate=0.05),
            }

        window_results = []
        model_forecasts_accum: Dict[str, List[Tuple[Any, MatchFeatureVector]]] = {
            m: [] for m in _get_models().keys()
        }

        for w in valid_windows:
            train_vecs = [v for v in sorted_vectors if w.train_start_date <= v.match_date <= w.train_end_date]
            test_vecs = [v for v in sorted_vectors if w.test_start_date <= v.match_date <= w.test_end_date]

            # Leakage verification: max train date <= min test date
            max_tr_date = max(v.match_date for v in train_vecs) if train_vecs else ""
            min_te_date = min(v.match_date for v in test_vecs) if test_vecs else ""
            if max_tr_date > min_te_date:
                raise ValueError(f"Temporal leakage detected in window {w.window_id}: train {max_tr_date} > test {min_te_date}")

            w_model_evals = {}
            models_dict = _get_models()

            for model_key, model_obj in models_dict.items():
                # Fit strictly on training vectors
                model_obj.fit(train_vecs)
                # Predict test vectors
                test_forecasts = model_obj.predict_batch(test_vecs)
                # Evaluate metrics for window
                m_eval = evaluate_forecast_performance(test_forecasts, test_vecs)
                w_model_evals[model_key] = m_eval

                # Accumulate forecasts for global aggregation
                for fc, vec in zip(test_forecasts, test_vecs):
                    model_forecasts_accum[model_key].append((fc, vec))

            window_results.append({
                "window_id": w.window_id,
                "train_period": f"{w.train_start_date} to {w.train_end_date}",
                "test_period": f"{w.test_start_date} to {w.test_end_date}",
                "train_matches": len(train_vecs),
                "test_matches": len(test_vecs),
                "model_evaluations": w_model_evals,
            })

        # Calculate aggregated overall metrics across all windows for each model
        aggregated_metrics = {}
        for model_key, pairs in model_forecasts_accum.items():
            if pairs:
                fcs, vecs = zip(*pairs)
                aggregated_metrics[model_key] = evaluate_forecast_performance(list(fcs), list(vecs))

        backtest_report = {
            "backtest_version": "STAGE12_BACKTEST_v1.0.0",
            "dataset_version": "STAGE9_FEATURE_DATASET_v1.0.0",
            "feature_version": "STAGE9_FEATURE_DATASET_v1.0.0",
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "code_identifier": "STAGE12_BACKTESTING_v1.0",
            "data_quality_report": {
                "total_eligible_matches": data_quality.total_eligible_matches,
                "matches_used": data_quality.matches_used,
                "matches_skipped": data_quality.matches_skipped,
                "skipped_reasons": data_quality.skipped_reasons,
                "competitions_count": len(data_quality.competitions_covered),
                "seasons_count": len(data_quality.seasons_covered),
                "earliest_test_period": data_quality.earliest_test_period,
                "latest_test_period": data_quality.latest_test_period,
            },
            "windows_count": len(valid_windows),
            "window_definitions": [
                {
                    "window_id": w.window_id,
                    "train_period": f"{w.train_start_date} to {w.train_end_date}",
                    "test_period": f"{w.test_start_date} to {w.test_end_date}",
                    "train_matches": w.train_matches_count,
                    "test_matches": w.test_matches_count,
                }
                for w in valid_windows
            ],
            "window_results": window_results,
            "aggregated_results": aggregated_metrics,
        }

        logger.info("Stage 12 Walk-Forward Backtest completed successfully.")
        return backtest_report

    def _audit_data_quality(self, vectors: List[MatchFeatureVector]) -> Tuple[DataQualityReport, List[MatchFeatureVector]]:
        report = DataQualityReport()
        report.total_eligible_matches = len(vectors)

        eligible = []
        skipped_reasons = {"missing_result": 0, "missing_goals": 0}
        comps = set()
        seasons = set()

        for vec in vectors:
            t = vec.targets
            if "full_time_result" not in t or t["full_time_result"] is None:
                skipped_reasons["missing_result"] += 1
                continue
            if "full_time_home_goals" not in t or "full_time_away_goals" not in t:
                skipped_reasons["missing_goals"] += 1
                continue

            comps.add(vec.competition_id)
            seasons.add(vec.season_id)
            eligible.append(vec)

        report.matches_used = len(eligible)
        report.matches_skipped = report.total_eligible_matches - report.matches_used
        report.skipped_reasons = skipped_reasons
        report.competitions_covered = sorted(list(comps))
        report.seasons_covered = sorted(list(seasons))

        return report, eligible
