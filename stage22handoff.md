# STAGE 22 HANDOFF REPORT — HISTORICAL VALIDATION / SHADOW TESTING

STAGE
Stage 22 — Historical Validation / Shadow Testing

STATUS
COMPLETE

OBJECTIVE
Run a controlled historical validation and shadow-testing exercise against the approved prediction pipeline using only real historical football data acquired and validated by Stages 6–9. Evaluate the production forecaster (`xgboost_platt` from Stage 13) across post-training historical fixtures (2023-07-01 to 2024-06-30) without temporal leakage, data contamination, recalibration, or bookmaker odds modeling.

MODEL PROVENANCE AUDIT
- Training data period: Windows 1–3 (`2020-07-01` to `2023-06-30`, 37,723 historical matches).
- Calibration data period: Windows 1–3 (`2020-07-01` to `2023-06-30`).
- Model-selection period: Window 4 (`2023-07-01` to `2024-05-28`, 29,203 matches used in Stage 13 model candidate selection).
- Stage 22 evaluation period: `2023-07-01` to `2024-06-30` (12,140 eligible matches in historical dataset `STAGE9_FEATURE_DATASET_v1.0.0`).
- Overlap: Complete overlap exists between Stage 13 model selection (Window 4) and Stage 22 historical evaluation dates (`2023-07-01` to `2024-05-28`).
- Unseen evaluation verified: NO (`is_unseen_out_of_sample = False`).
- Evidence: Stage 13 calibration report (`stage13_calibration_report.json`) explicitly records Window 4 (`2023-07-01` to `2024-05-28`) as the selection holdout set used to select `xgboost_platt`.

DATASET COVERAGE RECONCILIATION
- Actual dataset end date: `2026-09-03` (dataset contains historical fixtures up to current cutoff).
- Stage 22 requested end date: `2024-06-30`.
- Actual fixtures available: 12,140 eligible fixtures occurring within `2023-07-01` to `2024-06-30`.
- Explanation: The historical dataset contains 12,140 eligible matches in the evaluation period. All 12,140 matches were evaluated in the Stage 22 shadow validation run and stored in `STAGE22_VALIDATION_ARTIFACT_v1.0.0`.

STATISTICAL INTERPRETATION
- Are the reported metrics unbiased out-of-sample metrics: NO
- Exact reason: Stage 22 evaluation fixtures (`2023-07-01` to `2024-06-30`) overlap with the Stage 13 model-selection period (`2023-07-01` to `2024-05-28`). The metrics represent historical selection-set replay performance and MUST NOT be presented as an unbiased out-of-sample estimate of future performance.

HISTORICAL EVALUATION RECONCILIATION
- Test fixtures: 2 (synthetic test-harness fixtures used strictly in automated unit tests `test_stage22_shadow_validation.py`).
- Actual historical fixtures: 12,140 real historical matches evaluated during the Stage 22 shadow validation run across global competitions.
- Total considered: 238,837 historical matches in dataset `STAGE9_FEATURE_DATASET_v1.0.0`.
- Eligible: 12,140 fixtures occurring strictly within the evaluation window (2023-07-01 to 2024-06-30).
- Excluded: 226,697 matches.
- Exact exclusion reasons:
  - `outside_evaluation_period`: 226,697 matches (occurring before 2023-07-01 or after 2024-06-30).
  - `missing_targets`: 0 matches.
  - `invalid_dates`: 0 matches.

METRIC RECOMPUTATION
- Data source: Historical pre-match feature vectors from `STAGE9_FEATURE_DATASET_v1.0.0` executed through `EndToEndPredictionPipeline`.
- Number of eligible fixtures: 12,140 fixtures.
- Calculation source: Calculated directly post-prediction over the 12,140 fixture evaluation records stored in `STAGE22_VALIDATION_ARTIFACT_v1.0.0`.
- Confirmation that metrics were independently recomputed: Confirmed. All metrics were independently calculated from the Stage 22 shadow prediction records and actual outcomes, without using or copying Stage 13 or earlier backtest outputs.
- Aggregate Metrics Recomputed:
  - 1X2 Log Loss: 1.10003
  - 1X2 Brier Score: 0.66603
  - 1X2 Ranked Probability Score (RPS): 0.23349
  - Home Goals MAE: 1.08397
  - Away Goals MAE: 0.83451
  - Total Goals MAE: 1.48290
  - Over 2.5 Log Loss: 0.83362
  - Over 2.5 Brier Score: 0.31284
  - BTTS Log Loss: 0.69713
  - BTTS Brier Score: 0.25189
  - Coverage Rate: 0.5981 (59.81% eligible forecasts)
  - NO-BET Rate: 0.4019 (40.19% NO-BET/low-confidence/high-risk forecasts)
  - Blocked Rate: 0.0000 (0.0% blocked forecasts)

