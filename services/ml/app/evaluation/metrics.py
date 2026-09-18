"""
Model Evaluation Metrics Module

Calculates probabilistic and accuracy evaluation metrics over historical match forecasts:
- 1X2 Multi-class Log Loss
- 1X2 Multi-class Brier Score
- 1X2 Ranked Probability Score (RPS)
- Expected Goals MAE & RMSE
- Over/Under 2.5 Log Loss & Brier Score
- BTTS Log Loss & Brier Score
"""

import math
from typing import Any, Dict, List

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import ForecastOutput


def calculate_1x2_log_loss(forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]) -> float:
    eps = 1e-15
    total_ll = 0.0
    count = 0

    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "full_time_result" not in vec.targets or vec.targets["full_time_result"] is None:
            continue

        res = vec.targets["full_time_result"]
        p_home = max(eps, min(1.0 - eps, fc.probabilities_1x2.get("home", 0.33)))
        p_draw = max(eps, min(1.0 - eps, fc.probabilities_1x2.get("draw", 0.33)))
        p_away = max(eps, min(1.0 - eps, fc.probabilities_1x2.get("away", 0.33)))

        if res == "H":
            total_ll += -math.log(p_home)
        elif res == "D":
            total_ll += -math.log(p_draw)
        elif res == "A":
            total_ll += -math.log(p_away)
        else:
            continue
        count += 1

    return float(total_ll / count) if count > 0 else 0.0


def calculate_1x2_brier_score(forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]) -> float:
    total_bs = 0.0
    count = 0

    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "full_time_result" not in vec.targets or vec.targets["full_time_result"] is None:
            continue

        res = vec.targets["full_time_result"]
        p_home = fc.probabilities_1x2.get("home", 0.33)
        p_draw = fc.probabilities_1x2.get("draw", 0.33)
        p_away = fc.probabilities_1x2.get("away", 0.33)

        y_h = 1.0 if res == "H" else 0.0
        y_d = 1.0 if res == "D" else 0.0
        y_a = 1.0 if res == "A" else 0.0

        bs = (p_home - y_h) ** 2 + (p_draw - y_d) ** 2 + (p_away - y_a) ** 2
        total_bs += bs
        count += 1

    return float(total_bs / count) if count > 0 else 0.0


def calculate_1x2_rps(forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]) -> float:
    """
    Calculates Ranked Probability Score (RPS) for ordered 1X2 outcomes (H, D, A).
    RPS = 0.5 * [(P_H - Y_H)^2 + ((P_H + P_D) - (Y_H + Y_D))^2]
    """
    total_rps = 0.0
    count = 0

    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "full_time_result" not in vec.targets or vec.targets["full_time_result"] is None:
            continue

        res = vec.targets["full_time_result"]
        p_home = fc.probabilities_1x2.get("home", 0.33)
        p_draw = fc.probabilities_1x2.get("draw", 0.33)

        y_h = 1.0 if res == "H" else 0.0
        y_d = 1.0 if res == "D" else 0.0

        cum_p1 = p_home
        cum_p2 = p_home + p_draw

        cum_y1 = y_h
        cum_y2 = y_h + y_d

        rps = 0.5 * ((cum_p1 - cum_y1) ** 2 + (cum_p2 - cum_y2) ** 2)
        total_rps += rps
        count += 1

    return float(total_rps / count) if count > 0 else 0.0


