"""
Stage 12 Step-by-Step Backtest Execution & Aggregation Runner

Runs chronological windows individually with feature caching to optimize performance,
saves per-window out-of-sample forecast outputs, and computes pooled aggregate metrics
for the canonical STAGE12_BACKTEST_ARTIFACT_v1.0.0 report.
"""

import os
import sys
import time
import json
import pickle
import argparse
from datetime import datetime, timezone
from services.ml.app.backtesting.engine import WalkForwardBacktestEngine
from services.ml.app.backtesting.versioning import generate_backtest_artifact
from services.ml.app.evaluation.metrics import evaluate_forecast_performance
from services.ml.app.models.poisson import PoissonGoalModel
from services.ml.app.models.dixon_coles import DixonColesGoalModel
from services.ml.app.models.benchmark import EmpiricalBaselineModel
from services.ml.app.models.logistic_regression import LogisticRegressionForecaster
from services.ml.app.models.random_forest import RandomForestForecaster
from services.ml.app.models.xgboost_model import XGBoostForecaster

WORK_DIR = "/tmp/stage12_artifacts"
CACHE_PATH = os.path.join(WORK_DIR, "feature_vectors_cache.pkl")
os.makedirs(WORK_DIR, exist_ok=True)

def load_or_compute_vectors(engine):
    if os.path.exists(CACHE_PATH):
        print(f"Loading cached feature vectors from {CACHE_PATH}...", flush=True)
        t0 = time.time()
        with open(CACHE_PATH, "rb") as f:
            vectors = pickle.load(f)
        print(f"Loaded {len(vectors)} feature vectors from cache in {time.time()-t0:.2f}s.", flush=True)
        return vectors

    print("Calculating Stage 9 feature vectors...", flush=True)
    t0 = time.time()
    vectors = engine.feature_engine.calculate_features_for_all_fixtures()
    print(f"Calculated {len(vectors)} feature vectors in {time.time()-t0:.2f}s.", flush=True)

    with open(CACHE_PATH, "wb") as f:
        pickle.dump(vectors, f)
    print(f"Cached feature vectors to {CACHE_PATH}", flush=True)
    return vectors