PRE-MATCH INPUT AUDIT
- Prediction cutoff: $T_{\text{retrieval}} \le T_{\text{cutoff}}$ (strictly set to $12:00:00\text{Z}$ on match day, prior to kickoff).
- Information available before cutoff: Pre-match feature vectors (Stage 9 features computed up to match date) and fixture metadata.
- Outcome fields excluded: `full_time_result`, `full_time_home_goals`, `full_time_away_goals`, `total_goals`, `btts`.
- Leakage test result: PASS. `OutcomeLeakageError` verified via automated guard test `test_outcome_isolation_guard`.

HISTORICAL RESEARCH/EVIDENCE INPUT
- Exact source: Pre-match feature vectors from `STAGE9_FEATURE_DATASET_v1.0.0`.
- Whether live web acquisition was used: No live web acquisition occurred. Stage 14 automated web scraping is explicitly identified as not implemented.
- Whether mock/structured evidence was used: Structured pre-match feature vectors and default empty research containers were passed to `EndToEndPredictionPipeline`, evaluating model inference against base registered features without unvetted external web claims.

ARTIFACT RECONCILIATION
- Artifact version: `STAGE22_VALIDATION_ARTIFACT_v1.0.0`
- Artifact File Path: `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json`
- Artifact fixture count: 12,140 fixture evaluation records.
- Artifact metrics:
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
- Confirmation handoff matches artifact: Confirmed. All numbers in this handoff report match the generated validation artifact `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json` exactly.

IMPLEMENTED
- Updated `services/ml/app/validation/schemas.py` and `services/ml/app/validation/engine.py` adding explicit model provenance audit fields (`is_unseen_out_of_sample=False`, `model_selection_overlap_period`, `statistical_interpretation`).
- Executed `ShadowValidationEngine` over 12,140 real historical fixtures (`2023-07-01` to `2024-06-30`).
- Implemented strict outcome isolation and `OutcomeLeakageError` guard verifying that outcome fields (`full_time_result`, goals, btts) are strictly excluded from pre-match prediction input payloads.
- Computed post-prediction evaluation metrics across 12,140 real historical fixtures: 1X2 Log Loss (1.10003), Brier (0.66603), RPS (0.23349), Goal MAE, Over/Under 2.5, BTTS, coverage rate (59.81%), NO-BET rate (40.19%), and blocked rate (0.0%).
- Exported machine-readable artifact `STAGE22_VALIDATION_ARTIFACT_v1.0.0` at `/tmp/stage22_artifacts/stage22_shadow_validation_artifact.json`.
- Added unit and provenance guard tests in `services/ml/tests/test_stage22_shadow_validation.py` (`test_model_selection_provenance_guard`).
- Updated documentation in `docs/STAGE22_HISTORICAL_VALIDATION.md` and created `stage22handoff.md`.

RESEARCH PERFORMED
- Verified strict overlap between Stage 13 model selection dates (Window 4: `2023-07-01` to `2024-05-28`) and Stage 22 historical evaluation dates (`2023-07-01` to `2024-06-30`).
- Confirmed that `xgboost_platt` forecaster configuration from Stage 13 operates without recalibration during shadow testing.
- Audited Stage 9 feature vectors and Stage 16 current feature update cutoff rules to ensure $T_{\text{retrieval}} \le T_{\text{cutoff}}$.

FILES CREATED
- `services/ml/app/validation/__init__.py`
- `services/ml/app/validation/schemas.py`
- `services/ml/app/validation/engine.py`
- `services/ml/tests/test_stage22_shadow_validation.py`
- `docs/STAGE22_HISTORICAL_VALIDATION.md`
- `stage22handoff.md`

FILES MODIFIED
- `services/ml/app/selection/selector.py`

DATABASE CHANGES
None. (Shadow validation prediction reports utilize existing Stage 19 `PredictionReportModel` schema and `PredictionHistoryRepository` persistence layer).

DATA SOURCES
- Canonical historical football data lake (`STAGE9_FEATURE_DATASET_v1.0.0`).

DATASETS
- Dataset Version: `STAGE9_FEATURE_DATASET_v1.0.0`
- Feature Dataset Version: `STAGE9_FEATURE_DATASET_v1.0.0`

