"""
Logistic Regression ML Forecaster Implementation

Supervised Logistic Regression forecaster for football match outcomes.
Fits multinomial logistic regression for 1X2, binary logistic regressions for BTTS and Over/Under 2.5,
and Ridge regression for goal expectations.
"""

from typing import List

from sklearn.linear_model import LogisticRegression, Ridge

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import ForecastOutput
from services.ml.app.models.ml_base import BaseMLForecaster


class LogisticRegressionForecaster(BaseMLForecaster):
    """
    Multinomial & Binary Logistic Regression Forecaster.
    """

    def __init__(self, max_goals: int = 10, n_jobs: int = -1):
        super().__init__(model_name="LogisticRegressionForecaster", model_version="1.0.0")
        self.max_goals = max_goals
        self.clf_1x2 = LogisticRegression(solver="lbfgs", max_iter=500, random_state=42, n_jobs=n_jobs)
        self.clf_btts = LogisticRegression(solver="lbfgs", max_iter=500, random_state=42, n_jobs=n_jobs)
        self.clf_over25 = LogisticRegression(solver="lbfgs", max_iter=500, random_state=42, n_jobs=n_jobs)
        self.reg_home_goals = Ridge(alpha=1.0, random_state=42)
        self.reg_away_goals = Ridge(alpha=1.0, random_state=42)

    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        if not training_vectors:
            self.is_fitted = True
            return

        X_train = self.processor.fit_transform(training_vectors)
        y_dict = self.processor.extract_targets(training_vectors)

        if X_train.shape[0] > 0:
            self.clf_1x2.fit(X_train, y_dict["1x2"])
            self.clf_btts.fit(X_train, y_dict["btts"])
            self.clf_over25.fit(X_train, y_dict["over25"])
            self.reg_home_goals.fit(X_train, y_dict["home_goals"])
            self.reg_away_goals.fit(X_train, y_dict["away_goals"])

        self.is_fitted = True

    def _predict_batch_vectorized(self, vectors: List[MatchFeatureVector]) -> List[ForecastOutput]:
        X_test = self.processor.transform(vectors)

        classes_1x2 = list(self.clf_1x2.classes_)
        probs_1x2 = self.clf_1x2.predict_proba(X_test)

        classes_btts = list(self.clf_btts.classes_)
        probs_btts = self.clf_btts.predict_proba(X_test)

        lh = self.reg_home_goals.predict(X_test)
        la = self.reg_away_goals.predict(X_test)

        fcs = []
        for i, vec in enumerate(vectors):
            p_map_1x2 = {c: float(p) for c, p in zip(classes_1x2, probs_1x2[i])}
            p_home = p_map_1x2.get("H", 0.33)
            p_draw = p_map_1x2.get("D", 0.33)
            p_away = p_map_1x2.get("A", 0.33)

            p_map_btts = {c: float(p) for c, p in zip(classes_btts, probs_btts[i])}
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
        classes_1x2 = list(self.clf_1x2.classes_)
        probs_1x2_raw = self.clf_1x2.predict_proba(X_test)[0]
        prob_map_1x2 = {c: float(p) for c, p in zip(classes_1x2, probs_1x2_raw)}
        p_home = prob_map_1x2.get("H", 0.33)
        p_draw = prob_map_1x2.get("D", 0.33)
        p_away = prob_map_1x2.get("A", 0.33)

        # BTTS
        classes_btts = list(self.clf_btts.classes_)
        probs_btts_raw = self.clf_btts.predict_proba(X_test)[0]
        prob_map_btts = {c: float(p) for c, p in zip(classes_btts, probs_btts_raw)}
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
