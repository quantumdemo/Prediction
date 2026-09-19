# STAGE 16 — CURRENT-MATCH FEATURE UPDATE & FORECASTING PIPELINE REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Selection Artifact**: `STAGE13_CALIBRATION_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE16_CURRENT_MATCH_PIPELINE_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 16 implements the Current-Match Feature Update and Forecasting Pipeline. This layer takes Stage 15 validated current-match evidence, updates prediction-time safe numerical features defined in the Stage 9 Feature Registry (`STAGE9_FEATURE_REGISTRY`), enforces strict prediction-time cutoff bounds ($T_{\text{retrieval}} \le T_{\text{cutoff}}$), records complete feature update provenance (`CurrentFeatureProvenance`), preserves explicit missingness states without data fabrication, and passes updated feature vectors into the approved Stage 13 production model (`xgboost_platt`).

Unverified fixtures, prediction-time leakage, or unresolved critical evidence conflicts automatically trigger a structured `BLOCKED_NO_FORECAST` status with explicit reason tracking. Stage 16 maintains strict architectural separation from betting market mapping (Stage 17), risk scoring / NO-BET abstention logic (Stage 18), and prediction report rendering (Stage 20).

---

## 2. Pipeline Architecture & Data Flow

```
[Verified Fixture & Baseline Stage 9 Vectors]
                   │
                   ▼
[Stage 15 Validated Evidence Report]
                   │
                   ▼
[1. Prediction-Time Cutoff Check] ──(T_retrieved > T_cutoff -> PREDICTION_TIME_LEAKAGE)
                   │
                   ▼
[2. Conflict & Unverified Check] ──(Unresolved Conflicts -> BLOCKED_NO_FORECAST)
                   │
                   ▼
[3. Current Feature Updater] ──► Updates Stage 9 Numerical Features
                   │             & Records Feature Provenance
                   ▼
[4. Updated MatchFeatureVector]
                   │
                   ▼
[5. Approved Stage 13 Model Interface] ──► XGBoostForecaster (xgboost_platt)
                   │
                   ▼
[CurrentMatchForecastContainer] ──► Output Structured Forecast Output
```

---

## 3. Feature Update & Provenance Rules

1. **Stage 9 Registry Reuse**: Only registered Stage 9 numerical features (`FEAT_REST_DAYS_HOME`, `FEAT_FORM3_HOME`, `FEAT_H2H_HOME_WINS`, etc.) are updated. New unregistered features cannot be dynamically invented.
2. **Prediction-Time Cutoff Enforcement**: Evidence retrieved after prediction cutoff $T_{\text{cutoff}}$ is rejected with reason `PREDICTION_TIME_LEAKAGE`.
3. **Explicit Missingness Preservation**: Missing or unverified features retain explicit missingness states (`INSUFFICIENT_HISTORY`, `MISSING_SOURCE_DATA`, `PRESERVE_NULL`). Default or fabricated values are strictly forbidden.
4. **Full Feature Provenance**: Every updated feature records `feature_id`, `updated_value`, `original_historical_value`, `source_fact_id`, `source_name`, `source_url`, `evidence_state`, `update_timestamp_utc`, and `transformation_rule`.

---

## 4. Model Selection Interface Usage

Stage 16 invokes the production forecaster selected in Stage 13 (`xgboost_platt` / `XGBoostForecaster` calibrated with Platt Scaling). Stage 16 does NOT retrain models, alter model parameters, or re-run model selection.

---

## 5. Testing & Verification

Unit test suite (`services/ml/tests/test_stage16_current_forecasting.py`) verifies:
- Verified fixture flow and `READY` forecast container status.
- Valid current evidence feature updating and provenance capture.
- Missing evidence handling with preserved NULL states.
- Stale evidence handling and state downgrading.
- Unresolved evidence conflict blocking (`BLOCKED_NO_FORECAST`).
- Unverified fixture rejection (`UNVERIFIED_FIXTURE`).
- Prediction-time leakage rejection (`PREDICTION_TIME_LEAKAGE`).
- Deterministic feature vector generation.
- Correct Stage 13 selected model interface usage (`XGBoostForecaster`).
- Absolute rejection of synthetic or fabricated values.

---

## 6. Stage Boundary & Limitations

1. **No Market Mapping or Odds**: Market catalogue mapping and bookmaker odds belong strictly to Stage 17.
2. **No Value / Kelly / NO-BET Engine**: Risk scoring, value calculation, and NO-BET decision logic belong strictly to Stage 18.
3. **No Auditable Database Ingestion**: Storing traceable audit records in PostgreSQL belongs strictly to Stage 19.
