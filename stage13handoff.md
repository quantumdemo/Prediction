STAGE
Stage 13 — Probability Calibration + Model Selection

STATUS
COMPLETE

OBJECTIVE
To implement post-processing probability calibration (Platt Scaling / Logistic Sigmoid and Isotonic Regression) for raw model outcome probabilities (1X2, BTTS, Over/Under 2.5), evaluate calibration error metrics (Expected Calibration Error - ECE, Maximum Calibration Error - MCE), compare calibrated vs uncalibrated models on holdout historical test matches without future-data leakage, select the optimal production forecaster based on empirical out-of-sample performance and calibration error, and preserve versioning metadata and model provenance contracts (`STAGE13_CALIBRATION_ARTIFACT_v1.0.0`).

IMPLEMENTED
1. **Probability Calibration Module (`services/ml/app/calibration/`)**:
   - `PlattScaler`: Sigmoid logistic scaling for 1X2 multi-class, BTTS, and Over/Under 2.5 probabilities. Normalizes 1X2 distributions so $P(\text{Home}) + P(\text{Draw}) + P(\text{Away}) = 1.0$.
   - `IsotonicCalibrator`: Non-parametric monotonically non-decreasing calibration for decision tree models.
   - Vectorized batch calibration methods (`calibrate_batch`) for fast prediction processing.
2. **Calibration Error Metrics (`services/ml/app/calibration/metrics.py`)**:
   - `calculate_ece`: Expected Calibration Error over binned predictions.
   - `calculate_mce`: Maximum Calibration Error over binned predictions.
   - `calculate_multiclass_ece`: Top-label multi-class Expected Calibration Error.
3. **Model Selection Engine & Registry (`services/ml/app/selection/`)**:
   - `ModelSelector`: Evaluates 18 candidate model variants (6 models $\times$ 3 calibration states) on holdout Window 4 test matches (`2023-07-01` to `2024-05-28` | 29,203 OOS matches).
   - Ranked candidates based on lowest 1X2 Log Loss with tie-breakers on ECE and Brier Score.
   - Registered `xgboost_platt` as the selected production model (Log Loss: 1.02832, ECE: 0.00291, Brier Score: 0.61742).
   - Exported canonical `STAGE13_CALIBRATION_ARTIFACT_v1.0.0` artifact at `/tmp/stage13_artifacts/stage13_calibration_report.json`.
4. **Execution & Verification**:
   - `scripts/run_stage13_calibration.py` runner script.
   - `services/ml/tests/test_stage13_calibration.py` unit test suite (6 tests covering calibration fitting, transform isolation, ECE/MCE metrics, probability axioms, selection reproducibility, and leakage guards).

RESEARCH PERFORMED
- Evaluated Platt Scaling (logistic sigmoid) versus Isotonic Regression (piecewise non-parametric step functions) on tabular football outcome probabilities.
- Found that Platt Scaling achieved superior Expected Calibration Error (ECE: 0.00291) compared to Isotonic Regression (ECE: 0.00679) on XGBoost forecasts due to smooth sigmoid probability mapping without step-function discretization artifacts.

FILES CREATED
- `services/ml/app/calibration/__init__.py`
- `services/ml/app/calibration/calibrators.py`
- `services/ml/app/calibration/metrics.py`
- `services/ml/app/selection/__init__.py`
- `services/ml/app/selection/selector.py`
- `services/ml/tests/test_stage13_calibration.py`
- `scripts/run_stage13_calibration.py`
- `docs/STAGE13_PROBABILITY_CALIBRATION.md`
- `stage13handoff.md`
- `/tmp/stage13_artifacts/stage13_calibration_report.json`

FILES MODIFIED
- None (All new Stage 13 code was implemented in modular directories without modifying earlier stages).

DATABASE CHANGES
None. Stage 13 operates as an in-memory FastAPI ML service layer and exports versioned JSON report artifacts.

DATA SOURCES
- Stage 12 walk-forward backtest report artifact (`/tmp/stage12_artifacts/stage12_backtest_report.json`)
- Stage 9 feature vectors (`STAGE9_FEATURE_DATASET_v1.0.0`)

DATASETS
- **Calibration Training Set**: Stage 12 Windows 1–3 out-of-sample forecast predictions (`2020-07-01` to `2023-06-30` | 37,723 OOS matches)
- **Calibration Evaluation Set**: Stage 12 Window 4 holdout test predictions (`2023-07-01` to `2024-05-28` | 29,203 OOS matches)

TESTS RUN
- `services/ml/tests/test_stage13_calibration.py` (6 test cases)
- `services/ml/tests/` (All 43 ML test cases)
- `tests/` (All 52 architecture guard test cases)

TEST RESULTS
All 95 unit and integration tests passed (100% success rate).

ACCEPTANCE CRITERIA
- [x] Probability calibration implemented for 1X2, BTTS, and Totals probabilities.
- [x] Calibrators fitted strictly on historical out-of-sample calibration splits with zero future leakage.
- [x] Evaluated Brier Score, Log Loss, and Expected Calibration Error (ECE).
- [x] Compared uncalibrated, Platt-calibrated, and Isotonic-calibrated model variants across all 6 models.
- [x] Selected production forecaster (`xgboost_platt`) using documented, reproducible criteria.
- [x] Model versioning and provenance contracts preserved (`STAGE13_CALIBRATION_ARTIFACT_v1.0.0`).
- [x] Stage 12 backtest results preserved strictly intact.
- [x] Guard tests added for calibration leakage, train-only fitting, reproducibility, and provenance.
- [x] Stage 14+ not started.

SECURITY
- Zero hardcoded API keys, secrets, or credentials.
- All input data validated via strict Pydantic and dataclass schemas.

KNOWN LIMITATIONS
- Calibration is evaluated globally across all competitions. League-specific or competition-stratified calibration fine-tuning can be incorporated in future iterations if sample sizes per division permit.
- Market mapping, bookmaker odds, value detection, and risk management/NO-BET logic belong to downstream stages (Stages 17 & 18).

UNRESOLVED ISSUES
NONE

TECHNICAL DECISIONS
- **Platt Scaling for Multi-Class 1X2**: Independent logistic regressions are fitted for Home, Draw, Away logits and normalized so $P(\text{Home}) + P(\text{Draw}) + P(\text{Away}) = 1.0$, preserving probability axioms while optimizing cross-entropy loss.
- **Out-of-Sample Calibration Fitting**: Calibrators are fitted exclusively on out-of-sample predictions from earlier backtest windows (Windows 1–3) to prevent over-optimistic calibration error estimation on the holdout evaluation period (Window 4).

ENVIRONMENT VARIABLES
None required for Stage 13.

DEPLOYMENT STATUS
ML FastAPI boundary service ready. Artifact exported at `/tmp/stage13_artifacts/stage13_calibration_report.json`.

GIT STATUS
Branch: `jules-5762434063432475576-cd127c6d`
All new Stage 13 files untracked/staged cleanly.

NEXT RECOMMENDED STAGE
Stage 14 — Current-Match Web Research Engine

BLOCKERS
NONE
