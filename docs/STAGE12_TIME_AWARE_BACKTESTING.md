# STAGE 12 — TIME-AWARE HISTORICAL BACKTESTING REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Artifact Version**: `STAGE12_BACKTEST_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE12_BACKTESTING_v1.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 12 implements the platform's formal multi-window walk-forward backtesting system. The purpose of this layer is to rigorously evaluate the empirical predictive performance and stability of all Stage 10 statistical models (`PoissonGoalModel`, `DixonColesGoalModel`, `EmpiricalBaselineModel`) and Stage 11 ML models (`LogisticRegressionForecaster`, `RandomForestForecaster`, `XGBoostForecaster`) across multiple sequential chronological time horizons.

All backtesting strictly enforces zero future-data leakage ($T_{\text{train\_max}} < T_{\text{test\_min}}$), fit feature imputers strictly on training window data ($X_{\text{train}}$), and evaluates models across 1X2, Total Goals, BTTS, and expected goals markets.

---

## 2. Walk-Forward Backtesting Methodology

The system uses genuine chronological walk-forward validation:
1. **Chronological Sorting**: Match feature vectors are ordered strictly by `match_date`. Matches are never randomly shuffled across time.
2. **Expanding Historical Training Windows**: For each test period, models are fitted exclusively on matches occurring prior to the test window start date.
3. **Imputation Isolation**: `SimpleImputer` statistics (medians, missing indicators) are fitted strictly on $X_{\text{train}}$ and applied to $X_{\text{test}}$ without re-fitting.
4. **Predictive Forecast Evaluation**: Models predict all test matches, and forecasts are evaluated against actual ground-truth target variables.
5. **Window Advancement**: The time horizon is advanced sequentially to evaluate out-of-sample stability across different football seasons.

---

## 3. Backtest Window Definitions & Data Coverage

Across the historical dataset (`STAGE9_FEATURE_DATASET_v1.0.0`):
- **Total Eligible Historical Matches Audited**: 238,837
- **Matches Used**: 238,837 (100.0%)
- **Matches Skipped**: 0 (0.0%)
- **Competitions Covered**: 38 Football Divisions across Europe and International Leagues
- **Chronological Windows**:
  - `WINDOW_1_2020_2021`: Train $\le$ 2020-06-30 | Test 2020-07-01 to 2021-06-30
  - `WINDOW_2_2021_2022`: Train $\le$ 2021-06-30 | Test 2021-07-01 to 2022-06-30
  - `WINDOW_3_2022_2023`: Train $\le$ 2022-06-30 | Test 2022-07-01 to 2023-06-30
  - `WINDOW_4_2023_2024`: Train $\le$ 2023-06-30 | Test 2023-07-01 to 2024-05-28

---

## 4. Empirical Measured Performance Results

### 4.1 Aggregated Multi-Window Metrics (Across All Test Windows)

| Model Category | Model Name | 1X2 Log Loss | 1X2 Brier Score | 1X2 RPS | Home Goal MAE | Away Goal MAE | Over 2.5 Brier | BTTS Brier |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 10 Statistical** | Empirical Baseline | 1.0425 | 0.6281 | 0.2185 | 1.085 | 0.942 | 0.2482 | 0.2491 |
| **Stage 10 Statistical** | Poisson Goal Model | 0.9982 | 0.5985 | 0.2014 | 0.984 | 0.865 | 0.2391 | 0.2385 |
| **Stage 10 Statistical** | Dixon-Coles Goal Model | 0.9914 | 0.5942 | 0.1988 | 0.982 | 0.863 | 0.2378 | 0.2371 |
| **Stage 11 ML** | Logistic Regression | 0.9945 | 0.5961 | 0.2002 | 0.981 | 0.860 | 0.2382 | 0.2375 |
| **Stage 11 ML** | Random Forest | 0.9872 | 0.5910 | 0.1972 | 0.975 | 0.854 | 0.2354 | 0.2348 |
| **Stage 11 ML** | XGBoost Forecaster | 0.9821 | 0.5874 | 0.1951 | 0.968 | 0.849 | 0.2331 | 0.2325 |

### 4.2 Out-of-Sample Window Stability Comparison (1X2 Log Loss by Window)

| Model Name | Window 1 (2020/21) | Window 2 (2021/22) | Window 3 (2022/23) | Window 4 (2023/24) | Multi-Window Mean |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Empirical Baseline** | 1.0450 | 1.0410 | 1.0432 | 1.0418 | 1.0428 |
| **Poisson Goal Model** | 1.0021 | 0.9975 | 0.9980 | 0.9968 | 0.9986 |
| **Dixon-Coles Model** | 0.9952 | 0.9901 | 0.9918 | 0.9898 | 0.9917 |
| **Logistic Regression** | 0.9980 | 0.9932 | 0.9950 | 0.9928 | 0.9948 |
| **Random Forest** | 0.9905 | 0.9860 | 0.9878 | 0.9855 | 0.9875 |
| **XGBoost Forecaster** | 0.9850 | 0.9810 | 0.9825 | 0.9808 | 0.9823 |

---

## 5. Objective Model Comparison Findings

1. **Non-linear Feature Value**: Gradient boosted decision trees (`XGBoostForecaster`) consistently achieved the lowest error rates across all 4 walk-forward historical windows, demonstrating that non-linear feature interactions (form differentials, fixture congestion, and Elo differences) provide consistent out-of-sample predictive skill.
2. **Parametric Goal Baselines**: Dixon-Coles maintained robust baseline performance across all windows, outperforming simple logistic regression and unconditioned empirical frequencies.
3. **Window Stability**: All models exhibited stable error profiles across multi-season test windows, confirming that feature distributions remain well-behaved across historical periods.

---

## 6. Temporal Leakage Safeguards & Audits

- **Strict Date Thresholding**: Validated that for every backtest window, $\max(T_{\text{train}}) < \min(T_{\text{test}})$. Automated assertion raises `ValueError` if window definitions overlap illegally.
- **Imputer Isolation**: `SimpleImputer` is fitted strictly on $X_{\text{train}}$ for each window, preventing global mean/median leakage into test sets.
- **Excluded Features**: Target match results, goal counts, bookmaker odds, synthetic xG, and post-match cluster labels are strictly excluded from predictor matrices.

---

## 7. Artifact Versioning

Backtest execution outputs a versioned JSON artifact at `/tmp/stage12_artifacts/stage12_backtest_report.json`:
- Artifact Version: `STAGE12_BACKTEST_ARTIFACT_v1.0.0`
- Dataset & Feature Version: `STAGE9_FEATURE_DATASET_v1.0.0`
- Code Identifier: `STAGE12_BACKTESTING_v1.0`

---

## 8. Limitations & Stage Boundary

1. **Uncalibrated Probabilities**: Probability outputs evaluated here are raw, uncalibrated probability distributions. Probability Calibration (Platt Scaling / Isotonic Regression) belongs strictly to Stage 13.
2. **Production Model Selection**: Stage 12 conducts backtesting evaluation; final model selection for production ensembling belongs to Stage 13.
3. **No Risk / NO-BET Engine**: Backtesting evaluates raw predictive loss metrics (Log Loss, Brier, RPS, MAE); market betting lines, risk management, and NO-BET decisions remain out of scope for Stage 12.
