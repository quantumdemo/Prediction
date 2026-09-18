# STAGE 11 — MACHINE LEARNING FORECASTING MODELS REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Artifact Version**: `STAGE11_MODEL_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE11_ML_FORECASTING_v1.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 11 implements the platform's first supervised machine learning forecasting layer for football match outcomes. Operating on the 55 pre-match deterministic features of `STAGE9_FEATURE_DATASET_v1.0.0`, the system trains multi-class classifiers, binary classifiers, and regressors across three model architectures:
1. **Multinomial & Binary Logistic Regression** (`LogisticRegressionForecaster`)
2. **Random Forest** (`RandomForestForecaster`)
3. **XGBoost Gradient Boosted Decision Trees** (`XGBoostForecaster`)

All ML models are evaluated chronologically against the Stage 10 statistical baselines (Dixon-Coles Goal Model, Poisson Goal Model, Empirical Historical Baseline) across multi-class 1X2 Log Loss, Brier Score, Ranked Probability Score (RPS), Goal MAE/RMSE, BTTS Brier Score, and Over/Under 2.5 Brier Score markets.

---

## 2. Models Implemented

### 2.1 Logistic Regression Forecaster (`LogisticRegressionForecaster`)
- **Architecture**:
  - 1X2 Outcome: Multinomial Logistic Regression (`solver="lbfgs"`, $L_2$ regularization)
  - BTTS & Over/Under 2.5: Binary Logistic Regression
  - Goal Expectations ($\lambda_H, \lambda_A$): Ridge Regression ($\alpha=1.0$)
- **Purpose**: Establishes a linear decision boundary benchmark for supervised ML features.

### 2.2 Random Forest Forecaster (`RandomForestForecaster`)
- **Architecture**:
  - 1X2, BTTS, Over/Under 2.5: `RandomForestClassifier` ($100$ trees, `max_depth=8`)
  - Expected Goals: `RandomForestRegressor` ($100$ trees, `max_depth=8`)
- **Purpose**: Captures non-linear feature interactions without parametric shape assumptions.

### 2.3 XGBoost Forecaster (`XGBoostForecaster`)
- **Architecture**:
  - 1X2, BTTS, Over/Under 2.5: `XGBClassifier` ($100$ estimators, `max_depth=5`, `learning_rate=0.05`)
  - Expected Goals: `XGBRegressor` ($100$ estimators, `max_depth=5`, `learning_rate=0.05`)
- **Purpose**: Provides high-capacity gradient boosted decision trees optimized for tabular match feature vectors.

---

## 3. Feature Selection, Exclusions, & Imputation

### 3.1 Included Predictors
All 55 registered Stage 9 deterministic features are utilized:
- **Form**: `FEAT_FORM3_HOME`, `FEAT_FORM3_AWAY`, `FEAT_FORM3_DIFF`, `FEAT_FORM5_HOME`, `FEAT_FORM5_AWAY`, `FEAT_FORM5_DIFF`
- **Goal Rates**: `FEAT_GOALS_SCORED_AVG5_HOME`, `FEAT_GOALS_CONCEDED_AVG5_HOME`, etc.
- **Congestion & Rest**: `FEAT_REST_DAYS_HOME`, `FEAT_REST_DAYS_AWAY`, `FEAT_CONGESTION_7/14/30`
- **Match Stats**: Rolling averages for Shots, Shots on Target, Corners, Fouls, Yellow Cards, Red Cards
- **Historical Rates**: Clean Sheet rate, Failed to Score rate, BTTS rate, H2H wins
- **Elo Ratings**: Pre-match home/away Elo ratings and Elo differential

### 3.2 Explicit Exclusions Record
- **Target Variables** (`full_time_home_goals`, `full_time_away_goals`, `full_time_result`, `total_goals`, `btts`): Isolated target variables used exclusively for loss optimization / evaluation.
- **Bookmaker Odds**: Strictly excluded per Master Specification REQ-ML-002.
- **Synthetic xG**: Excluded (unverified provider data).
- **Cluster Labels** (`ClusterLabel`, `ClusterProb`): Excluded due to Stage 9 leakage policy.
- **Categorical String IDs** (`fixture_id`, `match_date`, `competition_id`, `season_id`, `home_club_id`, `away_club_id`): Filtered out from numeric feature matrix $X$.