def run_single_window(window_idx: int):
    print(f"\n=======================================================", flush=True)
    print(f"STARTING BACKTEST EXECUTION FOR WINDOW {window_idx}/4", flush=True)
    print(f"=======================================================", flush=True)

    engine = WalkForwardBacktestEngine()
    vectors = load_or_compute_vectors(engine)

    data_quality, eligible_vectors = engine._audit_data_quality(vectors)
    sorted_vectors = sorted(eligible_vectors, key=lambda v: v.match_date)
    sorted_dates = [v.match_date for v in sorted_vectors]
    windows = engine.default_backtest_windows(sorted_dates)

    if window_idx < 1 or window_idx > len(windows):
        raise ValueError(f"Invalid window index {window_idx}. Must be between 1 and {len(windows)}")

    w = windows[window_idx - 1]

    train_vecs = [v for v in sorted_vectors if w.train_start_date <= v.match_date <= w.train_end_date]
    test_vecs = [v for v in sorted_vectors if w.test_start_date <= v.match_date <= w.test_end_date]

    max_tr_date = max(v.match_date for v in train_vecs)
    min_te_date = min(v.match_date for v in test_vecs)

    print(f"Window ID: {w.window_id}", flush=True)
    print(f"Train period: {w.train_start_date} to {w.train_end_date} | Train count: {len(train_vecs)} (Max date: {max_tr_date})", flush=True)
    print(f"Test period:  {w.test_start_date} to {w.test_end_date} | Test count:  {len(test_vecs)} (Min date: {min_te_date})", flush=True)

    if max_tr_date > min_te_date:
        raise ValueError(f"Temporal leakage detected in window {w.window_id}: max train {max_tr_date} > min test {min_te_date}")

    models_dict = {
        "poisson": PoissonGoalModel(),
        "dixon_coles": DixonColesGoalModel(),
        "empirical": EmpiricalBaselineModel(),
        "logistic_regression": LogisticRegressionForecaster(),
        "random_forest": RandomForestForecaster(n_estimators=100, max_depth=8),
        "xgboost": XGBoostForecaster(n_estimators=100, max_depth=5, learning_rate=0.05),
    }

    w_model_evals = {}
    forecast_records = {}

    for m_key, m_obj in models_dict.items():
        print(f"--> [{m_key}] Fitting on {len(train_vecs)} training matches...", flush=True)
        t_f0 = time.time()
        m_obj.fit(train_vecs)
        fit_dur = time.time() - t_f0

        print(f"--> [{m_key}] Predicting on {len(test_vecs)} test matches...", flush=True)
        t_p0 = time.time()
        fcs = m_obj.predict_batch(test_vecs)
        pred_dur = time.time() - t_p0

        m_eval = evaluate_forecast_performance(fcs, test_vecs)
        w_model_evals[m_key] = m_eval

        print(f"    Finished [{m_key:<20}] in fit={fit_dur:.1f}s, pred={pred_dur:.1f}s | 1X2 LogLoss={m_eval['1x2_log_loss']}", flush=True)

        records = []
        for fc, vec in zip(fcs, test_vecs):
            records.append({
                "fixture_id": fc.fixture_id,
                "match_date": fc.match_date,
                "model_name": fc.model_name,
                "expected_home_goals": fc.expected_home_goals,
                "expected_away_goals": fc.expected_away_goals,
                "probabilities_1x2": fc.probabilities_1x2,
                "probabilities_totals": fc.probabilities_totals,
                "probabilities_btts": fc.probabilities_btts,
                "target_1x2": vec.targets.get("full_time_result"),
                "target_home_goals": vec.targets.get("full_time_home_goals"),
                "target_away_goals": vec.targets.get("full_time_away_goals"),
                "target_btts": vec.targets.get("btts"),
                "target_total_goals": vec.targets.get("total_goals"),
            })
        forecast_records[m_key] = records

    out_payload = {
        "window_id": w.window_id,
        "train_period": f"{w.train_start_date} to {w.train_end_date}",
        "test_period": f"{w.test_start_date} to {w.test_end_date}",
        "train_matches": len(train_vecs),
        "test_matches": len(test_vecs),
        "max_train_date": max_tr_date,
        "min_test_date": min_te_date,
        "model_evaluations": w_model_evals,
        "forecast_records": forecast_records,
    }

    out_path = os.path.join(WORK_DIR, f"window_{window_idx}_report.json")
    with open(out_path, "w") as f:
        json.dump(out_payload, f, indent=2)

    print(f"WINDOW {window_idx} COMPLETE! Report saved to {out_path}", flush=True)

