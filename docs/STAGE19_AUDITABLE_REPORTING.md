# STAGE 19 — AUDITABLE PREDICTION REPORTING AND HISTORY REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Selection Artifact**: `STAGE13_CALIBRATION_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE19_AUDITABLE_REPORTING_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 19 implements the platform's Auditable Prediction Reporting and History Engine. Operating on top of Stage 16 forecast containers (`CurrentMatchForecastContainer`), Stage 17 mapped market reports (`MappedMarketReport`), and Stage 18 risk decisions (`RiskEngineReport`), Stage 19 constructs complete, immutable, structured prediction reports for every prediction attempt.

Both prediction recommendations (`ELIGIBLE`) and abstentions (`LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`) are made fully auditable. The reporting engine preserves the complete end-to-end prediction chain trace (Verified Fixture $\to$ Current Evidence $\to$ Validated Evidence $\to$ Feature Updates $\to$ Model Forecaster $\to$ Probability Calibration $\to$ Market Probabilities $\to$ Confidence Scores / Risk Flags $\to$ Final Decision) and computes a deterministic SHA256 audit hash (`audit_hash`) over every prediction attempt.

---

## 2. Prediction Chain Traceability & Provenance Architecture

```
[1. Verified Fixture Identity] (Stage 14)
               │
               ▼
[2. Validated Research Evidence] (Stage 15)
               │
               ▼
[3. Updated Numerical Feature Vector & Provenance] (Stage 16)
               │
               ▼
[4. Approved Calibrated Model Forecast] (Stage 13 & 16: xgboost_platt)
               │
               ▼
[5. Mapped Market Probabilities & Provenance] (Stage 17)
               │
               ▼
[6. Confidence Score & Risk Flags Assessment] (Stage 18)
               │
               ▼
[7. Final Decision Status] (ELIGIBLE / NO-BET / BLOCKED)
               │
               ▼
[AuditablePredictionReport] ──► Deterministic SHA256 Audit Hash
               │
               ▼
[PredictionHistoryRepository] ──► PostgreSQL / In-Memory History
```

---

## 3. Distinction Between Probability, Confidence, and Risk

Stage 19 strictly enforces clear mathematical distinctions:
1. **Model Probability ($P \in [0, 1]$)**: Calibrated probability of match outcome (e.g. $P(\text{Home Win}) = 0.58$), derived from the statistical/ML forecaster.
2. **Confidence Score ($C \in [0.0, 1.0]$)**: Quality metric assessing prediction reliability based on calibration status, probability margins, feature completeness, and evidence freshess.
3. **Risk Flags**: Specific diagnostic risk indicators (`RISK_UNRESOLVED_EVIDENCE_CONFLICT`, `RISK_MISSING_KEY_FEATURE`, `RISK_LOW_TOP_PROBABILITY`, `RISK_UNSUPPORTED_MARKET`).
4. **Decision Status**: Final decision outcome (`ELIGIBLE`, `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`).

*Strict Rule*: Confidence scores are NEVER described as calibrated outcome probabilities, preventing misinterpretation by downstream operators.

---

## 4. Historical Repository Query Contracts

`PredictionHistoryRepository` supports multi-criteria querying via `PredictionHistoryFilter`:
- `prediction_id`: Unique prediction attempt UUID.
- `fixture_id`: Target match canonical ID.
- `start_date` / `end_date`: Historical prediction timestamp range.
- `model_name` / `model_version`: Forecaster attribution.
- `market_id`: Market identifier (`MKT_1X2`, `MKT_OVER_UNDER_2_5`, etc.).
- `decision_status`: Decision status (`ELIGIBLE`, `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`).

---

## 5. Testing & Verification

Unit test suite (`services/ml/tests/test_stage19_auditable_reporting.py`) verifies:
- Complete eligible prediction report generation.
- NO-BET and blocked report generation.
- Prediction chain provenance preservation.
- Model name, version, and calibration method preservation.
- Market probability and confidence/risk metric preservation.
- Deterministic SHA256 audit hash generation.
- Prediction history repository persistence and multi-criteria querying.
- Report immutability (overwriting existing report ID raises `ValueError`).
- Distinction between model probability and confidence score.
- Absolute absence of fabricated values, bookmaker odds, expected value edge, or Kelly stake sizing.

---

## 6. Stage Boundary & Limitations

1. **No Bookmaker Odds or Market Lines**: Bookmaker odds ingestion belongs to Stage 20.
2. **No Value / Edge / Kelly Sizing**: Expected value calculations belong to downstream prediction integration.
3. **No Automated Live Shadow Prediction Runs**: Live shadow testing belongs to Stage 22.