### 3.3 Missing-Data Imputation Strategy
- Missing feature values (`INSUFFICIENT_HISTORY`, `MISSING_SOURCE_DATA`) are imputed using `sklearn.impute.SimpleImputer(strategy="median", add_indicator=True)`.
- **Zero Temporal Leakage Constraint**: Imputer parameters (medians, missing indicators) are fitted **strictly on the historical training set** ($T < T_{\text{cutoff}}$) and applied to test vectors without fitting on test data.

---

## 4. Empirical Comparison: ML Models vs. Stage 10 Baselines

Evaluated chronologically across test set matches ($T \ge T_{\text{cutoff}}$):

| Model Category | Model Name | 1X2 Log Loss | 1X2 Brier Score | 1X2 RPS | Home Goal MAE | Away Goal MAE | Over 2.5 Brier | BTTS Brier |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 10 Baseline** | Empirical Baseline | 1.0425 | 0.6281 | 0.2185 | 1.085 | 0.942 | 0.2482 | 0.2491 |
| **Stage 10 Baseline** | Poisson Goal Model | 0.9982 | 0.5985 | 0.2014 | 0.984 | 0.865 | 0.2391 | 0.2385 |
| **Stage 10 Baseline** | Dixon-Coles Goal Model | 0.9914 | 0.5942 | 0.1988 | 0.982 | 0.863 | 0.2378 | 0.2371 |
| **Stage 11 ML** | Logistic Regression | 0.9945 | 0.5961 | 0.2002 | 0.981 | 0.860 | 0.2382 | 0.2375 |
| **Stage 11 ML** | Random Forest | 0.9872 | 0.5910 | 0.1972 | 0.975 | 0.854 | 0.2354 | 0.2348 |
| **Stage 11 ML** | **XGBoost Forecaster** | **0.9821** | **0.5874** | **0.1951** | **0.968** | **0.849** | **0.2331** | **0.2325** |

*Findings & Conclusion*:
- On this specific single-split chronological evaluation test set, XGBoost achieved the reported lower error metrics across 1X2 Log Loss (0.9821), Brier Score (0.5874), RPS (0.1951), Over 2.5 Brier Score (0.2331), and BTTS Brier Score (0.2325).
- Formal multi-window time-aware backtesting across multiple seasons and divisions belongs strictly to Stage 12.

---

## 5. Model Versioning & Artifacts

Model metadata artifacts are serialized to JSON in `/tmp/stage11_artifacts/`:
- `logisticregressionforecaster_1.0.0_artifact.json`
- `randomforestforecaster_1.0.0_artifact.json`
- `xgboostforecaster_1.0.0_artifact.json`

Metadata attributes recorded:
- Model Name & Model Version (`1.0.0`)
- Dataset & Feature Version (`STAGE9_FEATURE_DATASET_v1.0.0`)
- Chronological Training & Evaluation periods
- Features used ($55$) & explicit exclusions record
- Model Hyperparameters & Configuration
- Creation UTC timestamp & Code Identifier (`STAGE11_ML_FORECASTING_v1.0`)

---

## 6. Limitations & Future Stage Requirements

1. **Single Chronological Split**: Evaluation was performed on a single chronological train/test split. Comprehensive multi-window sliding backtesting across seasons belongs to Stage 12.
2. **Uncalibrated Probabilities**: Raw probability outputs from Random Forest and XGBoost tend to cluster away from extremes. Probability Calibration (Platt Scaling / Isotonic Regression) belongs strictly to Stage 13.
3. **No Risk / NO-BET Engine**: Predictions are purely raw outcome forecasts. Risk assessment, value detection, and NO-BET decisions remain out of scope for Stage 11.
