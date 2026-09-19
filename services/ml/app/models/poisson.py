"""
Poisson Goal Model Implementation

Independent Poisson goal forecasting model.
Estimates expected home goals (lambda_H) and expected away goals (lambda_A)
via team attack/defense parameters and home advantage fit on historical pre-match data.
Calculates mathematically valid 1X2, BTTS, Over/Under totals, and correct score matrices.
"""

import math
from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import minimize

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import BaseStatisticalModel, ForecastOutput


class PoissonGoalModel(BaseStatisticalModel):
    """
    Parametric Independent Poisson Goal Model for Football Match Forecasting.
    """

    def __init__(self, max_goals: int = 10):
        super().__init__(model_name="PoissonGoalModel", model_version="1.0.0")
        self.max_goals = max_goals
        self.team_indices: Dict[str, int] = {}
        self.teams_list: List[str] = []
        self.team_attack: Dict[str, float] = {}
        self.team_defense: Dict[str, float] = {}
        self.mu_home: float = 1.50
        self.mu_away: float = 1.10
        self.home_advantage: float = 0.25

    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        """
        Fits Poisson team attack, defense, and home advantage parameters using Maximum Likelihood Estimation (MLE).
        """
        if not training_vectors:
            self.is_fitted = True
            return

        # Build list of unique teams
        teams = set()
        valid_vectors = []
        for vec in training_vectors:
            h = vec.home_club_id
            a = vec.away_club_id
            h_g = vec.targets.get("full_time_home_goals")
            a_g = vec.targets.get("full_time_away_goals")
            if h and a and h_g is not None and a_g is not None:
                teams.add(h)
                teams.add(a)
                valid_vectors.append(vec)

        if not valid_vectors or not teams:
            self.is_fitted = True
            return

        self.teams_list = sorted(list(teams))
        self.team_indices = {t: i for i, t in enumerate(self.teams_list)}
        n_teams = len(self.teams_list)

        # Baseline average goal rates
        total_home_goals = sum(v.targets["full_time_home_goals"] for v in valid_vectors)
        total_away_goals = sum(v.targets["full_time_away_goals"] for v in valid_vectors)
        n_matches = len(valid_vectors)

        self.mu_home = max(0.5, total_home_goals / n_matches)
        self.mu_away = max(0.5, total_away_goals / n_matches)
        self.home_advantage = math.log(self.mu_home / self.mu_away) if self.mu_away > 0 else 0.25

        # Initialize parameters: [home_adv, att_0..att_N-1, def_0..def_N-1]
        # Constraint: sum(att) = 0, sum(def) = 0
        init_params = np.zeros(1 + 2 * n_teams)
        init_params[0] = self.home_advantage

        # Vectorized data arrays for fast optimization
        home_indices = np.array([self.team_indices[v.home_club_id] for v in valid_vectors], dtype=int)
        away_indices = np.array([self.team_indices[v.away_club_id] for v in valid_vectors], dtype=int)
        home_goals = np.array([v.targets["full_time_home_goals"] for v in valid_vectors], dtype=float)
        away_goals = np.array([v.targets["full_time_away_goals"] for v in valid_vectors], dtype=float)

        log_mu_h = math.log(self.mu_home)
        log_mu_a = math.log(self.mu_away)

        def _neg_log_likelihood_and_grad(params: np.ndarray):
            gamma = params[0]
            att = params[1 : 1 + n_teams]
            deff = params[1 + n_teams :]

            sum_att = np.sum(att)
            sum_def = np.sum(deff)
            penalty = 100.0 * (sum_att**2 + sum_def**2)

            log_lambda_h = log_mu_h + gamma + att[home_indices] + deff[away_indices]
            log_lambda_a = log_mu_a + att[away_indices] + deff[home_indices]

            lambda_h = np.exp(np.clip(log_lambda_h, -5.0, 3.0))
            lambda_a = np.exp(np.clip(log_lambda_a, -5.0, 3.0))

            ll_h = home_goals * np.log(lambda_h) - lambda_h
            ll_a = away_goals * np.log(lambda_a) - lambda_a

            loss = -np.sum(ll_h + ll_a) + penalty

            e_h = lambda_h - home_goals
            e_a = lambda_a - away_goals

            grad_gamma = np.sum(e_h)
            grad_att = np.bincount(home_indices, weights=e_h, minlength=n_teams) + \
                       np.bincount(away_indices, weights=e_a, minlength=n_teams) + \
                       200.0 * sum_att
            grad_def = np.bincount(away_indices, weights=e_h, minlength=n_teams) + \
                       np.bincount(home_indices, weights=e_a, minlength=n_teams) + \
                       200.0 * sum_def

            grad = np.concatenate([[grad_gamma], grad_att, grad_def])
            return loss, grad

        res = minimize(_neg_log_likelihood_and_grad, init_params, jac=True, method="L-BFGS-B", options={"maxiter": 150})

        if res.success or res.x is not None:
            opt_params = res.x
            self.home_advantage = float(opt_params[0])
            att_opt = opt_params[1 : 1 + n_teams]
            def_opt = opt_params[1 + n_teams :]

            # Zero-center parameters
            att_opt -= np.mean(att_opt)
            def_opt -= np.mean(def_opt)

            for i, t in enumerate(self.teams_list):
                self.team_attack[t] = float(att_opt[i])
                self.team_defense[t] = float(def_opt[i])

        self.is_fitted = True

    def predict_expected_goals(self, home_club_id: str, away_club_id: str) -> Tuple[float, float, str]:
        """
        Computes pre-match expected goals (lambda_H, lambda_A).
        """
        h_att = self.team_attack.get(home_club_id)
        h_def = self.team_defense.get(home_club_id)
        a_att = self.team_attack.get(away_club_id)
        a_def = self.team_defense.get(away_club_id)

        status = "FULL_EVIDENCE"
        if h_att is None or h_def is None or a_att is None or a_def is None:
            status = "LEAGUE_BASELINE_FALLBACK"
            h_att = h_att if h_att is not None else 0.0
            h_def = h_def if h_def is not None else 0.0
            a_att = a_att if a_att is not None else 0.0
            a_def = a_def if a_def is not None else 0.0

        log_lambda_h = math.log(self.mu_home) + self.home_advantage + h_att + a_def
        log_lambda_a = math.log(self.mu_away) + a_att + h_def

        lambda_h = max(0.05, math.exp(min(2.5, max(-3.0, log_lambda_h))))
        lambda_a = max(0.05, math.exp(min(2.5, max(-3.0, log_lambda_a))))

        return lambda_h, lambda_a, status

    def calculate_joint_score_matrix(self, lambda_h: float, lambda_a: float) -> np.ndarray:
        """
        Computes Independent Poisson joint probability matrix up to max_goals x max_goals.
        """
        h_p = np.array([self._poisson_pmf(k, lambda_h) for k in range(self.max_goals + 1)])
        a_p = np.array([self._poisson_pmf(k, lambda_a) for k in range(self.max_goals + 1)])

        # Outer product for independent Poisson
        matrix = np.outer(h_p, a_p)

        # Normalize matrix so sum = 1.0
        total_p = np.sum(matrix)
        if total_p > 0:
            matrix /= total_p

        return matrix

    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        lambda_h, lambda_a, status = self.predict_expected_goals(
            vector.home_club_id, vector.away_club_id
        )

        matrix = self.calculate_joint_score_matrix(lambda_h, lambda_a)

        # Derive outcome probabilities
        p_home = float(np.sum(np.tril(matrix, -1)))
        p_draw = float(np.sum(np.diag(matrix)))
        p_away = float(np.sum(np.triu(matrix, 1)))

        # Totals probabilities
        totals = {}
        for threshold, val in [("0_5", 0.5), ("1_5", 1.5), ("2_5", 2.5), ("3_5", 3.5), ("4_5", 4.5)]:
            k = int(math.floor(val))
            # Sum where h_g + a_g > k
            grid_h, grid_a = np.indices(matrix.shape)
            over_p = float(np.sum(matrix[grid_h + grid_a > k]))
            under_p = 1.0 - over_p
            totals[f"over_{threshold}"] = over_p
            totals[f"under_{threshold}"] = max(0.0, under_p)

        # BTTS probabilities
        btts_yes = float(np.sum(matrix[1:, 1:]))
        btts_no = max(0.0, 1.0 - btts_yes)
        btts = {"btts_yes": btts_yes, "btts_no": btts_no}

        # Format score matrix dict
        score_matrix_dict = {}
        for h_g in range(self.max_goals + 1):
            score_matrix_dict[h_g] = {}
            for a_g in range(self.max_goals + 1):
                score_matrix_dict[h_g][a_g] = float(matrix[h_g, a_g])

        output = ForecastOutput(
            fixture_id=vector.fixture_id,
            match_date=vector.match_date,
            model_name=self.model_name,
            model_version=self.model_version,
            expected_home_goals=lambda_h,
            expected_away_goals=lambda_a,
            probabilities_1x2={"home": p_home, "draw": p_draw, "away": p_away},
            probabilities_totals=totals,
            probabilities_btts=btts,
            correct_score_matrix=score_matrix_dict,
            data_quality_status=status,
        )

        val_errors = output.validate()
        if val_errors:
            raise ValueError(f"Poisson Forecast Output validation failed: {val_errors}")

        return output

    @staticmethod
    def _poisson_pmf(k: int, mu: float) -> float:
        return (mu**k) * math.exp(-mu) / math.factorial(k)
