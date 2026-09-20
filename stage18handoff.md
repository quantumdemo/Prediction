STAGE
Stage 18 — Risk, Confidence & NO-BET Engine

STATUS
COMPLETE

OBJECTIVE
To build the Risk, Confidence, and NO-BET Decision Engine on top of approved Stage 17 market probabilities and Stage 16 forecast outputs, evaluate prediction quality using measurable signals (probability strength, calibration status, evidence completeness, evidence conflicts, feature completeness, market support, data quality), define deterministic confidence tiers (`HIGH`, `MEDIUM`, `LOW`) and risk flags, implement `NO-BET` / `INSUFFICIENT_EVIDENCE` / `BLOCKED` as first-class decision outputs, block markets from recommendation when required evidence or data quality conditions fail, preserve complete provenance, and maintain strict architectural isolation without using bookmaker odds, calculating expected value edges, or determining Kelly stake sizes.

IMPLEMENTED
1. **Risk & NO-BET Engine (`services/ml/app/risk/engine.py`)**:
   - `RiskEngine`: Evaluates Stage 17 mapped markets and Stage 16 forecast containers.
   - Computes deterministic confidence scores ($C \in [0.0, 1.0]$) and confidence levels (`HIGH`, `MEDIUM`, `LOW`).
   - Attaches deterministic risk flags (`RISK_UNRESOLVED_EVIDENCE_CONFLICT`, `RISK_MISSING_KEY_FEATURE`, `RISK_LOW_TOP_PROBABILITY`, `RISK_UNSUPPORTED_MARKET`, `RISK_BLOCKED_FORECAST_CONTAINER`, `RISK_UNSUPPORTED_MODEL_CALIBRATION`).
   - Evaluates decision statuses (`ELIGIBLE`, `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`).
   - Treats `NO-BET` and `INSUFFICIENT_EVIDENCE` as first-class outputs when quality conditions fail.
2. **Risk Engine Schemas & Contracts (`services/ml/app/risk/schemas.py`)**:
   - `ConfidenceLevel`, `DecisionStatus`, `RiskFlag`, `MarketDecision`, `RiskEngineReport`.
3. **Unit Test Suite (`services/ml/tests/test_stage18_risk_engine.py`)**:
   - 13 unit tests covering valid market ELIGIBLE status, low probability LOW_CONFIDENCE, high risk conditions, insufficient evidence NO-BET, conflicting evidence flagging, missing features, invalid probability, unsupported market blocking, blocked forecast container, deterministic confidence calculation, deterministic risk flags, correct NO-BET/blocked decisions, provenance preservation, no fabricated values, no bookmaker odds, and no expected value edge calculation.

RESEARCH PERFORMED
- Formulated numerical confidence scoring formulas incorporating top outcome probability signals, calibration state bonuses, missing feature penalties, and evidence conflict penalties.
- Defined explicit risk flag decision trees for market abstention.

FILES CREATED
- `services/ml/app/risk/__init__.py`
- `services/ml/app/risk/schemas.py`
- `services/ml/app/risk/engine.py`
- `services/ml/tests/test_stage18_risk_engine.py`
- `docs/STAGE18_RISK_NO_BET_ENGINE.md`
- `stage18handoff.md`

FILES MODIFIED
None. All new Stage 18 code was implemented in modular packages without modifying earlier stages.

DATABASE CHANGES
None. Stage 18 operates as an in-memory FastAPI ML service layer and exports structured Pydantic risk reports.

DATA SOURCES
- Stage 17 Mapped Market Reports (`MappedMarketReport`)
- Stage 16 Current Match Forecast Containers (`CurrentMatchForecastContainer`)

DATASETS
- Evaluated risk decision reports (`RiskEngineReport`) with complete provenance summaries.

TESTS RUN
- `services/ml/tests/test_stage18_risk_engine.py` (13 test cases)
- `services/ml/tests/` (All 107 ML test cases total)
- `tests/` (All 52 platform architecture test cases)

TEST RESULTS
All 159 unit and integration tests passed (107 ML tests + 52 platform architecture tests = 159 total tests, 100% success rate).

ACCEPTANCE CRITERIA
- [x] Accepts validated Stage 17 market probabilities and provenance.
- [x] Evaluates prediction quality using probability strength, calibration status, evidence completeness, evidence conflicts, feature completeness, forecast status, and market support.
- [x] Defines deterministic confidence categories (`HIGH`, `MEDIUM`, `LOW`) based on numerical rules.
- [x] Defines deterministic risk flags based on documented conditions.
- [x] Implements NO-BET / INSUFFICIENT EVIDENCE as a first-class output.
- [x] Blocks market from recommendation when required evidence, model output, or market mapping conditions fail.
- [x] Never converts low confidence into a high-confidence result.
- [x] Never manufactures a probability, confidence value, risk value, or missing evidence.
- [x] Preserves complete provenance (source forecast, market, probability, evidence status, feature status, model/version, confidence calculation, risk flags, decision status, decision reasons).
- [x] Decision engine is 100% deterministic and auditable.
- [x] Did NOT use bookmaker odds.
- [x] Did NOT calculate expected value, edge, stake size, bankroll management, or betting returns.
- [x] Did NOT modify underlying ML models, calibration, feature engineering, or market mapping.
- [x] Supports explicit outcomes (`ELIGIBLE`, `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, `BLOCKED`).
- [x] Added tests covering valid market ELIGIBLE status, low probability/confidence, high risk, insufficient evidence, conflicting evidence, incomplete features, invalid probability, unsupported market, blocked forecast, deterministic confidence calculation, deterministic risk flags, correct NO-BET/blocked decisions, provenance preservation, no fabricated values, no bookmaker odds, and no edge/value calculation.
- [x] Stage 19+ not started.

SECURITY
- Zero hardcoded secrets, credentials, or API keys.
- Inputs validated via strict Pydantic models.

KNOWN LIMITATIONS
- Decision engine operates on risk thresholds ($C \ge 0.65$); user-configurable risk appetite profiles can be integrated via API settings in future stages.
- Auditable PostgreSQL database persistence belongs strictly to Stage 19.

UNRESOLVED ISSUES
NONE

TECHNICAL DECISIONS
- **Deterministic Confidence Formula**: Base confidence derived from Stage 13 calibration status ($0.70$ for Platt-calibrated, $0.50$ for uncalibrated) combined with top outcome probability signal ($+ 0.20 \times P_{\text{max}}$) and penalties for missing features or evidence conflicts.
- **First-Class Abstention**: Treating `LOW_CONFIDENCE`, `HIGH_RISK`, `INSUFFICIENT_EVIDENCE`, and `BLOCKED` as first-class decision outputs guarantees the system abstains from betting recommendations whenever data quality or model confidence is insufficient.

ENVIRONMENT VARIABLES
None required for Stage 18.

DEPLOYMENT STATUS
ML FastAPI boundary service ready. Risk, Confidence & NO-BET Engine ready for downstream auditable reporting (Stage 19) and prediction integration (Stage 20).

GIT STATUS
Branch: `jules-5762434063432475576-cd127c6d`
All new Stage 18 files untracked/staged cleanly.

NEXT RECOMMENDED STAGE
Stage 19 — Auditable Reporting Engine

BLOCKERS
NONE
