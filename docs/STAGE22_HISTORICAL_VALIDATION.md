# Stage 22 — Historical Validation / Shadow Testing Final Report

## 1. Stage 22 Objective and Status
- **Stage**: Stage 22 — Historical Validation / Shadow Testing
- **Status**: COMPLETE
- **Objective**: Execute a controlled historical validation and shadow-testing exercise against the approved prediction pipeline using real historical football data from Stages 6–9. Evaluate the production forecaster (`xgboost_platt` from Stage 13) across historical fixtures without temporal leakage, data contamination, recalibration, or bookmaker odds modeling.

## 2. Model Provenance Audit
- **Training Period**: Windows 1–3 (`2020-07-01` to `2023-06-30`, 37,723 historical matches).
- **Calibration Fit Period**: Windows 1–3 (`2020-07-01` to `2023-06-30`).
- **Stage 13 Model-Selection Period**: Window 4 (`2023-07-01` to `2024-05-28`, 29,203 matches used in Stage 13 candidate model selection).
- **Stage 22 Evaluation Period**: `2023-07-01` to `2024-06-30` (12,140 eligible matches in historical dataset `STAGE9_FEATURE_DATASET_v1.0.0`).
- **Explicit Overlap**: Complete overlap exists between the Stage 13 model selection holdout set (Window 4: `2023-07-01` to `2024-05-28`) and the Stage 22 historical evaluation dates (`2023-07-01` to `2024-06-30`).
- **Unseen Out-Of-Sample Evaluation Verified**: NO (`is_unseen_out_of_sample = False`).
- **Statistical Interpretation**: `HISTORICAL_SELECTION_SET_REPLAY`. Reported metrics represent historical selection-set replay performance and MUST NOT be presented as an unbiased out-of-sample performance estimate.

## 3. Dataset Coverage Reconciliation
- **Total Historical Fixtures Considered**: 238,837 historical matches in dataset `STAGE9_FEATURE_DATASET_v1.0.0`.
- **Eligible Fixtures**: 12,140 matches occurring strictly within `2023-07-01` to `2024-06-30`.
- **Excluded Fixtures**: 226,697 matches.
- **Exact Exclusion Reasons**:
  - `outside_evaluation_period`: 226,697 matches (occurring before `2023-07-01` or after `2024-06-30`).
  - `missing_targets`: 0 matches.
  - `invalid_dates`: 0 matches.

## 4. Independently Recomputed Metrics
All aggregate metrics were calculated post-prediction directly from the 12,140 fixture-level evaluation records in `STAGE22_VALIDATION_ARTIFACT_v1.0.0`:
- **1X2 Multi-class Log Loss**: 1.10003
- **1X2 Brier Score**: 0.66603
- **1X2 Ranked Probability Score (RPS)**: 0.23349
- **Home Goals MAE**: 1.08397
- **Away Goals MAE**: 0.83451
- **Total Goals MAE**: 1.48290
- **Over 2.5 Log Loss**: 0.83362
- **Over 2.5 Brier Score**: 0.31284
- **BTTS Log Loss**: 0.69713
- **BTTS Brier Score**: 0.25189
- **Coverage Rate**: 0.5981 (59.81% eligible forecasts, 7,261 matches)
- **NO-BET Rate**: 0.4019 (40.19% NO-BET/low-confidence/high-risk forecasts, 4,879 matches)
- **Blocked Rate**: 0.0000 (0.0% blocked forecasts, 0 matches)

## 5. Pre-Match Input Cutoff & Outcome Isolation Verification
- **Pre-match Input Cutoff**: $T_{\text{retrieval}} \le T_{\text{cutoff}}$ (strictly set to $12:00:00\text{Z}$ on match day, prior to kickoff).
- **Information Available Before Cutoff**: Pre-match feature vectors (Stage 9 features computed up to match date) and pre-match fixture metadata.
- **Outcome Fields Excluded**: `full_time_result`, `full_time_home_goals`, `full_time_away_goals`, `total_goals`, `btts`.
- **Leakage Test Result**: PASS (`VERIFIED_NO_INPUT_LEAKAGE`). `OutcomeLeakageError` verified via automated guard test `test_outcome_isolation_guard`.

## 6. Historical Research/Evidence Input & Web Acquisition Realities
- **Exact Source**: Pre-match feature vectors from `STAGE9_FEATURE_DATASET_v1.0.0`.
- **No Live Web Acquisition**: No live web scraping or active HTTP web fetching occurred. Stage 14 automated web scraping is explicitly identified as not implemented.
- **Structured Evidence Input**: Structured pre-match feature vectors and default empty research containers were passed to `EndToEndPredictionPipeline`, evaluating model inference against base registered features without unvetted external web claims.