def calculate_goal_mae_and_rmse(
    forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]
) -> Dict[str, float]:
    total_home_abs_err = 0.0
    total_away_abs_err = 0.0
    total_total_abs_err = 0.0

    total_home_sq_err = 0.0
    total_away_sq_err = 0.0
    total_total_sq_err = 0.0

    count = 0
    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "full_time_home_goals" not in vec.targets:
            continue

        act_h = float(vec.targets["full_time_home_goals"])
        act_a = float(vec.targets["full_time_away_goals"])
        act_tot = act_h + act_a

        pred_h = fc.expected_home_goals
        pred_a = fc.expected_away_goals
        pred_tot = pred_h + pred_a

        err_h = pred_h - act_h
        err_a = pred_a - act_a
        err_tot = pred_tot - act_tot

        total_home_abs_err += abs(err_h)
        total_away_abs_err += abs(err_a)
        total_total_abs_err += abs(err_tot)

        total_home_sq_err += err_h**2
        total_away_sq_err += err_a**2
        total_total_sq_err += err_tot**2

        count += 1

    if count == 0:
        return {
            "home_goals_mae": 0.0,
            "away_goals_mae": 0.0,
            "total_goals_mae": 0.0,
            "home_goals_rmse": 0.0,
            "away_goals_rmse": 0.0,
            "total_goals_rmse": 0.0,
        }

    return {
        "home_goals_mae": float(total_home_abs_err / count),
        "away_goals_mae": float(total_away_abs_err / count),
        "total_goals_mae": float(total_total_abs_err / count),
        "home_goals_rmse": float(math.sqrt(total_home_sq_err / count)),
        "away_goals_rmse": float(math.sqrt(total_away_sq_err / count)),
        "total_goals_rmse": float(math.sqrt(total_total_sq_err / count)),
    }


def calculate_btts_metrics(forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]) -> Dict[str, float]:
    eps = 1e-15
    total_bs = 0.0
    total_ll = 0.0
    count = 0

    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "btts" not in vec.targets:
            continue

        act_btts = 1.0 if vec.targets["btts"] is True else 0.0
        p_yes = fc.probabilities_btts.get("btts_yes", 0.5)

        total_bs += (p_yes - act_btts) ** 2
        p_clamped = max(eps, min(1.0 - eps, p_yes if act_btts == 1.0 else (1.0 - p_yes)))
        total_ll += -math.log(p_clamped)
        count += 1

    if count == 0:
        return {"btts_brier_score": 0.0, "btts_log_loss": 0.0}

    return {
        "btts_brier_score": float(total_bs / count),
        "btts_log_loss": float(total_ll / count),
    }


def calculate_over_under_2_5_metrics(
    forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]
) -> Dict[str, float]:
    eps = 1e-15
    total_bs = 0.0
    total_ll = 0.0
    count = 0

    vector_map = {v.fixture_id: v for v in test_vectors}

    for fc in forecasts:
        vec = vector_map.get(fc.fixture_id)
        if not vec or "total_goals" not in vec.targets:
            continue

        act_over = 1.0 if vec.targets["total_goals"] > 2.5 else 0.0
        p_over = fc.probabilities_totals.get("over_2_5", 0.5)

        total_bs += (p_over - act_over) ** 2
        p_clamped = max(eps, min(1.0 - eps, p_over if act_over == 1.0 else (1.0 - p_over)))
        total_ll += -math.log(p_clamped)
        count += 1

    if count == 0:
        return {"over_2_5_brier_score": 0.0, "over_2_5_log_loss": 0.0}

    return {
        "over_2_5_brier_score": float(total_bs / count),
        "over_2_5_log_loss": float(total_ll / count),
    }


def evaluate_forecast_performance(
    forecasts: List[ForecastOutput], test_vectors: List[MatchFeatureVector]
) -> Dict[str, Any]:
    """
    Computes full benchmark evaluation suite over test forecasts.
    """
    log_loss_1x2 = calculate_1x2_log_loss(forecasts, test_vectors)
    brier_score_1x2 = calculate_1x2_brier_score(forecasts, test_vectors)
    rps_1x2 = calculate_1x2_rps(forecasts, test_vectors)
    goal_errors = calculate_goal_mae_and_rmse(forecasts, test_vectors)
    btts_metrics = calculate_btts_metrics(forecasts, test_vectors)
    over_under_metrics = calculate_over_under_2_5_metrics(forecasts, test_vectors)

    return {
        "total_test_fixtures_evaluated": len(forecasts),
        "1x2_log_loss": round(log_loss_1x2, 5),
        "1x2_brier_score": round(brier_score_1x2, 5),
        "1x2_ranked_probability_score": round(rps_1x2, 5),
        "goal_metrics": {k: round(v, 5) for k, v in goal_errors.items()},
        "btts_metrics": {k: round(v, 5) for k, v in btts_metrics.items()},
        "over_under_2_5_metrics": {k: round(v, 5) for k, v in over_under_metrics.items()},
    }
