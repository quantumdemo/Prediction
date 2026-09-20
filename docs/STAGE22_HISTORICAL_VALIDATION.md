# Stage 22 — Historical Validation / Shadow Testing Specification & Documentation

## Overview
Stage 22 implements a controlled historical shadow-validation framework for the football AI platform. It evaluates the production prediction pipeline (`EndToEndPredictionPipeline`) and production forecaster (`xgboost_platt` calibrated via Stage 13 Platt Scaling) across historical football fixtures without temporal leakage, data contamination, or odds modeling.

## Model Provenance Audit & Model Selection Overlap
- **Training Period**: Windows 1–3 (`2020-07-01` to `2023-06-30`, 37,723 historical matches).
- **Calibration Fit Period**: Windows 1–3 (`2020-07-01` to `2023-06-30`).
- **Model Selection Period**: Window 4 (`2023-07-01` to `2024-05-28`, 29,203 matches used in Stage 13 candidate selection).
- **Stage 22 Evaluation Period**: `2023-07-01` to `2024-06-30` (12,140 eligible matches in historical dataset `STAGE9_FEATURE_DATASET_v1.0.0`).
- **Overlap**: Complete overlap exists between the Stage 13 model selection set (Window 4) and the Stage 22 historical evaluation period (`2023-07-01` to `2024-05-28`).
- **Unseen Out-Of-Sample Evaluation Verified**: NO (`is_unseen_out_of_sample = False`).
- **Statistical Interpretation**: `HISTORICAL_SELECTION_SET_REPLAY`. Reported metrics reflect selection-set replay performance and MUST NOT be presented as an unbiased out-of-sample performance estimate.

## Core Architectural Design & No-Leakage Guard
To guarantee zero outcome contamination, prediction inputs are strictly isolated from post-prediction evaluation outcomes.

1. **Prediction Input Isolation**: The prediction pipeline receives ONLY pre-match feature vectors ($T_{\text{retrieval}} \le T_{\text{cutoff}}$) and pre-match fixture metadata.
2. **Outcome Leakage Guard**: `OutcomeLeakageError` is raised if outcome variables (`full_time_result`, `full_time_home_goals`, `full_time_away_goals`, `total_goals`, `btts`) enter the prediction payload.
3. **Post-Prediction Evaluation**: Actual match outcomes are recorded separately in `ActualMatchOutcome` records after shadow predictions are generated.

## Evaluated Supported Markets
Shadow predictions are generated and evaluated for the 8 approved Stage 17 markets:
1. `MKT_MATCH_RESULT_1X2` (Home, Draw, Away)
2. `MKT_TOTAL_GOALS_OVER_UNDER` (Over / Under 0.5 to 4.5)
3. `MKT_BOTH_TEAMS_TO_SCORE` (BTTS Yes / No)
4. `MKT_CORRECT_SCORE_GRID` (0-3 x 0-3 Grid)

## Aggregate Replay Metrics & NO-BET Statistics
Aggregate performance is calculated strictly post-prediction over 12,140 evaluated shadow prediction records in `STAGE22_VALIDATION_ARTIFACT_v1.0.0`:
- **1X2 Log Loss**: 1.10003
- **1X2 Brier Score**: 0.66603
- **1X2 Ranked Probability Score (RPS)**: 0.23349
- **Goal MAE & RMSE**: Home Goals MAE = 1.08397, Away Goals MAE = 0.83451, Total Goals MAE = 1.48290.
- **Over 2.5 Metrics**: Over 2.5 Log Loss = 0.83362, Brier Score = 0.31284.
- **BTTS Metrics**: BTTS Log Loss = 0.69713, Brier Score = 0.25189.
- **Coverage & NO-BET Rates**: Coverage Rate = 59.81% (7,261 eligible forecasts), NO-BET Rate = 40.19% (4,879 NO-BET forecasts), Blocked Rate = 0.0000 (0 blocked forecasts).

## Validation Artifact Format
Stage 22 generates a machine-readable JSON artifact (`STAGE22_VALIDATION_ARTIFACT_v1.0.0`) stored at `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json` containing run metadata, provenance audit fields (`is_unseen_out_of_sample=False`), statistical interpretation, data quality summary, aggregate metrics, and individual `FixtureEvaluationRecord` entries.

## Limitations & Scope Rules
- **Selection-Set Replay Only**: Metrics represent historical replay performance on the Stage 13 selection set and do not constitute an unbiased out-of-sample estimate.
- **No Betting Odds or EV**: Bookmaker odds, +EV edge calculations, Kelly criterion, and bankroll management are strictly prohibited.
- **No Future Guarantee**: Historical validation metrics do not constitute a guarantee of future prediction performance.
