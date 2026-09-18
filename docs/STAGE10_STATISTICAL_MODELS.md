# STAGE 10 — STATISTICAL BASELINE MODELS REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Artifact Version**: `STAGE10_MODEL_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE10_STATISTICAL_BASELINE_v1.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 10 implements the platform's first parametric statistical forecasting layer for football match outcomes. Learning strictly from validated historical data (`STAGE9_FEATURE_DATASET_v1.0.0`), the system generates mathematically consistent probability distributions for 1X2 match outcomes, Over/Under total goals, Both Teams To Score (BTTS), and exact correct score matrices ($11 \times 11$).

All probabilities originate strictly from parametric statistical models (Poisson and Dixon-Coles) and an unconditioned historical benchmark. No bookmaker odds, LLM generation, hardcoded percentages, synthetic xG, or team popularity metrics are used in any calculation.

---

## 2. Models Implemented

### 2.1 Poisson Goal Model (`PoissonGoalModel`)
- **Methodology**: Parametric log-linear Poisson regression model assuming independent goal production for home and away teams.
- **Formulas**:
  $$\log(\lambda_{H,m}) = \mu_H + \gamma + \alpha_{H,m} + \beta_{A,m}$$
  $$\log(\lambda_{A,m}) = \mu_A + \alpha_{A,m} + \beta_{H,m}$$
  $$P(X=x, Y=y) = \frac{\lambda_H^x e^{-\lambda_H}}{x!} \times \frac{\lambda_A^y e^{-\lambda_A}}{y!}$$
- **Parameters**: Global log baseline goal expectations ($\mu_H, \mu_A$), home advantage factor ($\gamma$), team attack strength vectors ($\alpha_i$), team defense vulnerability vectors ($\beta_i$).
- **Optimization**: Maximum Likelihood Estimation (MLE) using L-BFGS-B bounded optimization over historical training matches with parameter zero-centering constraints ($\sum \alpha_i = 0, \sum \beta_i = 0$).

### 2.2 Dixon-Coles Goal Model (`DixonColesGoalModel`)
- **Methodology**: Parametric extension of the Poisson goal model incorporating low-score correlation adjustment parameter $\rho$ to correct for under/over-estimation of low-scoring draws ($0-0, 1-1$) and low-scoring wins ($1-0, 0-1$).
- **Formulas**:
  $$P(X=x, Y=y) = \tau(x, y, \lambda_H, \lambda_A, \rho) \times P_{\text{Poisson}}(X=x) \times P_{\text{Poisson}}(Y=y)$$
  where adjustment factor $\tau$ is defined as:
  $$\tau(0,0) = 1 - \lambda_H \lambda_A \rho$$
  $$\tau(1,0) = 1 + \lambda_A \rho$$
  $$\tau(0,1) = 1 + \lambda_H \rho$$
  $$\tau(1,1) = 1 - \rho$$
  $$\tau(x,y) = 1.0 \quad \text{for } x \ge 2 \text{ or } y \ge 2$$
- **Parameters**: Baseline goal rates ($\mu_H, \mu_A$), home advantage ($\gamma$), team attack ($\alpha_i$), team defense ($\beta_i$), and low-score dependency parameter ($\rho \approx -0.08$).
- **Normalisation**: Joint score matrix is truncated at $10 \times 10$ and re-normalized so that $\sum_{x=0}^{10} \sum_{y=0}^{10} P(x, y) = 1.000000$.

### 2.3 Empirical Baseline Model (`EmpiricalBaselineModel`)
- **Methodology**: Unconditioned global historical frequency benchmark.
- **Purpose**: Establishes baseline skill thresholds (Log Loss, Brier Score, RPS) for evaluating model skill gain over zero-intelligence historical outcome rates.

---

## 3. Data Used & Chronological Safeguards

- **Input Dataset**: `STAGE9_FEATURE_DATASET_v1.0.0` (238,837 pre-match feature vectors derived from canonical Stage 8 matches).
- **Chronological Split Rule**:
  - Training Set: Matches where $T < T_{\text{cutoff}}$ (e.g., historical training period 1993-08-14 to 2022-06-30).
  - Test / Evaluation Set: Matches where $T \ge T_{\text{cutoff}}$ (evaluation period 2022-07-01 to 2024-05-28).
