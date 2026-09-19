STAGE
Stage 15 — Evidence Validation + Provenance

STATUS
COMPLETE

OBJECTIVE
To build the platform's Evidence Validation Engine on top of the approved Stage 14 web research layer to deterministically validate every current-match evidence item, enforce source validity, URL validity, timestamp freshness, claim completeness, entity/fixture association, duplicate detection, and contradiction flagging while preserving full provenance, explicit research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`), and SHA256 auditability without converting missing or uncertain evidence into verified data or modifying probability models.

IMPLEMENTED
1. **Evidence Validation Engine (`services/ml/app/evidence/validator.py`)**:
   - `EvidenceValidationEngine`: Deterministically checks source domain allowlists, URL validity (`http://`/`https://`), timestamp freshness (retrieval within 7 days of match), claim completeness, entity association, deduplication via claim hashes, and conflict flagging.
   - Calculates deterministic SHA256 `audit_trail_hash` for complete report auditability.
2. **Evidence Validation Schemas & Contracts (`services/ml/app/evidence/schemas.py`)**:
   - `ValidationOutcome` enum (`ACCEPTED`, `DOWNGRADED`, `REJECTED`, `FLAGGED_CONFLICT`).
   - `ValidationReason` enum (`VALID_PRIMARY_SOURCE`, `UNALLOWLISTED_SOURCE`, `STALE_TIMESTAMP`, `MISSING_TIMESTAMP`, `INVALID_URL`, `EMPTY_CLAIM`, `WRONG_ENTITY_ASSOCIATION`, `DUPLICATE_EVIDENCE`, `CONTRADICTORY_EVIDENCE`).
   - `ValidatedEvidenceItem` and `EvidenceValidationReport` Pydantic models.
3. **Unit Test Suite (`services/ml/tests/test_stage15_evidence_validation.py`)**:
   - 12 unit tests covering valid evidence, invalid source, invalid URL, stale evidence, missing timestamp, duplicate evidence, conflicting evidence, wrong fixture/entity, empty claim, provenance retention, deterministic validation, and rejection of fabricated data.

RESEARCH PERFORMED
- Researched domain allowlist credibility hierarchies across major sports news portals (`bbc.com`, `skysports.com`, official club websites).
- Formulated deterministic freshness threshold rules (7 days for retrieval, 14 days for publication prior to kickoff).

FILES CREATED
- `services/ml/app/evidence/__init__.py`
- `services/ml/app/evidence/schemas.py`
- `services/ml/app/evidence/validator.py`
- `services/ml/tests/test_stage15_evidence_validation.py`
- `docs/STAGE15_EVIDENCE_VALIDATION.md`
- `stage15handoff.md`

FILES MODIFIED
None. All new Stage 15 code was implemented in modular packages without modifying earlier stages.

DATABASE CHANGES
None. Stage 15 operates as an in-memory FastAPI ML service layer and exports structured Pydantic / JSON validation reports.

DATA SOURCES
- Stage 14 Research Reports (`ResearchReport`)
- Default Credible Source Allowlist (`ALLOWLISTED_DOMAINS`)

DATASETS
- Validated current-match evidence reports with full provenance attributes and SHA256 audit hashes.

TESTS RUN
- `services/ml/tests/test_stage15_evidence_validation.py` (12 test cases)
- `services/ml/tests/` (All 70 ML test cases total)
- `tests/` (All 52 platform architecture test cases)

TEST RESULTS
All 122 unit and integration tests passed (70 ML tests + 52 platform architecture tests = 122 total tests, 100% success rate).

ACCEPTANCE CRITERIA
- [x] Validates every current-match evidence item before downstream use.
- [x] Checks source validity, URL validity, retrieval timestamp, claim completeness, fixture/entity association, evidence freshness, duplicate evidence, and conflicting evidence.
- [x] Preserves full provenance (source, URL, retrieval timestamp, claim, fixture/entity, validation outcome, validation reasons).
- [x] Preserves existing research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`).
- [x] Never silently converts uncertain, conflicting, stale, or missing evidence into verified data.
- [x] Establishes deterministic rules for accepted, downgraded, rejected, and flagged conflict items.
- [x] Validation results are auditable and reproducible via SHA256 audit trail hashes.
- [x] Evidence validation kept strictly separate from feature engineering, model training, probability generation, calibration, market mapping, odds, and risk/NO-BET logic.
- [x] Added tests covering valid evidence, invalid source, invalid URL, stale evidence, missing timestamp, duplicate evidence, conflicting evidence, wrong fixture/entity, unsupported claim, provenance retention, deterministic validation, and rejection of fabricated data.
- [x] Stage 16+ not started.

SECURITY
- Strict URL protocol filtering: Rejects non-HTTP/HTTPS URLs (e.g. `ftp://`, `file://`, local paths) preventing Server-Side Request Forgery (SSRF).
- Zero hardcoded secrets, API keys, or credentials.

KNOWN LIMITATIONS
- Domain allowlist is configured in code (`ALLOWLISTED_DOMAINS`); dynamic database-driven domain allowlists can be integrated via PostgreSQL in future stages.
- Merging validated evidence items into numerical pre-match feature vectors belongs strictly to Stage 16.

UNRESOLVED ISSUES
NONE

TECHNICAL DECISIONS
- **Deterministic Outcome Classification**: `ValidationOutcome` (`ACCEPTED`, `DOWNGRADED`, `REJECTED`, `FLAGGED_CONFLICT`) provides transparent, rule-based decision trees for downstream feature update pipelines.
- **SHA256 Audit Trail Hashes**: Computing SHA256 hashes over sorted validated item JSON blobs guarantees 100% auditable and reproducible validation reports.

ENVIRONMENT VARIABLES
None required for Stage 15.

DEPLOYMENT STATUS
ML FastAPI boundary service ready. Evidence validation engine ready for current match research validation.

GIT STATUS
Branch: `jules-5762434063432475576-cd127c6d`
All new Stage 15 files untracked/staged cleanly.

NEXT RECOMMENDED STAGE
Stage 16 — Current Feature Update Pipeline

BLOCKERS
NONE
