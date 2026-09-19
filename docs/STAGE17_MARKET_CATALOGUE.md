# STAGE 17 — MARKET CATALOGUE AND MAPPING REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Selection Artifact**: `STAGE13_CALIBRATION_ARTIFACT_v1.0.0`
**Code Identifier**: `STAGE17_MARKET_MAPPING_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 17 implements the platform's Market Catalogue and Deterministic Market Mapping Engine. Operating directly on the calibrated probability outputs of Stage 16 (`CurrentMatchForecastContainer`), Stage 17 maps model expectations into 8 supported football betting markets (Full Time Result 1X2, Over/Under Goals 0.5, 1.5, 2.5, 3.5, 4.5, Both Teams To Score BTTS, and Correct Score Grid) using exact deterministic mathematical rules.

Three unsupported market categories (`MKT_ASIAN_HANDICAP`, `MKT_CORNER_TOTALS`, `MKT_CARD_TOTALS`) are registered in the controlled catalogue with `is_supported=False` and explicit rejection reasons. Probabilities are strictly bounded in $[0, 1]$ and satisfy complementary probability axioms ($\sum P = 1.0$). Every mapped market records full traceability back to the source forecast container, fixture ID, model name, model version, and transformation rule. Bookmaker odds, expected value edge calculations, risk scoring, and NO-BET decision logic are strictly excluded from Stage 17.

---

## 2. Controlled Market Catalogue & Mapping Rules

| Canonical Market ID | Market Name | Market Type | Required Model Output | Mapping Transformation Rule | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `MKT_1X2` | Full Time Result (1X2) | Multi-Class | `probabilities_1x2` | Direct mapping of calibrated Home, Draw, Away probabilities. $\sum P = 1.0$. | **SUPPORTED** |
| `MKT_OVER_UNDER_0_5` | Over/Under 0.5 Goals | Binary | `probabilities_totals` | Direct mapping of Over 0.5 & Under 0.5 probabilities. $P(\text{Over}) + P(\text{Under}) = 1.0$. | **SUPPORTED** |
| `MKT_OVER_UNDER_1_5` | Over/Under 1.5 Goals | Binary | `probabilities_totals` | Direct mapping of Over 1.5 & Under 1.5 probabilities. $P(\text{Over}) + P(\text{Under}) = 1.0$. | **SUPPORTED** |
| `MKT_OVER_UNDER_2_5` | Over/Under 2.5 Goals | Binary | `probabilities_totals` | Direct mapping of Over 2.5 & Under 2.5 probabilities. $P(\text{Over}) + P(\text{Under}) = 1.0$. | **SUPPORTED** |
| `MKT_OVER_UNDER_3_5` | Over/Under 3.5 Goals | Binary | `probabilities_totals` | Direct mapping of Over 3.5 & Under 3.5 probabilities. $P(\text{Over}) + P(\text{Under}) = 1.0$. | **SUPPORTED** |
| `MKT_OVER_UNDER_4_5` | Over/Under 4.5 Goals | Binary | `probabilities_totals` | Direct mapping of Over 4.5 & Under 4.5 probabilities. $P(\text{Over}) + P(\text{Under}) = 1.0$. | **SUPPORTED** |
| `MKT_BTTS` | Both Teams To Score | Binary | `probabilities_btts` | Direct mapping of BTTS Yes & BTTS No probabilities. $P(\text{Yes}) + P(\text{No}) = 1.0$. | **SUPPORTED** |
| `MKT_CORRECT_SCORE` | Correct Score Grid | Matrix | `correct_score_matrix` | Matrix extraction of exact score probabilities $P(h, a)$. $\sum P(h, a) = 1.0$. | **SUPPORTED** |
| `MKT_ASIAN_HANDICAP` | Asian Handicap | Handicap | `handicap_distribution` | Requires Asian handicap distribution model - Not supported in Stage 17. | **UNSUPPORTED** |
| `MKT_CORNER_TOTALS` | Total Match Corners | Statistical | `corner_distribution` | Requires corner Poisson model - Not supported in Stage 17. | **UNSUPPORTED** |
| `MKT_CARD_TOTALS` | Total Match Cards | Statistical | `card_distribution` | Requires booking points model - Not supported in Stage 17. | **UNSUPPORTED** |

---

## 3. Traceability & Provenance Contracts

Every `MappedMarket` contains a `MarketProvenanceRecord` with immutable audit attributes:
- `market_id`: Canonical market identifier (e.g. `MKT_1X2`).
- `source_forecast_container_id`: Source Stage 16 container ID.
- `source_fixture_id`: Target fixture canonical UUID.
- `source_model_name` & `source_model_version`: Forecaster attribution (e.g., `XGBoostForecaster` / `1.0.0_platt`).
- `mapping_rule`: Deterministic transformation rule applied.
- `is_supported` & `unsupported_reason`: Clear support classification.
- `mapping_timestamp_utc`: UTC timestamp when mapping was executed.

---

## 4. Testing & Verification

Unit test suite (`services/ml/tests/test_stage17_market_mapping.py`) verifies:
- Every supported market (1X2, Totals 0.5-4.5, BTTS, Correct Score) mapped correctly.
- Deterministic repeated execution stability.
- Probability bounds $[0, 1]$ and probability sum axioms.
- Correct score matrix distribution mapping.
- Explicit unsupported market rejections (Asian Handicap, Corners, Cards).
- Blocked forecast container and missing output handling.
- Full provenance retention.
- Complete absence of bookmaker odds, value calculation, or fabricated probabilities.

---

## 5. Stage Boundary & Limitations

1. **No Bookmaker Odds or Margin Removal**: Bookmaker odds ingestion and margin removal belong strictly to Stage 18.
2. **No Value / Edge / Kelly Calculation**: Expected value calculation and Kelly stake sizing belong strictly to Stage 18.
3. **No Risk / NO-BET Abstention Engine**: Risk decision trees and NO-BET logic belong strictly to Stage 18.