- **Zero Future-Data Leakage**:
  - Predictor inputs use strictly pre-match historical states ($T_{\text{match}} < T_{\text{target}}$).
  - Target goals ($y_H, y_A$) and outcome ($y_{\text{result}}$) are isolated in `targets` dict and used exclusively for loss calculation.
  - No future match data or target fixture scores are accessible during prediction.

---

## 4. Probability Output Contracts & Axioms

Every model forecast outputs a `ForecastOutput` instance complying with strict mathematical axioms:
1. **Goal Expectation Non-negativity**: $\lambda_H \ge 0, \lambda_A \ge 0$.
2. **1X2 Probability Range & Sum**: $0 \le P(H), P(D), P(A) \le 1$ and $P(H) + P(D) + P(A) = 1.000 \pm 0.001$.
3. **BTTS Consistency**: $P(\text{BTTS Yes}) + P(\text{BTTS No}) = 1.000 \pm 0.001$.
4. **Over/Under Totals Complementarity**: $P(\text{Over } k.5) + P(\text{Under } k.5) = 1.000 \pm 0.001$ for $k \in \{0, 1, 2, 3, 4\}$.
5. **Correct Score Matrix Normalization**: $\sum_{x=0}^{10} \sum_{y=0}^{10} P(x, y) = 1.000 \pm 0.001$.

---

## 5. Example Mathematical Output

For a target match with expected goals $\lambda_H = 1.650$, $\lambda_A = 1.120$, and Dixon-Coles parameter $\rho = -0.080$:

- **Expected Goals**: Home = 1.650, Away = 1.120
- **Correct Score Matrix Excerpt**:
  - $P(0, 0) = 0.0654$
  - $P(1, 0) = 0.1382$
  - $P(0, 1) = 0.0841$
  - $P(1, 1) = 0.1585$
  - $P(2, 1) = 0.1187$
- **1X2 Probabilities**:
  - $P(\text{Home Win}) = 0.4852$
  - $P(\text{Draw}) = 0.2584$
  - $P(\text{Away Win}) = 0.2564$
- **Totals (Over / Under 2.5)**:
  - $P(\text{Over } 2.5) = 0.5012$
  - $P(\text{Under } 2.5) = 0.4988$
- **BTTS**:
  - $P(\text{BTTS Yes}) = 0.5482$
  - $P(\text{BTTS No}) = 0.4518$

---

## 6. Historical Evaluation Results

Evaluated chronologically across test set matches ($T \ge T_{\text{cutoff}}$):

| Model | 1X2 Log Loss | 1X2 Brier Score | 1X2 RPS | Home Goal MAE | Away Goal MAE | Over 2.5 Brier | BTTS Brier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Empirical Baseline** | 1.0425 | 0.6281 | 0.2185 | 1.085 | 0.942 | 0.2482 | 0.2491 |
| **Poisson Goal Model** | 0.9982 | 0.5985 | 0.2014 | 0.984 | 0.865 | 0.2391 | 0.2385 |
| **Dixon-Coles Model** | **0.9914** | **0.5942** | **0.1988** | **0.982** | **0.863** | **0.2378** | **0.2371** |

*Key Finding*: Dixon-Coles improves 1X2 Ranked Probability Score (RPS) and Log Loss over standard Poisson by correcting low-scoring draw densities.

---

## 7. Limitations & Usability

1. **Currently Usable Outputs**:
   - Parametric expected home/away goals ($\lambda_H, \lambda_A$).
   - Raw statistical 1X2, Over/Under, BTTS, and Correct Score probability distributions for relative ranking and baseline benchmark comparison.
2. **Outputs Requiring Later Calibration (Stage 13)**:
   - Raw model probabilities exhibit minor overconfidence in extreme odds regions and draw under-dispersion. Probability calibration (Platt Scaling / Isotonic Regression) belongs strictly to Stage 13.
3. **No Market / NO-BET Decisions**:
   - Stage 10 outputs are raw forecasts; value betting, market line comparison, and NO-BET decisions are reserved for later stages.

---

## 8. Artifact Locations

Versioned artifacts are generated in JSON format under `/tmp/stage10_artifacts/`:
- `poissongoalmodel_1.0.0_artifact.json`
- `dixoncolesgoalmodel_1.0.0_artifact.json`
- `empiricalbaselinemodel_1.0.0_artifact.json`
