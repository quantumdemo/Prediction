"""
XGBoost Gradient Boosted Trees ML Forecaster Implementation

Supervised XGBoost forecaster for football match outcomes.
Fits XGBoost Classifiers for 1X2, BTTS, and Over/Under 2.5,
and XGBoost Regressors for expected home/away goal counts.
"""

from typing import List

import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import ForecastOutput
from services.ml.app.models.ml_base import BaseMLForecaster


class XGBoostForecaster(BaseMLForecaster):
    """
    XGBoost Gradient Boosted Decision Trees Forecaster.
    """

    def __init__(self, max_goals: int = 10, n_estimators: int = 100, max_depth: int = 5, learning_rate: float = 0.05, n_jobs: int = -1):
        super().__init__(model_name="XGBoostForecaster", model_version="1.0.0")
        self.max_goals = max_goals
        self.label_encoder_1x2 = LabelEncoder()

        self.clf_1x2 = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            eval_metric="mlogloss",
            n_jobs=n_jobs,
        )
        self.clf_btts = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            eval_metric="logloss",
            n_jobs=n_jobs,
        )
        self.clf_over25 = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            eval_metric="logloss",
            n_jobs=n_jobs,
        )
        self.reg_home_goals = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            n_jobs=n_jobs,
        )
        self.reg_away_goals = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            n_jobs=n_jobs,
        )

    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        if not training_vectors:
            self.is_fitted = True
            return

        X_train = self.processor.fit_transform(training_vectors)
        y_dict = self.processor.extract_targets(training_vectors)

        if X_train.shape[0] > 0:
            y_1x2_encoded = self.label_encoder_1x2.fit_transform(y_dict["1x2"])
            self.clf_1x2.fit(X_train, y_1x2_encoded)
            self.clf_btts.fit(X_train, y_dict["btts"])
            self.clf_over25.fit(X_train, y_dict["over25"])
            self.reg_home_goals.fit(X_train, y_dict["home_goals"])
            self.reg_away_goals.fit(X_train, y_dict["away_goals"])

        self.is_fitted = True

    def _predict_batch_vectorized(self, vectors: List[MatchFeatureVector]) -> List[ForecastOutput]:
        X_test = self.processor.transform(vectors)

        classes_1x2_num = list(self.clf_1x2.classes_)
        classes_1x2_str = self.label_encoder_1x2.inverse_transform(classes_1x2_num)
        probs_1x2 = self.clf_1x2.predict_proba(X_test)

        classes_btts = list(self.clf_btts.classes_)
        probs_btts = self.clf_btts.predict_proba(X_test)

        lh = self.reg_home_goals.predict(X_test)
        la = self.reg_away_goals.predict(X_test)

        fcs = []
        for i, vec in enumerate(vectors):
            p_map_1x2 = {str(c): float(p) for c, p in zip(classes_1x2_str, probs_1x2[i])}
            p_home = p_map_1x2.get("H", 0.33)
            p_draw = p_map_1x2.get("D", 0.33)
            p_away = p_map_1x2.get("A", 0.33)

            p_map_btts = {int(c): float(p) for c, p in zip(classes_btts, probs_btts[i])}
            p_btts_yes = p_map_btts.get(1, 0.5)

            lambda_h = max(0.05, float(lh[i]))
            lambda_a = max(0.05, float(la[i]))

            fc = self.build_forecast_output(
                vector=vec,
                p_home=p_home,
                p_draw=p_draw,
                p_away=p_away,
                p_btts_yes=p_btts_yes,
                lambda_h=lambda_h,
                lambda_a=lambda_a,
                max_goals=self.max_goals,
            )
            fcs.append(fc)
        return fcs

    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        X_test = self.processor.transform([vector])

        # 1X2 probabilities
        classes_1x2_num = list(self.clf_1x2.classes_)
        classes_1x2_str = self.label_encoder_1x2.inverse_transform(classes_1x2_num)
        probs_1x2_raw = self.clf_1x2.predict_proba(X_test)[0]
        prob_map_1x2 = {str(c): float(p) for c, p in zip(classes_1x2_str, probs_1x2_raw)}

        p_home = prob_map_1x2.get("H", 0.33)
        p_draw = prob_map_1x2.get("D", 0.33)
        p_away = prob_map_1x2.get("A", 0.33)

        # BTTS
        classes_btts = list(self.clf_btts.classes_)
        probs_btts_raw = self.clf_btts.predict_proba(X_test)[0]
        prob_map_btts = {int(c): float(p) for c, p in zip(classes_btts, probs_btts_raw)}
        p_btts_yes = prob_map_btts.get(1, 0.5)

        # Expected Goals
        lambda_h = max(0.05, float(self.reg_home_goals.predict(X_test)[0]))
        lambda_a = max(0.05, float(self.reg_away_goals.predict(X_test)[0]))

        return self.build_forecast_output(
            vector=vector,
            p_home=p_home,
            p_draw=p_draw,
            p_away=p_away,
            p_btts_yes=p_btts_yes,
            lambda_h=lambda_h,
            lambda_a=lambda_a,
            max_goals=self.max_goals,
        )
