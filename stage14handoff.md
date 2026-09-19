STAGE
Stage 14 — Current-Match Web Research Engine

STATUS
COMPLETE

OBJECTIVE
To build the platform's Current-Match Web Research Engine to verify upcoming fixture identity, collect and structure pre-match information across 12 fact categories with full source provenance (URL, retrieval timestamp), enforce explicit research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`), handle conflicting sources explicitly without fact fabrication or silent selection, and maintain strict architectural isolation from probability generation, feature engineering, odds, or risk/NO-BET logic.

IMPLEMENTED
1. **Current-Match Web Research Engine (`services/ml/app/research/engine.py`)**:
   - `CurrentMatchResearchEngine`: Processes pre-match research inputs across 12 fact categories.
   - Retains source provenance (source name, valid URL, UTC retrieval timestamp).
   - Classifies research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`).
   - Detects contradictions explicitly across opposing claims and records `contradiction_details`.
   - Tracks `unavailable_categories` explicitly without inventing synthetic data.
2. **Fixture Identity Verifier (`services/ml/app/research/verification.py`)**:
   - `FixtureVerifier`: Resolves raw team names ("Man Utd", "Arsenal") and competition aliases ("EPL") to canonical platform UUIDs (`CLUB_ENG_MANCHESTER_UNITED`, `COMP_ENG_PL`).
   - Verifies match date, kickoff time, venue, and status against canonical standards.
3. **Data Contracts & Pydantic Schemas (`services/ml/app/research/schemas.py`)**:
   - `FixtureVerification`, `ResearchItem`, `ResearchReport`, `ResearchState`, `FactCategory`.
4. **Unit Test Suite (`services/ml/tests/test_stage14_web_research.py`)**:
   - 9 test cases verifying fixture verification, alias resolution, provenance capture, explicit research states, contradiction detection, unavailable categories, invalid input rejection, and probability isolation.

RESEARCH PERFORMED
- Researched team and competition name alias mapping patterns across major European leagues and international competitions.
- Evaluated contradiction detection logic for opposing player status claims (e.g. OUT vs FIT) across multiple news sources.

FILES CREATED
- `services/ml/app/research/__init__.py`
- `services/ml/app/research/schemas.py`
- `services/ml/app/research/verification.py`
- `services/ml/app/research/engine.py`
- `services/ml/tests/test_stage14_web_research.py`
- `docs/STAGE14_WEB_RESEARCH_ENGINE.md`
- `stage14handoff.md`

FILES MODIFIED
None. All new Stage 14 code was implemented in modular packages without modifying earlier stages.

DATABASE CHANGES
None. Stage 14 operates as an in-memory FastAPI ML service layer and exports structured Pydantic / JSON research reports.

DATA SOURCES
- Web research evidence inputs
- Canonical platform entity alias maps (`KNOWN_TEAM_ALIASES`, `KNOWN_COMPETITION_ALIASES`)

DATASETS
- Pre-match evidence items categorized into 12 fact categories with provenance metadata.

TESTS RUN
- `services/ml/tests/test_stage14_web_research.py` (9 test cases)
- `services/ml/tests/` (All 58 ML test cases total)
- `tests/` (All 52 platform architecture test cases)

TEST RESULTS
All 110 unit and integration tests passed (58 ML tests + 52 platform architecture tests = 110 total tests, 100% success rate).

ACCEPTANCE CRITERIA
- [x] Verifies fixture identity (home/away team, competition, season, date, kickoff time, venue, status, canonical IDs).
- [x] Collects current pre-match information across 12 fact categories.
- [x] Every research item retains source name, valid URL, and UTC retrieval timestamp.
- [x] Implements explicit research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`).
- [x] Handles conflicting sources explicitly without silently inventing or picking a claim.
- [x] Rejects invalid URLs, empty claims, or synthetic/fabricated football data.
- [x] LLM and research engine generate zero prediction probabilities.
- [x] Web research kept strictly separate from historical datasets, feature engineering, model training, probability calibration, market mapping, and risk/NO-BET logic.
- [x] Final prediction pipeline, betting markets, odds, value detection, and NO-BET logic NOT built.
- [x] Added tests for fixture verification, provenance capture, timestamps, conflicts, unavailable info, alias resolution, and rejection of fabricated values.
- [x] Stage 15+ not started.

SECURITY
- Server-Side Request Forgery (SSRF) controls: URL validation requires strict `http://` or `https://` protocol prefixes.
- Zero hardcoded secrets, credentials, or API keys.

KNOWN LIMITATIONS
- Research engine operates on structured/parsed text evidence inputs; live HTML web scraper connectors can be wired to headless scrapers or RSS feeds in production deployment.
- Evidence item merging and cross-evidence conflict resolution across updated features belongs to Stage 15 and Stage 16.

UNRESOLVED ISSUES
NONE

TECHNICAL DECISIONS
- **Explicit Research States**: `ResearchState` enum (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`) ensures downstream stages know the exact evidence confidence without hidden assumptions.
- **Canonical Alias Resolution**: `FixtureVerifier` resolves ambiguous strings ("Man Utd", "EPL") to immutable UUIDs (`CLUB_ENG_MANCHESTER_UNITED`, `COMP_ENG_PL`) prior to research aggregation.

ENVIRONMENT VARIABLES
None required for Stage 14.

DEPLOYMENT STATUS
ML FastAPI boundary service ready. Research engine and verifier ready for live current match evidence ingestion.

GIT STATUS
Branch: `jules-5762434063432475576-cd127c6d`
All new Stage 14 files untracked/staged cleanly.

NEXT RECOMMENDED STAGE
Stage 15 — Evidence Validation Engine

BLOCKERS
NONE
