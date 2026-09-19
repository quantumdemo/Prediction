STAGE
Stage 17 — Market Catalogue + Mapping

STATUS
COMPLETE

OBJECTIVE
To build the Market Catalogue and Deterministic Mapping Layer on top of the approved Stage 16 forecast output, define a controlled catalogue of supported football markets (1X2, Over/Under Goals 0.5–4.5, BTTS, Correct Score Grid), map Stage 16 forecast probabilities into market probabilities using exact deterministic mathematical rules, enforce probability bounds $[0, 1]$ and complementary probability axioms ($\sum P = 1.0$), return explicit unsupported statuses for unsupported markets without inventing fake probabilities, preserve full traceability back to source forecasters, and maintain strict architectural separation from bookmaker odds, expected value edge calculations, risk scoring, and NO-BET decision logic.

IMPLEMENTED
1. **Controlled Market Catalogue (`services/ml/app/markets/catalogue.py`)**:
   - `CONTROLLED_MARKET_CATALOGUE`: Defines 8 supported markets (`MKT_1X2`, `MKT_OVER_UNDER_0_5`, `MKT_OVER_UNDER_1_5`, `MKT_OVER_UNDER_2_5`, `MKT_OVER_UNDER_3_5`, `MKT_OVER_UNDER_4_5`, `MKT_BTTS`, `MKT_CORRECT_SCORE`) and 3 unsupported markets (`MKT_ASIAN_HANDICAP`, `MKT_CORNER_TOTALS`, `MKT_CARD_TOTALS`).
   - Specifies canonical market IDs, market names, market types, required model outputs, calculation rules, and support statuses.
2. **Market Mapper Engine (`services/ml/app/markets/mapper.py`)**:
   - `MarketMapper`: Deterministically maps Stage 16 `CurrentMatchForecastContainer` probabilities into market outcome probabilities.
   - Enforces probability bounds $[0, 1]$ and sum axioms.
   - Handles matrix outcomes for Correct Score grid.
   - Returns explicit `is_supported=False` with `unsupported_reason` for unsupported or blocked markets without inventing fake probabilities.
   - Preserves complete provenance traceability.
3. **Market Schemas & Data Contracts (`services/ml/app/markets/schemas.py`)**:
   - `MappedMarketOutcome`, `MarketProvenanceRecord`, `MappedMarket`, `MappedMarketReport`.
4. **Unit Test Suite (`services/ml/tests/test_stage17_market_mapping.py`)**:
   - 12 unit tests covering every supported market, deterministic mapping, probability bounds, probability consistency, correct score distribution handling, unsupported markets, missing forecast output, invalid forecast input, provenance preservation, no bookmaker odds usage, no fabricated probabilities, and deterministic repeated execution.

RESEARCH PERFORMED
- Formulated market catalogue mappings and probability complementary sum axioms for multi-class and binary markets.
- Designed explicit rejection rules for unsupported derivative markets (Asian Handicap, Corners, Cards).

FILES CREATED
- `services/ml/app/markets/__init__.py`
- `services/ml/app/markets/catalogue.py`
- `services/ml/app/markets/schemas.py`
- `services/ml/app/markets/mapper.py`
- `services/ml/tests/test_stage17_market_mapping.py`
- `docs/STAGE17_MARKET_CATALOGUE.md`
- `stage17handoff.md`

FILES MODIFIED
None. All new Stage 17 code was implemented in modular packages without modifying earlier stages.

DATABASE CHANGES
None. Stage 17 operates as an in-memory FastAPI ML service layer and exports structured Pydantic market reports.

DATA SOURCES
- Stage 16 Current Match Forecast Containers (`CurrentMatchForecastContainer`)
- Controlled Market Catalogue (`CONTROLLED_MARKET_CATALOGUE`)

DATASETS
- Mapped market reports (`MappedMarketReport`) with complete provenance records.

TESTS RUN
- `services/ml/tests/test_stage17_market_mapping.py` (12 test cases)
- `services/ml/tests/` (All 94 ML test cases total)
- `tests/` (All 52 platform architecture test cases)

TEST RESULTS
All 146 unit and integration tests passed (94 ML tests + 52 platform architecture tests = 146 total tests, 100% success rate).

ACCEPTANCE CRITERIA
- [x] Defined controlled catalogue of supported football markets.
- [x] Supported markets derived mathematically from Stage 16 outputs (1X2, Over/Under 0.5–4.5, BTTS, Correct Score).
- [x] Every market defined with canonical market ID, name, type, required model output, calculation rule, support status, and description.
- [x] Mapped Stage 16 forecast probabilities into market probabilities using deterministic mathematical rules.
- [x] Never invented or fabricated market probabilities.
- [x] Did NOT use bookmaker odds.
- [x] Did NOT calculate value or expected value edge.
- [x] Did NOT introduce risk scoring or NO-BET logic.
- [x] Did NOT modify underlying statistical/ML models.
- [x] Unsupported or blocked markets return explicit unsupported status rather than fabricated probabilities.
- [x] Preserved full traceability (source forecast, model/version, market ID, mapping rule, resulting probability, validation status).
- [x] Added tests covering every supported market, deterministic mapping, probability bounds $[0,1]$, probability consistency, correct score distribution, unsupported markets, missing forecast output, invalid forecast input, provenance preservation, no bookmaker odds, no fabricated probabilities, and deterministic repeated execution.
- [x] Stage 18+ not started.

SECURITY
- Zero hardcoded secrets, credentials, or API keys.
- Input container validation via strict Pydantic schemas.

KNOWN LIMITATIONS
- Market catalogue supports standard pre-match outcome markets; complex player props or micro-betting markets are registered as unsupported.
- Bookmaker odds mapping, edge calculation, risk scoring, and NO-BET decision logic belong strictly to Stage 18.

UNRESOLVED ISSUES
NONE

TECHNICAL DECISIONS
- **Explicit Support Flags**: `is_supported=False` with `unsupported_reason` guarantees that unsupported markets fail gracefully with transparent diagnostic messages rather than returning default or fabricated probabilities.
- **Score Matrix Extraction**: `MKT_CORRECT_SCORE` extracts probabilities directly from the model joint distribution matrix $P(h, a)$, preserving exact score probability mass.

ENVIRONMENT VARIABLES
None required for Stage 17.

DEPLOYMENT STATUS
ML FastAPI boundary service ready. Market mapping engine ready for downstream risk and NO-BET engine integration.

GIT STATUS
Branch: `jules-5762434063432475576-cd127c6d`
All new Stage 17 files untracked/staged cleanly.

NEXT RECOMMENDED STAGE
Stage 18 — Risk, Confidence & NO-BET Engine

BLOCKERS
NONE
