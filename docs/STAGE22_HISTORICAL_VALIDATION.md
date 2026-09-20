# Stage 22 — Historical Validation / Shadow Testing Specification & Documentation

## Overview
Stage 22 implements a controlled historical shadow-validation framework for the football AI platform. It evaluates the production prediction pipeline (`EndToEndPredictionPipeline`) and production forecaster (`xgboost_platt` calibrated via Stage 13 Platt Scaling) across historical football fixtures without temporal leakage, data contamination, or odds modeling.

## Core Architectural Design & No-Leakage Guard
To guarantee zero outcome contamination, prediction inputs are strictly isolated from post-prediction evaluation outcomes.

1. **Prediction Input Isolation**: The prediction pipeline receives ONLY pre-match feature vectors ($T_{\text{retrieval}} \le T_{\text{cutoff}}$) and pre-match fixture metadata.
2. **Outcome Leakage Guard**: `OutcomeLeakageError` is raised if outcome variables (`full_time_result`, `full_time_home_goals`, `full_time_away_goals`, `total_goals`, `btts`) enter the prediction payload.
3. **Post-Prediction Evaluation**: Actual match outcomes are recorded separately in `ActualMatchOutcome` records after shadow predictions are generated.

## Evaluation Period & Dataset Versioning
- **Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
- **Feature Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
- **Training Cutoff Date**: `2023-06-30`
- **Evaluation Period**: `2023-07-01` to `2024-06-30` (Window 4 post-training historical period)
- **Production Forecaster**: `xgboost_platt` (`STAGE13_XGBOOST_PLATT_v1.0.0`)

## Evaluated Supported Markets
Shadow predictions are generated and evaluated for the 8 approved Stage 17 markets:
1. `MKT_MATCH_RESULT_1X2` (Home, Draw, Away)
2. `MKT_TOTAL_GOALS_OVER_UNDER` (Over / Under 0.5 to 4.5)
3. `MKT_BOTH_TEAMS_TO_SCORE` (BTTS Yes / No)
4. `MKT_CORRECT_SCORE_GRID` (0-3 x 0-3 Grid)

## Aggregate Metrics & NO-BET Statistics
Aggregate performance is calculated strictly post-prediction over evaluated shadow predictions:
- **1X2 Log Loss**: Multi-class cross-entropy log loss over outcome probabilities.
- **1X2 Brier Score**: Mean squared error over multi-class probability vectors.
- **1X2 Ranked Probability Score (RPS)**: Ranked probability score evaluating ordered outcome predictions (Home, Draw, Away).
- **Goal MAE & RMSE**: Expected Home/Away goal errors compared to actual goals scored.
- **Coverage & NO-BET Rates**: Explicit tracking of `ELIGIBLE`, `NO_BET`, `LOW_CONFIDENCE`, and `BLOCKED` prediction statuses.

## Validation Artifact Format
Stage 22 generates a machine-readable JSON artifact (`STAGE22_VALIDATION_ARTIFACT_v1.0.0`) stored at `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json` containing run metadata, data quality summary, aggregate metrics, and individual `FixtureEvaluationRecord` entries.

## Limitations & Scope Rules
- **Shadow Mode Only**: This is a historical validation exercise, not a live trading or betting advisory system.
- **No Betting Odds or EV**: Bookmaker odds, +EV edge calculations, Kelly criterion, and bankroll management are strictly prohibited.
- **No Future Guarantee**: Historical validation metrics do not constitute a guarantee of future prediction performance.
