"""
Dixon-Coles Goal Model Implementation

Parametric Dixon-Coles goal model.
Adjusts independent Poisson low-score probabilities (0-0, 1-0, 0-1, 1-1) using dependency parameter rho.
Ensures non-negative probabilities, score matrix re-normalization, and strict probability constraints.
"""

import math
from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import minimize

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.models.base import BaseStatisticalModel, ForecastOutput


class DixonColesGoalModel(BaseStatisticalModel):
    """
    Dixon-Coles Goal Model with Low-Score Correlation Adjustment.
    """

    def __init__(self, max_goals: int = 10):
        super().__init__(model_name="DixonColesGoalModel", model_version="1.0.0")
        self.max_goals = max_goals
        self.team_indices: Dict[str, int] = {}
        self.teams_list: List[str] = []
        self.team_attack: Dict[str, float] = {}
        self.team_defense: Dict[str, float] = {}
        self.mu_home: float = 1.50
        self.mu_away: float = 1.10
        self.home_advantage: float = 0.25
        self.rho: float = -0.08  # Default low-score dependence parameter

    def fit(self, training_vectors: List[MatchFeatureVector]) -> None:
        """
        Fits Dixon-Coles parameters (team attack/defense, home advantage, rho) using MLE.
        """
        if not training_vectors:
            self.is_fitted = True
            return

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

        total_home_goals = sum(v.targets["full_time_home_goals"] for v in valid_vectors)
        total_away_goals = sum(v.targets["full_time_away_goals"] for v in valid_vectors)
        n_matches = len(valid_vectors)

        self.mu_home = max(0.5, total_home_goals / n_matches)
        self.mu_away = max(0.5, total_away_goals / n_matches)
        self.home_advantage = math.log(self.mu_home / self.mu_away) if self.mu_away > 0 else 0.25

        # Initialize params: [home_adv, rho, att_0..att_N-1, def_0..def_N-1]
        init_params = np.zeros(2 + 2 * n_teams)
        init_params[0] = self.home_advantage
        init_params[1] = -0.05  # Initial rho

        home_indices = np.array([self.team_indices[v.home_club_id] for v in valid_vectors], dtype=int)
        away_indices = np.array([self.team_indices[v.away_club_id] for v in valid_vectors], dtype=int)
        home_goals = np.array([v.targets["full_time_home_goals"] for v in valid_vectors], dtype=float)
        away_goals = np.array([v.targets["full_time_away_goals"] for v in valid_vectors], dtype=float)

        log_mu_h = math.log(self.mu_home)
        log_mu_a = math.log(self.mu_away)

        def _dixon_coles_tau(x: float, y: float, lambda_h: float, lambda_a: float, rho: float) -> float:
            if x == 0 and y == 0:
                return max(0.001, 1.0 - lambda_h * lambda_a * rho)
            elif x == 1 and y == 0:
                return max(0.001, 1.0 + lambda_a * rho)
            elif x == 0 and y == 1:
                return max(0.001, 1.0 + lambda_h * rho)
            elif x == 1 and y == 1:
                return max(0.001, 1.0 - rho)
            return 1.0

        mask_00 = (home_goals == 0) & (away_goals == 0)
        mask_10 = (home_goals == 1) & (away_goals == 0)
        mask_01 = (home_goals == 0) & (away_goals == 1)
        mask_11 = (home_goals == 1) & (away_goals == 1)

        def _neg_log_likelihood_and_grad(params: np.ndarray):
            gamma = params[0]
            rho = np.clip(params[1], -0.25, 0.25)
            att = params[2 : 2 + n_teams]
            deff = params[2 + n_teams :]

            sum_att = np.sum(att)
            sum_def = np.sum(deff)
            penalty = 100.0 * (sum_att**2 + sum_def**2)

            log_lambda_h = log_mu_h + gamma + att[home_indices] + deff[away_indices]
            log_lambda_a = log_mu_a + att[away_indices] + deff[home_indices]

            lambda_h = np.exp(np.clip(log_lambda_h, -5.0, 3.0))
            lambda_a = np.exp(np.clip(log_lambda_a, -5.0, 3.0))

            ll_h = home_goals * np.log(lambda_h) - lambda_h
            ll_a = away_goals * np.log(lambda_a) - lambda_a

            tau_vals = np.ones(len(valid_vectors))
            dtau_dlh = np.zeros(len(valid_vectors))
            dtau_dla = np.zeros(len(valid_vectors))
            dtau_drho = np.zeros(len(valid_vectors))

            if np.any(mask_00):
                lh = lambda_h[mask_00]
                la = lambda_a[mask_00]
                denom = np.maximum(0.001, 1.0 - lh * la * rho)
                tau_vals[mask_00] = denom
                dtau_dlh[mask_00] = -la * rho / denom
                dtau_dla[mask_00] = -lh * rho / denom
                dtau_drho[mask_00] = -lh * la / denom

            if np.any(mask_10):
                la = lambda_a[mask_10]
                denom = np.maximum(0.001, 1.0 + la * rho)
                tau_vals[mask_10] = denom
                dtau_dla[mask_10] = rho / denom
                dtau_drho[mask_10] = la / denom

            if np.any(mask_01):
                lh = lambda_h[mask_01]
                denom = np.maximum(0.001, 1.0 + lh * rho)
                tau_vals[mask_01] = denom
                dtau_dlh[mask_01] = rho / denom
                dtau_drho[mask_01] = lh / denom

            if np.any(mask_11):
                denom = np.maximum(0.001, 1.0 - rho)
                tau_vals[mask_11] = denom
                dtau_drho[mask_11] = -1.0 / denom

            ll_tau = np.log(tau_vals)
            loss = -np.sum(ll_h + ll_a + ll_tau) + penalty

            e_h = lambda_h - home_goals - lambda_h * dtau_dlh
            e_a = lambda_a - away_goals - lambda_a * dtau_dla

            grad_gamma = np.sum(e_h)
            grad_rho = -np.sum(dtau_drho)
            grad_att = np.bincount(home_indices, weights=e_h, minlength=n_teams) + \
                       np.bincount(away_indices, weights=e_a, minlength=n_teams) + \
                       200.0 * sum_att
            grad_def = np.bincount(away_indices, weights=e_h, minlength=n_teams) + \
                       np.bincount(home_indices, weights=e_a, minlength=n_teams) + \
                       200.0 * sum_def

            grad = np.concatenate([[grad_gamma, grad_rho], grad_att, grad_def])
            return loss, grad

        res = minimize(_neg_log_likelihood_and_grad, init_params, jac=True, method="L-BFGS-B", options={"maxiter": 150})

        if res.success or res.x is not None:
            opt_params = res.x
            self.home_advantage = float(opt_params[0])
            self.rho = float(np.clip(opt_params[1], -0.25, 0.25))
            att_opt = opt_params[2 : 2 + n_teams]
            def_opt = opt_params[2 + n_teams :]

            att_opt -= np.mean(att_opt)
            def_opt -= np.mean(def_opt)

            for i, t in enumerate(self.teams_list):
                self.team_attack[t] = float(att_opt[i])
                self.team_defense[t] = float(def_opt[i])

        self.is_fitted = True

    def predict_expected_goals(self, home_club_id: str, away_club_id: str) -> Tuple[float, float, str]:
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

    def calculate_dixon_coles_score_matrix(self, lambda_h: float, lambda_a: float) -> np.ndarray:
        """
        Computes Dixon-Coles low-score adjusted joint probability matrix up to max_goals x max_goals.
        """
        h_p = np.array([self._poisson_pmf(k, lambda_h) for k in range(self.max_goals + 1)])
        a_p = np.array([self._poisson_pmf(k, lambda_a) for k in range(self.max_goals + 1)])

        matrix = np.outer(h_p, a_p)

        # Apply Dixon-Coles tau adjustment for low scores (0,0), (1,0), (0,1), (1,1)
        tau_00 = max(0.0, 1.0 - lambda_h * lambda_a * self.rho)
        tau_10 = max(0.0, 1.0 + lambda_a * self.rho)
        tau_01 = max(0.0, 1.0 + lambda_h * self.rho)
        tau_11 = max(0.0, 1.0 - self.rho)

        matrix[0, 0] *= tau_00
        matrix[1, 0] *= tau_10
        matrix[0, 1] *= tau_01
        matrix[1, 1] *= tau_11

        # Strict non-negativity check
        matrix = np.maximum(0.0, matrix)

        # Re-normalize matrix so total probability sum = 1.0
        total_p = np.sum(matrix)
        if total_p > 0:
            matrix /= total_p

        return matrix

    def predict_fixture(self, vector: MatchFeatureVector) -> ForecastOutput:
        lambda_h, lambda_a, status = self.predict_expected_goals(
            vector.home_club_id, vector.away_club_id
        )

        matrix = self.calculate_dixon_coles_score_matrix(lambda_h, lambda_a)

        # 1X2 probabilities
        p_home = float(np.sum(np.tril(matrix, -1)))
        p_draw = float(np.sum(np.diag(matrix)))
        p_away = float(np.sum(np.triu(matrix, 1)))

        # Totals probabilities
        totals = {}
        grid_h, grid_a = np.indices(matrix.shape)
        for threshold, val in [("0_5", 0.5), ("1_5", 1.5), ("2_5", 2.5), ("3_5", 3.5), ("4_5", 4.5)]:
            k = int(math.floor(val))
            over_p = float(np.sum(matrix[grid_h + grid_a > k]))
            under_p = 1.0 - over_p
            totals[f"over_{threshold}"] = over_p
            totals[f"under_{threshold}"] = max(0.0, under_p)

        # BTTS probabilities
        btts_yes = float(np.sum(matrix[1:, 1:]))
        btts_no = max(0.0, 1.0 - btts_yes)
        btts = {"btts_yes": btts_yes, "btts_no": btts_no}

        # Score matrix dict
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
            raise ValueError(f"Dixon-Coles Forecast Output validation failed: {val_errors}")

        return output

    @staticmethod
    def _poisson_pmf(k: int, mu: float) -> float:
        return (mu**k) * math.exp(-mu) / math.factorial(k)