## 7. Artifact Reconciliation
- **Artifact Version**: `STAGE22_VALIDATION_ARTIFACT_v1.0.0`
- **Artifact File Path**: `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json`
- **Artifact Fixture Count**: 12,140 fixture evaluation records.
- **Artifact Metrics**:
  - Total Considered: 238,837
  - Eligible: 12,140
  - Excluded: 226,697
  - Eligible Count: 7,261
  - NO-BET Count: 4,879
  - Blocked Count: 0
  - 1X2 Log Loss: 1.10003
  - 1X2 Brier Score: 0.66603
  - 1X2 RPS: 0.23349
  - Pre-match Input Leakage Status: `VERIFIED_NO_INPUT_LEAKAGE`
  - Unseen Out of Sample: `False`
  - Statistical Interpretation: `HISTORICAL_SELECTION_SET_REPLAY`

## 8. Implemented Changes & Files
- **Files Created**:
  - `services/ml/app/validation/__init__.py`
  - `services/ml/app/validation/schemas.py`
  - `services/ml/app/validation/engine.py`
  - `services/ml/tests/test_stage22_shadow_validation.py`
  - `docs/STAGE22_HISTORICAL_VALIDATION.md`
  - `stage22handoff.md`
- **Files Modified**:
  - `services/ml/app/selection/selector.py`
- **Database Changes**: None. (Shadow validation prediction reports utilize existing Stage 19 `PredictionReportModel` schema and `PredictionHistoryRepository` persistence layer).
- **Data Sources / Datasets**: Canonical historical football data lake (`STAGE9_FEATURE_DATASET_v1.0.0`).

## 9. Model and Calibration Versions
- **Model Name**: `xgboost_platt`
- **Model Version**: `STAGE13_XGBOOST_PLATT_v1.0.0`
- **Model Architecture**: XGBoost Forecaster (`n_estimators=100`, `max_depth=5`, `learning_rate=0.05`)
- **Calibration Method**: Platt Scaling (`PlattScaler`)
- **Calibration Version**: `STAGE13_PLATT_CALIBRATION_v1.0.0`

## 10. Tests and Exact Results
- **Tests Executed**:
  - `python3 -m unittest discover -s tests` (52 root architecture tests)
  - `python3 -m unittest discover -s services/ml/tests` (137 ML unit & integration tests)
- **Results**: 187 tests passed, 0 failed, 2 skipped (live PostgreSQL integration tests skipped when local PostgreSQL server is unavailable).

## 11. Data Quality, NO-BET & Blocked Results
- **Total Historical Fixtures Considered**: 238,837
- **Eligible Fixtures**: 12,140
- **Excluded Fixtures**: 226,697 (`outside_evaluation_period`)
- **Eligible Predictions Count**: 7,261 (59.81% coverage rate)
- **NO-BET Predictions Count**: 4,879 (40.19% NO-BET rate)
- **Blocked Predictions Count**: 0 (0.0% blocked rate)

## 12. Acceptance Criteria
1. Real historical football data used (Stages 6–9): PASS
2. Historical evaluation period occurs after the model training cutoff: PASS; however, it overlaps the Stage 13 model-selection period and is therefore not an unbiased out-of-sample evaluation.
3. Temporal cutoff rules enforced ($T_{\text{retrieval}} \le T_{\text{cutoff}}$): PASS
4. Outcome fields strictly isolated from prediction inputs: PASS
5. Approved Stage 13 production forecaster (`xgboost_platt`) used without recalibration: PASS
6. Shadow predictions recorded with probabilities, market outputs, and confidence/risk statuses: PASS
7. Evaluation metrics calculated strictly post-prediction across 12,140 historical fixtures: PASS
8. Supported Stage 17 markets evaluated: PASS
9. Machine-readable validation artifact (`STAGE22_VALIDATION_ARTIFACT_v1.0.0`) generated: PASS
10. Model selection overlap documented (`is_unseen_out_of_sample = False`) and classified as selection-set replay: PASS
11. Focused Stage 22 unit & provenance guard tests added and passing: PASS

## 13. Security, Known Limitations & Technical Decisions
- **Security**: All prediction input payloads are validated using strict Pydantic v2 schemas. Pre-match input data isolation prevents outcome injection.
- **Known Limitations**: Historical shadow testing evaluates selection-set replay performance due to overlap with Stage 13 Window 4 model selection dates. Genuinely unseen post-selection validation requires future data ingested after 2024-05-28. In-memory SQLite test harnesses skip 2 live PostgreSQL integration tests when a live PostgreSQL server is not running locally.
- **Technical Decisions**: Explicitly set `is_unseen_out_of_sample = False` in validation schemas and engine to ensure complete statistical honesty and prevent overclaiming model generalization.

## 14. Deployment & Git Status
- **Environment Variables**: `DATABASE_URL` (optional PostgreSQL connection string for live DB testing).
- **Deployment Status**: Ready for automated CI/CD pipeline integration.
- **Git Status**: All Stage 22 validation files, tests, documentation, and handoff report staged cleanly.

## 15. Correct Next Stage
- **Next Recommended Stage**: Stage 23 — Production Infrastructure + DB Hardening
