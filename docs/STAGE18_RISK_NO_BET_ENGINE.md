# STAGE 18 — RISK, CONFIDENCE AND NO-BET ENGINE REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Selection Artifact**: `STAGE13_CALIBRATION_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE18_RISK_ENGINE_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 18 implements the platform's Risk, Confidence, and NO-BET Decision Engine. Operating on top of Stage 17 mapped market probabilities (`MappedMarketReport`) and Stage 16 forecast containers (`CurrentMatchForecastContainer`), Stage 18 evaluates prediction strength, model calibration status, feature completeness, evidence conflicts, and market support to determine a deterministic confidence score ($C \in [0.0, 1.0]$), confidence level (`HIGH`, `MEDIUM`, `LOW`), risk flags, and final decision status.

Decision statuses explicitly support `ELIGIBLE`, `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, and `BLOCKED`. `NO-BET` and `INSUFFICIENT_EVIDENCE` are treated as first-class prediction outputs whenever data quality, evidence completeness, top outcome probability, or market support is insufficient. The engine preserves 100% provenance traceability without using bookmaker odds, calculating expected value edges, or determining Kelly stake sizes.

---

## 2. Decision Status Rules & Risk Flags

```
[Stage 17 Mapped Market Report] + [Stage 16 Forecast Container]
                                │
                                ▼
         [1. Forecast Container Status Check] ──(Not Ready -> BLOCKED)
                                │
                                ▼
          [2. Market Support Status Check] ──(Unsupported -> BLOCKED)
                                │
                                ▼
         [3. Feature Completeness Evaluator] ──(Missing -> RISK_MISSING_KEY_FEATURE)
                                │
                                ▼
          [4. Evidence Conflict Audit] ──(Conflict -> RISK_UNRESOLVED_EVIDENCE_CONFLICT)
                                │
                                ▼
        [5. Probability Margin Evaluator] ──(Low -> RISK_LOW_TOP_PROBABILITY)
                                │
                                ▼
          [6. Confidence Score & Decision] ──► Output MarketDecision
```

### 2.1 Supported Decision Statuses

| Decision Status | Condition / Trigger Rule | Action |
| :--- | :--- | :--- |
| **`ELIGIBLE`** | Confidence score $\ge 0.65$, no critical risk flags, market supported, model calibrated. | Recommendation candidate. |
| **`LOW_CONFIDENCE`** | Top probability $P_{\text{max}} < 0.38$ (3-way) / $< 0.52$ (binary) or confidence $< 0.50$. | **NO-BET** recommendation. |
| **`HIGH_RISK`** | Multiple risk flags present (e.g. uncalibrated model + missing feature + low probability). | **NO-BET** recommendation. |
| **`INSUFFICIENT_EVIDENCE`** | Unresolved evidence conflicts present or $> 10$ feature values missing. | **NO-BET** recommendation. |
| **`BLOCKED`** | Forecast container blocked, fixture unverified, or market unsupported. | **BLOCKED** from recommendation. |

### 2.2 Deterministic Risk Flags

- `RISK_UNRESOLVED_EVIDENCE_CONFLICT`: Opposing evidence claims detected in Stage 15/16 research.
- `RISK_MISSING_KEY_FEATURE`: One or more registered Stage 9 features are `NULL`.
- `RISK_LOW_TOP_PROBABILITY`: Top outcome probability fails market strength threshold.
- `RISK_UNSUPPORTED_MARKET`: Market is classified as unsupported in Stage 17 catalogue.
- `RISK_BLOCKED_FORECAST_CONTAINER`: Source forecast container has status `BLOCKED_NO_FORECAST`.
- `RISK_UNSUPPORTED_MODEL_CALIBRATION`: Forecast originates from uncalibrated model variant.
- `RISK_UNVERIFIED_FIXTURE`: Target match identity is unverified.
- `RISK_STALE_EVIDENCE`: Research evidence retrieval timestamp exceeds freshness threshold (> 7 days).

---

## 3. Confidence Calculation Rule

Confidence score $C \in [0.0, 1.0]$ is computed deterministically:
- **Base Confidence**: $0.70$ if calibrated (`platt_sigmoid`), $0.50$ if uncalibrated (`none`).
- **Probability Signal**: $+ 0.20 \times P_{\text{max}}$ (where $P_{\text{max}}$ is the top outcome probability).
- **Feature Completeness Penalty**: $- 0.05$ per missing feature field.
- **Evidence Conflict Penalty**: $- 0.35$ for unresolved evidence conflicts.
- **Stale Evidence Penalty**: $- 0.15$ for stale or uncertain research evidence.

Confidence Level Assignment:
- `HIGH`: $C \ge 0.70$
- `MEDIUM`: $0.50 \le C < 0.70$
- `LOW`: $C < 0.50$

---

## 4. Traceability & Provenance Contracts

Every `MarketDecision` records a `provenance_summary` containing:
- `source_container_id`: Source Stage 16 forecast container UUID.
- `source_fixture_id`: Target fixture canonical UUID.
- `model_name` & `model_version`: Forecaster attribution.
- `calibration_method`: Calibration status (`platt_sigmoid`, `isotonic_regression`, `none`).
- `container_status` & `container_blocked_reason`: Source container status.
- `market_supported` & `market_unsupported_reason`: Stage 17 support classification.

---

## 5. Testing & Verification

Unit test suite (`services/ml/tests/test_stage18_risk_engine.py`) verifies:
- Valid market with sufficient evidence (`ELIGIBLE`).
- Low top probability generating `LOW_CONFIDENCE` (NO-BET).
- Multiple risk factors generating `HIGH_RISK` (NO-BET).
- Unresolved evidence conflicts generating `INSUFFICIENT_EVIDENCE` (NO-BET).
- Missing features generating `RISK_MISSING_KEY_FEATURE`.
- Blocked forecast containers generating `BLOCKED` status.
- Unsupported markets generating `BLOCKED` status.
- Deterministic confidence score calculation and bounds $[0.0, 1.0]$.
- Full provenance preservation in `provenance_summary`.
- Complete absence of bookmaker odds, value calculation, or Kelly stake sizing.

---

## 6. Stage Boundary & Limitations

1. **No Bookmaker Odds or Odds Comparisons**: Odds ingestion belongs strictly to Stage 19/20.
2. **No Value / Edge / Kelly Stake Sizing**: Expected value calculation and bankroll management are deferred.
3. **No Auditable Database Audit Records**: PostgreSQL audit database persistence belongs to Stage 19.
