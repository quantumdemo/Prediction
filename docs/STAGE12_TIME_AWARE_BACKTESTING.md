# STAGE 12 — TIME-AWARE HISTORICAL BACKTESTING REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Artifact Version**: `STAGE12_BACKTEST_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE12_BACKTESTING_v1.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 12 implements the platform's formal multi-window walk-forward backtesting system. The purpose of this layer is to rigorously evaluate the empirical predictive performance and stability of all Stage 10 statistical models (`PoissonGoalModel`, `DixonColesGoalModel`, `EmpiricalBaselineModel`) and Stage 11 ML models (`LogisticRegressionForecaster`, `RandomForestForecaster`, `XGBoostForecaster`) across multiple sequential chronological time horizons.

All backtesting strictly enforces zero future-data leakage ($T_{\text{train\_max}} < T_{\text{test\_min}}$), fits imputation transformers strictly on training window data ($X_{\text{train}}$), and evaluates models across 1X2, Total Goals, BTTS, and expected goals markets.

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
  - `WINDOW_1_2020_2021`: Train $\le$ 2020-06-30 (171,911 matches) | Test 2020-07-01 to 2021-06-30 (12,660 matches)
  - `WINDOW_2_2021_2022`: Train $\le$ 2021-06-30 (184,571 matches) | Test 2021-07-01 to 2022-06-30 (12,696 matches)
  - `WINDOW_3_2022_2023`: Train $\le$ 2022-06-30 (197,267 matches) | Test 2022-07-01 to 2023-06-30 (12,367 matches)
  - `WINDOW_4_2023_2024`: Train $\le$ 2023-06-30 (209,634 matches) | Test 2023-07-01 to 2024-05-28 (29,203 matches)

---

## 4. Empirical Measured Performance Results

### 4.1 Aggregated Multi-Window Metrics (Pooled Across 66,926 Test Matches)

| Model Category | Model Name | 1X2 Log Loss | 1X2 Brier Score | 1X2 RPS | Home Goal MAE | Away Goal MAE | Over 2.5 Brier | BTTS Brier |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 10 Statistical** | Empirical Baseline | 1.07691 | 0.65178 | 0.22903 | 1.024 | 0.869 | 0.25019 | 0.24945 |
| **Stage 10 Statistical** | Poisson Goal Model | 1.04387 | 0.62792 | 0.21742 | 0.977 | 0.859 | 0.24888 | 0.24997 |
| **Stage 10 Statistical** | Dixon-Coles Goal Model | 1.04331 | 0.62751 | 0.21732 | 0.977 | 0.859 | 0.24871 | 0.24973 |
| **Stage 11 ML** | Logistic Regression | 1.03406 | 0.62128 | 0.21429 | 0.969 | 0.853 | 0.24722 | 0.24885 |
| **Stage 11 ML** | Random Forest | 1.04015 | 0.62543 | 0.21630 | 0.974 | 0.847 | 0.24752 | 0.24887 |
| **Stage 11 ML** | XGBoost Forecaster | 1.03456 | 0.62159 | 0.21451 | 0.974 | 0.846 | 0.24705 | 0.24865 |

### 4.2 Out-of-Sample Window Stability Comparison (1X2 Log Loss by Window)

| Model Name | Window 1 (2020/21) | Window 2 (2021/22) | Window 3 (2022/23) | Window 4 (2023/24) | Pooled Multi-Window |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Empirical Baseline** | 1.08452 | 1.07685 | 1.07183 | 1.07578 | 1.07691 |
| **Poisson Goal Model** | 1.05171 | 1.04141 | 1.03800 | 1.04402 | 1.04387 |
| **Dixon-Coles Model** | 1.05155 | 1.04107 | 1.03757 | 1.04315 | 1.04331 |
| **Logistic Regression** | 1.04504 | 1.03642 | 1.02927 | 1.03029 | 1.03406 |
| **Random Forest** | 1.04956 | 1.04290 | 1.03422 | 1.03738 | 1.04015 |
| **XGBoost Forecaster** | 1.04437 | 1.03715 | 1.03002 | 1.03111 | 1.03456 |

---

## 5. Objective Model Comparison Findings

1. **Supervised ML Superiority**: Supervised ML models (`LogisticRegressionForecaster` and `XGBoostForecaster`) consistently achieved the lowest error rates (Log Loss ~1.034) across all 4 walk-forward historical windows, outperforming parametric goal models.
2. **Parametric Goal Baselines**: Dixon-Coles maintained robust baseline performance across all windows (Log Loss 1.04331), slightly outperforming independent Poisson (1.04387) due to low-score correlation adjustments.
3. **Window Stability**: All models exhibited stable error profiles across multi-season test windows, confirming feature distribution stability without temporal degradation.

---

## 6. Temporal Leakage Safeguards & Audits

- **Strict Date Thresholding**: Validated that for every backtest window, $\max(T_{\text{train}}) \le \min(T_{\text{test}})$. Automated assertion raises `ValueError` if window definitions overlap illegally.
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
