STAGE:
Stage 12 — Time-Aware Historical Backtesting

STATUS:
COMPLETE

OBJECTIVE:
To evaluate the historical predictive accuracy and out-of-sample stability of all Stage 10 parametric statistical models (`PoissonGoalModel`, `DixonColesGoalModel`, `EmpiricalBaselineModel`) and Stage 11 supervised ML models (`LogisticRegressionForecaster`, `RandomForestForecaster`, `XGBoostForecaster`) across 4 chronological expanding walk-forward windows without future-data leakage or temporal feature contamination.

WINDOW RESULTS:
* **WINDOW_1_2020_2021**:
  * Train: `1888-09-08` to `2020-06-30` (171,911 matches, Max train date: `2020-06-30`)
  * Test:  `2020-07-01` to `2021-06-30` (12,660 matches, Min test date: `2020-07-01`)
  * 1X2 Log Loss: Empirical=1.08452 | Poisson=1.05171 | Dixon-Coles=1.05155 | LogisticReg=1.04504 | RandomForest=1.04956 | XGBoost=1.04437
* **WINDOW_2_2021_2022**:
  * Train: `1888-09-08` to `2021-06-30` (184,571 matches, Max train date: `2021-06-30`)
  * Test:  `2021-07-01` to `2022-06-30` (12,696 matches, Min test date: `2021-07-01`)
  * 1X2 Log Loss: Empirical=1.07685 | Poisson=1.04141 | Dixon-Coles=1.04107 | LogisticReg=1.03642 | RandomForest=1.04290 | XGBoost=1.03715
* **WINDOW_3_2022_2023**:
  * Train: `1888-09-08` to `2022-06-30` (197,267 matches, Max train date: `2022-06-30`)
  * Test:  `2022-07-01` to `2023-06-30` (12,367 matches, Min test date: `2022-07-01`)
  * 1X2 Log Loss: Empirical=1.07183 | Poisson=1.03800 | Dixon-Coles=1.03757 | LogisticReg=1.02927 | RandomForest=1.03422 | XGBoost=1.03002
* **WINDOW_4_2023_2024**:
  * Train: `1888-09-08` to `2023-06-30` (209,634 matches, Max train date: `2023-06-30`)
  * Test:  `2023-07-01` to `2024-05-28` (29,203 matches, Min test date: `2023-07-01`)
  * 1X2 Log Loss: Empirical=1.07578 | Poisson=1.04402 | Dixon-Coles=1.04315 | LogisticReg=1.03029 | RandomForest=1.03738 | XGBoost=1.03111

AGGREGATED RESULTS:
Pooled evaluation across all 66,926 out-of-sample test matches:
* **Logistic Regression**: 1X2 Log Loss=1.03406 | Brier=0.62128 | RPS=0.21429 | Home Goal MAE=0.969 | Away Goal MAE=0.853 | Over 2.5 Brier=0.24722 | BTTS Brier=0.24885
* **XGBoost Forecaster**: 1X2 Log Loss=1.03456 | Brier=0.62159 | RPS=0.21451 | Home Goal MAE=0.974 | Away Goal MAE=0.846 | Over 2.5 Brier=0.24705 | BTTS Brier=0.24865
* **Random Forest**: 1X2 Log Loss=1.04015 | Brier=0.62543 | RPS=0.21630 | Home Goal MAE=0.974 | Away Goal MAE=0.847 | Over 2.5 Brier=0.24752 | BTTS Brier=0.24887
* **Dixon-Coles Goal Model**: 1X2 Log Loss=1.04331 | Brier=0.62751 | RPS=0.21732 | Home Goal MAE=0.977 | Away Goal MAE=0.859 | Over 2.5 Brier=0.24871 | BTTS Brier=0.24973
* **Poisson Goal Model**: 1X2 Log Loss=1.04387 | Brier=0.62792 | RPS=0.21742 | Home Goal MAE=0.977 | Away Goal MAE=0.859 | Over 2.5 Brier=0.24888 | BTTS Brier=0.24997
* **Empirical Baseline**: 1X2 Log Loss=1.07691 | Brier=0.65178 | RPS=0.22903 | Home Goal MAE=1.024 | Away Goal MAE=0.869 | Over 2.5 Brier=0.25019 | BTTS Brier=0.24945

MODELS:
1. `EmpiricalBaselineModel` (Stage 10 parametric frequency baseline)
2. `PoissonGoalModel` (Stage 10 independent Poisson MLE model)
3. `DixonColesGoalModel` (Stage 10 Dixon-Coles low-score dependency MLE model)
4. `LogisticRegressionForecaster` (Stage 11 supervised multinomial/binary logistic model)
5. `RandomForestForecaster` (Stage 11 non-linear ensemble forecaster)
6. `XGBoostForecaster` (Stage 11 gradient boosted decision trees forecaster)

LEAKAGE CHECK:
- Zero temporal leakage verified ($T_{\text{train\_max}} \le T_{\text{test\_min}}$ for all windows).
- Imputers (`SimpleImputer`) fitted strictly on $X_{\text{train}}$ for each window.
- Excluded target variables, odds, synthetic xG, and post-match cluster labels from feature matrices.

TESTS:
- `services/ml/tests/test_stage12_backtesting.py`: 8 tests passed (including guard tests for metric reuse, leakage detection, window assignment, and pooled aggregation).
- `services/ml/tests/`: All 39 ML test module tests passed.
- `tests/`: All 52 platform architecture test cases passed.

FILES CREATED:
- `scripts/run_stage12_backtest.py`
- `stage12handoff.md`
- `/tmp/stage12_artifacts/stage12_backtest_report.json`

FILES MODIFIED:
- `docs/STAGE12_TIME_AWARE_BACKTESTING.md`
- `services/ml/app/models/poisson.py`
- `services/ml/app/models/dixon_coles.py`
- `services/ml/app/models/ml_base.py`
- `services/ml/app/models/logistic_regression.py`
- `services/ml/app/models/random_forest.py`
- `services/ml/app/models/xgboost_model.py`
- `services/ml/tests/test_stage12_backtesting.py`

BACKTEST ARTIFACT:
`/tmp/stage12_artifacts/stage12_backtest_report.json` (`STAGE12_BACKTEST_ARTIFACT_v1.0.0`)

LIMITATIONS:
- Uncalibrated raw probabilities (Probability calibration strictly belongs to Stage 13).
- Model ensembling and production model selection are deferred to Stage 13.
- Betting market lines, odds margin removal, and NO-BET decision logic belong to downstream stages.

BLOCKERS:
NONE

STAGE BOUNDARY:
Confirmed Stage 13+ (Probability Calibration & Ensembling) was NOT implemented.

NEXT:
Stage 13 — Probability Calibration + Model Selection