def combine_and_generate_artifact():
    print(f"\n=======================================================", flush=True)
    print("COMBINING ALL 4 WINDOW REPORTS & POOLING OOS PREDICTIONS", flush=True)
    print(f"=======================================================", flush=True)

    engine = WalkForwardBacktestEngine()
    vectors = load_or_compute_vectors(engine)
    data_quality, eligible_vectors = engine._audit_data_quality(vectors)
    sorted_vectors = sorted(eligible_vectors, key=lambda v: v.match_date)
    vector_map = {v.fixture_id: v for v in sorted_vectors}

    window_results = []
    window_definitions = []
    model_keys = ["poisson", "dixon_coles", "empirical", "logistic_regression", "random_forest", "xgboost"]
    pooled_forecasts_dict = {m: [] for m in model_keys}
    pooled_vectors_dict = {m: [] for m in model_keys}

    for idx in range(1, 5):
        w_path = os.path.join(WORK_DIR, f"window_{idx}_report.json")
        if not os.path.exists(w_path):
            raise FileNotFoundError(f"Missing window report {w_path}. Run --window {idx} first.")

        with open(w_path, "r") as f:
            w_data = json.load(f)

        window_definitions.append({
            "window_id": w_data["window_id"],
            "train_period": w_data["train_period"],
            "test_period": w_data["test_period"],
            "train_matches": w_data["train_matches"],
            "test_matches": w_data["test_matches"],
        })

        window_results.append({
            "window_id": w_data["window_id"],
            "train_period": w_data["train_period"],
            "test_period": w_data["test_period"],
            "train_matches": w_data["train_matches"],
            "test_matches": w_data["test_matches"],
            "max_train_date": w_data["max_train_date"],
            "min_test_date": w_data["min_test_date"],
            "model_evaluations": w_data["model_evaluations"],
        })

        from services.ml.app.models.base import ForecastOutput
        for m_key in model_keys:
            records = w_data["forecast_records"][m_key]
            for r in records:
                fc = ForecastOutput(
                    fixture_id=r["fixture_id"],
                    match_date=r["match_date"],
                    model_name=r["model_name"],
                    model_version="1.0.0",
                    expected_home_goals=r["expected_home_goals"],
                    expected_away_goals=r["expected_away_goals"],
                    probabilities_1x2=r["probabilities_1x2"],
                    probabilities_totals=r["probabilities_totals"],
                    probabilities_btts=r["probabilities_btts"],
                    correct_score_matrix={0: {0: 1.0}},
                )
                vec = vector_map[r["fixture_id"]]
                pooled_forecasts_dict[m_key].append(fc)
                pooled_vectors_dict[m_key].append(vec)

    print("Computing pooled multi-window evaluation metrics...", flush=True)
    aggregated_metrics = {}
    for m_key in model_keys:
        fcs = pooled_forecasts_dict[m_key]
        vecs = pooled_vectors_dict[m_key]
        print(f"--> Model '{m_key:<20}': Pooled {len(fcs)} out-of-sample predictions across 4 windows", flush=True)
        aggregated_metrics[m_key] = evaluate_forecast_performance(fcs, vecs)

    report_payload = {
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
            "earliest_test_period": "2020-07-01",
            "latest_test_period": "2024-05-28",
        },
        "windows_count": 4,
        "window_definitions": window_definitions,
        "window_results": window_results,
        "aggregated_results": aggregated_metrics,
    }

    artifact = generate_backtest_artifact(report_payload, WORK_DIR)
    print(f"\nSTAGE 12 BACKTEST REPORT ARTIFACT CREATED AT: {WORK_DIR}/stage12_backtest_report.json", flush=True)

    print("\n==========================================================================================", flush=True)
    print("POOLED MULTI-WINDOW AGGREGATE RESULTS TABLE (COPYABLE FOR DOCS)", flush=True)
    print("==========================================================================================", flush=True)
    print(f"| Model Name | 1X2 Log Loss | 1X2 Brier | 1X2 RPS | Home Goal MAE | Away Goal MAE | Over 2.5 Brier | BTTS Brier |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for m_key, m_eval in aggregated_metrics.items():
        print(f"| {m_key} | {m_eval['1x2_log_loss']:.5f} | {m_eval['1x2_brier_score']:.5f} | {m_eval['1x2_ranked_probability_score']:.5f} | {m_eval['goal_metrics']['home_goals_mae']:.3f} | {m_eval['goal_metrics']['away_goals_mae']:.3f} | {m_eval['over_under_2_5_metrics']['over_2_5_brier_score']:.5f} | {m_eval['btts_metrics']['btts_brier_score']:.5f} |")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, help="Window index to execute (1, 2, 3, or 4)")
    parser.add_argument("--combine", action="store_true", help="Combine window reports into final artifact")
    args = parser.parse_args()

    if args.window:
        run_single_window(args.window)
    elif args.combine:
        combine_and_generate_artifact()
    else:
        print("Usage: python scripts/run_stage12_backtest.py --window <1|2|3|4> OR --combine")

if __name__ == "__main__":
    main()