EVALUATION PERIOD
- Evaluation Period Start: `2023-07-01`
- Evaluation Period End: `2024-06-30`
- Training Cutoff Date: `2023-06-30`

MODEL/VERSION
- Model Name: `xgboost_platt`
- Model Version: `STAGE13_XGBOOST_PLATT_v1.0.0`
- Model Architecture: XGBoost Forecaster (`n_estimators=100`, `max_depth=5`, `learning_rate=0.05`)

CALIBRATION/VERSION
- Calibration Method: Platt Scaling (`PlattScaler`)
- Calibration Version: `STAGE13_PLATT_CALIBRATION_v1.0.0`

TESTS RUN
- `python3 -m unittest discover -s tests` (52 root architecture tests)
- `python3 -m unittest discover -s services/ml/tests` (137 ML unit & integration tests)

TEST RESULTS
- Total Tests Run: 189 tests across root and ML service packages.
- Passed: 187 tests passed.
- Failed: 0 tests failed.
- Skipped: 2 tests skipped (live PostgreSQL database integration tests skipped when local PostgreSQL server is unavailable).

DATA QUALITY
- Total Historical Fixtures Considered: 238,837
- Eligible Fixtures: 12,140
- Excluded Fixtures: 226,697
- Exclusion Reasons:
  - Outside evaluation period: 226,697
  - Missing targets: 0
- Missing-Data Impact: Fixtures lacking ground-truth outcomes are excluded from evaluation without fabrication.
- Blocked Predictions Count: 0
- NO-BET Predictions Count: 4,879 (40.19% NO-BET rate)

LEAKAGE CHECK
- Pre-match Input Leakage Status: `VERIFIED_NO_INPUT_LEAKAGE`
- Model Selection Overlap Status: Overlaps Window 4 selection dates (`is_unseen_out_of_sample = False`). Classified accurately as selection-set replay.
- `OutcomeLeakageError` verified via automated guard tests. Outcome targets (`full_time_result`, goals, btts) are strictly excluded from prediction input payloads.

NO-BET / BLOCKED RESULTS
- NO-BET Count: 4,879
- Blocked Count: 0
- Eligible Count: 7,261
- NO-BET Rate: 40.19%

ACCEPTANCE CRITERIA
1. Real historical football data used (Stages 6–9): PASS
2. Historical evaluation period occurs strictly after training cutoff date: PASS
3. Temporal cutoff rules enforced ($T_{\text{retrieval}} \le T_{\text{cutoff}}$): PASS
4. Outcome fields strictly isolated from prediction inputs: PASS
5. Approved Stage 13 production forecaster (`xgboost_platt`) used without recalibration: PASS
6. Shadow predictions recorded with probabilities, market outputs, and confidence/risk statuses: PASS
7. Evaluation metrics calculated strictly post-prediction across 12,140 historical fixtures: PASS
8. Supported Stage 17 markets evaluated: PASS
9. Machine-readable validation artifact (`STAGE22_VALIDATION_ARTIFACT_v1.0.0`) generated: PASS
10. Model selection overlap documented (`is_unseen_out_of_sample = False`) and classified as selection-set replay: PASS
11. Focused Stage 22 unit & provenance guard tests added and passing: PASS

SECURITY
- All prediction input payloads are validated using strict Pydantic v2 schemas.
- Pre-match input data isolation prevents malicious or post-match outcome injection.

KNOWN LIMITATIONS
1. Historical shadow testing evaluates selection-set replay performance due to overlap with Stage 13 Window 4 model selection dates. Genuinely unseen post-selection validation requires future data ingested after 2024-05-28.
2. In-memory SQLite test harnesses skip 2 live PostgreSQL integration tests when a live PostgreSQL database server is not running locally.

UNRESOLVED ISSUES
None.

TECHNICAL DECISIONS
- Explicitly set `is_unseen_out_of_sample = False` in validation schemas and engine to ensure complete statistical honesty and prevent overclaiming model generalization.
- Isolated prediction input construction from post-prediction outcome recording to provide mathematical and architectural proof against pre-match outcome leakage.

ENVIRONMENT VARIABLES
- `DATABASE_URL`: Optional PostgreSQL connection string for live database integration testing.

DEPLOYMENT STATUS
- Machine-readable artifact generator and shadow validation engine ready for automated CI/CD validation pipelines.

GIT STATUS
- New files staged for Stage 22 implementation under `services/ml/app/validation/`, `services/ml/tests/`, `docs/`, and root repository.

NEXT RECOMMENDED STAGE
Stage 23 — Live Match Operational Pipeline / Real-Time Testing

BLOCKERS
None.
