"""
Stage 13 Probability Calibrators Implementation

Implements Platt Scaling (Sigmoid Logistic Calibration) and Isotonic Regression
for 1X2 multi-class probabilities, BTTS binary probabilities, and Over/Under 2.5 probabilities.
Guarantees strict probability axioms (all probabilities in [0, 1], sum = 1.0).
Supports fast vectorized batch calibration.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from services.ml.app.models.base import ForecastOutput


class PlattScaler:
    """
    Platt Scaling (Logistic Sigmoid Calibration).
    Fits logistic regression on logit(p) to map uncalibrated probabilities to true empirical frequencies.
    """

    def __init__(self):
        self.calibrators: Dict[str, LogisticRegression] = {}
        self.is_fitted = False

    def fit(self, forecasts: List[ForecastOutput], targets_1x2: List[str], targets_btts: List[bool], targets_over25: List[bool]) -> None:
        if not forecasts or len(forecasts) < 5:
            self.is_fitted = True
            return

        eps = 1e-12

        # 1X2 Multi-class Calibration (Home, Draw, Away)
        for outcome in ["home", "draw", "away"]:
            p_raw = np.array([fc.probabilities_1x2.get(outcome, 0.33) for fc in forecasts])
            y_binary = np.array([1 if t == outcome[0].upper() else 0 for t in targets_1x2])

            if len(np.unique(y_binary)) > 1:
                p_clamped = np.clip(p_raw, eps, 1.0 - eps)
                logits = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)

                clf = LogisticRegression(solver="lbfgs", max_iter=200, random_state=42)
                clf.fit(logits, y_binary)
                self.calibrators[f"1x2_{outcome}"] = clf

        # BTTS Calibration
        p_btts = np.array([fc.probabilities_btts.get("btts_yes", 0.5) for fc in forecasts])
        y_btts = np.array([1 if t is True else 0 for t in targets_btts])
        if len(np.unique(y_btts)) > 1:
            p_clamped = np.clip(p_btts, eps, 1.0 - eps)
            logits_btts = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)

            clf_btts = LogisticRegression(solver="lbfgs", max_iter=200, random_state=42)
            clf_btts.fit(logits_btts, y_btts)
            self.calibrators["btts_yes"] = clf_btts

        # Over 2.5 Totals Calibration
        p_over25 = np.array([fc.probabilities_totals.get("over_2_5", 0.5) for fc in forecasts])
        y_over25 = np.array([1 if t is True else 0 for t in targets_over25])
        if len(np.unique(y_over25)) > 1:
            p_clamped = np.clip(p_over25, eps, 1.0 - eps)
            logits_over25 = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)

            clf_over25 = LogisticRegression(solver="lbfgs", max_iter=200, random_state=42)
            clf_over25.fit(logits_over25, y_over25)
            self.calibrators["over_2_5"] = clf_over25

        self.is_fitted = True

    def calibrate_batch(self, forecasts: List[ForecastOutput]) -> List[ForecastOutput]:
        if not self.is_fitted or not forecasts:
            return forecasts

        eps = 1e-12
        n = len(forecasts)

        # 1X2 Batch Calibration
        cal_1x2_dict = {}
        for outcome in ["home", "draw", "away"]:
            p_raw = np.array([fc.probabilities_1x2.get(outcome, 0.33) for fc in forecasts])
            clf = self.calibrators.get(f"1x2_{outcome}")
            if clf:
                p_clamped = np.clip(p_raw, eps, 1.0 - eps)
                logits = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)
                cal_1x2_dict[outcome] = clf.predict_proba(logits)[:, 1]
            else:
                cal_1x2_dict[outcome] = p_raw

        sum_1x2 = cal_1x2_dict["home"] + cal_1x2_dict["draw"] + cal_1x2_dict["away"]
        sum_1x2 = np.where(sum_1x2 > 0, sum_1x2, 1.0)
        p_home_norm = cal_1x2_dict["home"] / sum_1x2
        p_draw_norm = cal_1x2_dict["draw"] / sum_1x2
        p_away_norm = cal_1x2_dict["away"] / sum_1x2

        # BTTS Batch Calibration
        p_btts_raw = np.array([fc.probabilities_btts.get("btts_yes", 0.5) for fc in forecasts])
        clf_btts = self.calibrators.get("btts_yes")
        if clf_btts:
            p_clamped = np.clip(p_btts_raw, eps, 1.0 - eps)
            logits_btts = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)
            p_btts_cal = clf_btts.predict_proba(logits_btts)[:, 1]
        else:
            p_btts_cal = p_btts_raw
        p_btts_cal = np.clip(p_btts_cal, 0.0, 1.0)

        # Over 2.5 Batch Calibration
        p_over25_raw = np.array([fc.probabilities_totals.get("over_2_5", 0.5) for fc in forecasts])
        clf_over25 = self.calibrators.get("over_2_5")
        if clf_over25:
            p_clamped = np.clip(p_over25_raw, eps, 1.0 - eps)
            logits_over25 = np.log(p_clamped / (1.0 - p_clamped)).reshape(-1, 1)
            p_over25_cal = clf_over25.predict_proba(logits_over25)[:, 1]
        else:
            p_over25_cal = p_over25_raw
        p_over25_cal = np.clip(p_over25_cal, 0.0, 1.0)

        calibrated_fcs = []
        for i, fc in enumerate(forecasts):
            cal_totals = dict(fc.probabilities_totals)
            cal_totals["over_2_5"] = float(p_over25_cal[i])
            cal_totals["under_2_5"] = float(1.0 - p_over25_cal[i])

            calibrated_fcs.append(ForecastOutput(
                fixture_id=fc.fixture_id,
                match_date=fc.match_date,
                model_name=fc.model_name,
                model_version=f"{fc.model_version}_platt",
                expected_home_goals=fc.expected_home_goals,
                expected_away_goals=fc.expected_away_goals,
                probabilities_1x2={
                    "home": float(p_home_norm[i]),
                    "draw": float(p_draw_norm[i]),
                    "away": float(p_away_norm[i]),
                },
                probabilities_totals=cal_totals,
                probabilities_btts={
                    "btts_yes": float(p_btts_cal[i]),
                    "btts_no": float(1.0 - p_btts_cal[i]),
                },
                correct_score_matrix=fc.correct_score_matrix,
                data_quality_status=fc.data_quality_status,
            ))

        return calibrated_fcs

    def calibrate_forecast(self, fc: ForecastOutput) -> ForecastOutput:
        return self.calibrate_batch([fc])[0]


class IsotonicCalibrator:
    """
    Isotonic Regression Calibration.
    Non-parametric monotonically non-decreasing calibration mapping for non-linear decision trees.
    """

    def __init__(self):
        self.calibrators: Dict[str, IsotonicRegression] = {}
        self.is_fitted = False

    def fit(self, forecasts: List[ForecastOutput], targets_1x2: List[str], targets_btts: List[bool], targets_over25: List[bool]) -> None:
        if not forecasts or len(forecasts) < 5:
            self.is_fitted = True
            return

        # 1X2 Multi-class
        for outcome in ["home", "draw", "away"]:
            p_raw = np.array([fc.probabilities_1x2.get(outcome, 0.33) for fc in forecasts])
            y_binary = np.array([1 if t == outcome[0].upper() else 0 for t in targets_1x2])

            if len(np.unique(y_binary)) > 1:
                iso = IsotonicRegression(y_min=0.001, y_max=0.999, out_of_bounds="clip")
                iso.fit(p_raw, y_binary)
                self.calibrators[f"1x2_{outcome}"] = iso

        # BTTS
        p_btts = np.array([fc.probabilities_btts.get("btts_yes", 0.5) for fc in forecasts])
        y_btts = np.array([1 if t is True else 0 for t in targets_btts])
        if len(np.unique(y_btts)) > 1:
            iso_btts = IsotonicRegression(y_min=0.001, y_max=0.999, out_of_bounds="clip")
            iso_btts.fit(p_btts, y_btts)
            self.calibrators["btts_yes"] = iso_btts

        # Over 2.5
        p_over25 = np.array([fc.probabilities_totals.get("over_2_5", 0.5) for fc in forecasts])
        y_over25 = np.array([1 if t is True else 0 for t in targets_over25])
        if len(np.unique(y_over25)) > 1:
            iso_over25 = IsotonicRegression(y_min=0.001, y_max=0.999, out_of_bounds="clip")
            iso_over25.fit(p_over25, y_over25)
            self.calibrators["over_2_5"] = iso_over25

        self.is_fitted = True

    def calibrate_batch(self, forecasts: List[ForecastOutput]) -> List[ForecastOutput]:
        if not self.is_fitted or not forecasts:
            return forecasts

        n = len(forecasts)

        # 1X2 Batch Calibration
        cal_1x2_dict = {}
        for outcome in ["home", "draw", "away"]:
            p_raw = np.array([fc.probabilities_1x2.get(outcome, 0.33) for fc in forecasts])
            iso = self.calibrators.get(f"1x2_{outcome}")
            if iso:
                cal_1x2_dict[outcome] = iso.predict(p_raw)
            else:
                cal_1x2_dict[outcome] = p_raw

        sum_1x2 = cal_1x2_dict["home"] + cal_1x2_dict["draw"] + cal_1x2_dict["away"]
        sum_1x2 = np.where(sum_1x2 > 0, sum_1x2, 1.0)
        p_home_norm = cal_1x2_dict["home"] / sum_1x2
        p_draw_norm = cal_1x2_dict["draw"] / sum_1x2
        p_away_norm = cal_1x2_dict["away"] / sum_1x2

        # BTTS Batch Calibration
        p_btts_raw = np.array([fc.probabilities_btts.get("btts_yes", 0.5) for fc in forecasts])
        iso_btts = self.calibrators.get("btts_yes")
        if iso_btts:
            p_btts_cal = iso_btts.predict(p_btts_raw)
        else:
            p_btts_cal = p_btts_raw
        p_btts_cal = np.clip(p_btts_cal, 0.0, 1.0)

        # Over 2.5 Batch Calibration
        p_over25_raw = np.array([fc.probabilities_totals.get("over_2_5", 0.5) for fc in forecasts])
        iso_over25 = self.calibrators.get("over_2_5")
        if iso_over25:
            p_over25_cal = iso_over25.predict(p_over25_raw)
        else:
            p_over25_cal = p_over25_raw
        p_over25_cal = np.clip(p_over25_cal, 0.0, 1.0)

        calibrated_fcs = []
        for i, fc in enumerate(forecasts):
            cal_totals = dict(fc.probabilities_totals)
            cal_totals["over_2_5"] = float(p_over25_cal[i])
            cal_totals["under_2_5"] = float(1.0 - p_over25_cal[i])

            calibrated_fcs.append(ForecastOutput(
                fixture_id=fc.fixture_id,
                match_date=fc.match_date,
                model_name=fc.model_name,
                model_version=f"{fc.model_version}_isotonic",
                expected_home_goals=fc.expected_home_goals,
                expected_away_goals=fc.expected_away_goals,
                probabilities_1x2={
                    "home": float(p_home_norm[i]),
                    "draw": float(p_draw_norm[i]),
                    "away": float(p_away_norm[i]),
                },
                probabilities_totals=cal_totals,
                probabilities_btts={
                    "btts_yes": float(p_btts_cal[i]),
                    "btts_no": float(1.0 - p_btts_cal[i]),
                },
                correct_score_matrix=fc.correct_score_matrix,
                data_quality_status=fc.data_quality_status,
            ))

        return calibrated_fcs

    def calibrate_forecast(self, fc: ForecastOutput) -> ForecastOutput:
        return self.calibrate_batch([fc])[0]
