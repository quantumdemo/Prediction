# MASTER CONTROL SPECIFICATION
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### SINGLE SOURCE OF TRUTH

This document is the MASTER CONTROL SPECIFICATION for the Football AI Intelligence & Machine-Learning Platform. It is the SINGLE SOURCE OF TRUTH for the project.

- Do not replace it with another specification.
- Do not silently modify its principles.
- Do not simplify away difficult components.
- Do not jump ahead to later stages.
- Do not claim a stage is complete when its acceptance criteria have not been satisfied.
- If a technical decision conflicts with this specification, stop and report the conflict instead of silently changing the specification.

---

### SECTION 1: MASTER CONTROL SPECIFICATION (FOUNDATIONAL SECTIONS 1–29)

#### 1. CORE PRODUCT
A user enters a real football match.
The system must:
1. Verify the fixture.
2. Identify the correct teams and competition.
3. Gather legitimate historical football data.
4. Gather current match information from legitimate public sources.
5. Validate all collected information.
6. Preserve source/provenance and timestamps.
7. Engineer reproducible football features.
8. Use trained statistical/ML models to generate probabilities.
9. Calibrate and evaluate those probabilities.
10. Map forecasts to supported football markets.
11. Evaluate data quality, model reliability, uncertainty, and risk.
12. Return an evidence-backed prediction OR NO BET / INSUFFICIENT EVIDENCE.
13. Store an auditable record of the prediction and evidence.
The system produces probabilities, not certainty.

#### 2. FUNDAMENTAL ARCHITECTURE
Keep these logically separate:
A. Historical football data
B. Current-match web research
C. Data validation/evidence
D. Feature engineering
E. Statistical/ML forecasting
F. Market mapping
G. Risk/confidence/abstention
H. Reporting/audit

Web research does NOT directly produce prediction probabilities.
The LLM may assist with: extracting information from unstructured sources, structuring information, resolving aliases, classifying evidence, summarizing evidence, identifying contradictions.
The LLM MUST NOT invent numerical probabilities. Numerical forecasts MUST come from the statistical/ML forecasting engine.

#### 3. REAL DATA ONLY
Production predictive functionality must use real football data.
Never fabricate: match results, goals, xG, shots, shots on target, possession, corners, cards, fouls, offsides, injuries, suspensions, lineups, player statistics, league positions, fixtures, sources, historical records, probabilities.
If information is unavailable, represent it as unavailable/missing and handle it explicitly.
Never silently substitute fake/default football values.
Development fixtures or synthetic data may only be used for automated software tests where clearly isolated from production predictive datasets and explicitly labelled as test data.

#### 4. FOOTBALL ENTITY SYSTEM
Team names are identifiers, not predictive features.
The system must support canonical identifiers for: countries, competitions, seasons, clubs, players, matches.
Support: canonical names, aliases, external provider IDs where legally/technically available, country, competition membership, season membership, historical identity information.
Never use popularity, prestige, reputation, badge value, fanbase size, or media fame as predictive features. Team strength must be learned mathematically from football performance.

#### 5. FIXTURE VERIFICATION
Before forecasting a match, verify where possible: home team, away team, competition, season, date, kickoff, venue, match status, canonical team identifiers, fixture identity.
If the fixture cannot be reliably verified: STOP. Return an appropriate verification failure rather than guessing.

#### 6. HISTORICAL DATA
Where genuinely available, support: match results, goals for/against, home/away performance, shots, shots on target, possession, corners, cards, fouls, offsides, xG/xGA, BTTS, clean sheets, rest days, fixture congestion, opponent strength, competition context, player information, and other validated football statistics.

#### 7. CURRENT MATCH RESEARCH
For a verified upcoming match, research current information where legitimately available: recent form, current league position, injuries, suspensions, expected/confirmed lineups, manager information, tactical changes, fixture congestion, rest, travel/context, relevant H2H, current team news, credible public discussion, other relevant current evidence.
Every evidence item must retain: source, source URL where available, publication time/date where available, retrieval timestamp, evidence classification, validation status.

#### 8. DATA VALIDATION
Information must be classified using explicit states: VERIFIED, LIKELY, UNCERTAIN, CONFLICTING, UNAVAILABLE.
Validate: source quality, freshness, correctness, duplicates, contradictions, impossible values, missing values, identity matching.
Do not silently resolve contradictory information. Contradictions must remain visible and affect reliability where appropriate.

#### 9. FEATURE ENGINEERING
Create reproducible numerical features: recent form, home/away strength, goals for/against, xG/xGA, shots, shots on target, possession, corners, cards, fouls, offsides, rest, opponent strength, injuries, player availability, tactical indicators, competition context.
NO FUTURE-DATA LEAKAGE. A feature may only use information available at the time the prediction would actually have been made.

#### 10. FORECASTING ENGINE
Build a genuine forecasting system (Poisson, Dixon-Coles, Logistic Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM). Model selection must be evidence-based.
The system must output probabilities. Numerical forecasts MUST originate from the forecasting engine.

#### 11. TIME-AWARE VALIDATION
Do NOT randomly mix future matches into training. Use chronological/time-aware validation (Log Loss, Brier Score, MAE, RMSE, calibration).

#### 12. PROBABILITY CALIBRATION
Forecast probabilities must be calibrated (Platt scaling, isotonic regression). Models, datasets, feature versions, calibration methods, and evaluation results must be versioned.

#### 13. MARKET SYSTEM
Market catalogue defines supported markets and selection rules. It is NOT a prediction source. Do NOT allow bookmaker odds to become predictive inputs.

#### 14. SPECIALIST MARKETS
Potential specialist markets: goals, BTTS, corners, cards, offsides, fouls, shots, player markets, correct score. Activated ONLY when data, models, calibration, and historical validation are sufficient.

#### 15. RISK, CONFIDENCE AND NO BET
NO BET is a first-class output. Assess data quality, missing information, model reliability, model disagreement, lineup uncertainty, conflicting sources. If reliability is insufficient: NO BET / INSUFFICIENT EVIDENCE.

#### 16. AUDITABILITY
Every prediction must store: match identity, prediction timestamp, current evidence, source URLs, timestamps, features, feature version, dataset version, model version, calibration version, model probabilities, market probabilities, risk assessment, NO-BET decision.

#### 17. WEBSITE
Professional AI/data/analytics interface. NOT a sportsbook or casino.

#### 18. VERCEL DEPLOYMENT
Distinguish between UI, web/API layer, database, data ingestion, scheduled jobs, ML training, ML inference, web research, storage.

#### 19. SECURITY
Never expose secrets or DB credentials in client-side code. Server-side execution only for sensitive operations.

#### 20. VERSIONING
Version datasets, schemas, feature definitions, models, calibration, market definitions, prediction pipeline.

#### 21. TESTING
Automated testing for each stage (unit, integration, schema, data quality, ML, calibration, leakage).

#### 22. DATA AND RESEARCH RULE
Research unestablished information; never guess or bypass licensing/access restrictions.

#### 23. DEVELOPMENT STAGES
Strict stage execution from STAGE 1 through STAGE 26.

#### 24. STAGE CONTROL
Work ONLY on current stage.

#### 25. COMPLETION STANDARD
COMPLETE = IMPLEMENTED + TESTED + VERIFIED + DOCUMENTED + ACCEPTANCE CRITERIA PASSED.

#### 26. NO INVENTION RULE
Never manufacture certainty or substitute fake/default data.

#### 27. STANDARD STAGE HANDOFF REPORT
Use exact 27-section schema for stage handoff reports.

#### 28. COMMUNICATION RULE
Be factual and technical. Report measurable facts.

#### 29. MASTER PRINCIPLE
DATA INTEGRITY → SCIENTIFIC VALIDITY → REPRODUCIBILITY → AUDITABILITY → SAFETY → RELIABILITY → PRODUCT QUALITY.

---

### SECTION 2: FORMAL PLATFORM REQUIREMENTS DOCUMENT

#### 2.1 FUNCTIONAL REQUIREMENTS
- **REQ-FUNC-001**: System shall accept match requests (Home Team, Away Team, Competition, Date/Kickoff).
- **REQ-FUNC-002**: System shall perform fixture verification against canonical fixture databases before processing.
- **REQ-FUNC-003**: System shall trigger web research for upcoming verified matches to extract current team news, injuries, and lineups.
- **REQ-FUNC-004**: System shall compute match probabilities strictly via statistical/ML forecasting engines.
- **REQ-FUNC-005**: System shall issue `NO BET / INSUFFICIENT EVIDENCE` when safety/quality conditions are violated.
- **REQ-FUNC-006**: System shall display prediction audit details including probability breakdown, evidence list, and feature snapshots.

#### 2.2 DATA REQUIREMENTS
- **REQ-DATA-001**: Historical data must store match results, goals, shots, corners, cards, fouls, and xG where available.
- **REQ-DATA-002**: Data ingestion MUST reject synthetic/default values in production pipelines.
- **REQ-DATA-003**: Entity Resolution System must maintain canonical IDs and alias tables for clubs, competitions, players, and venues.
- **REQ-DATA-004**: System must preserve exact source URL, retrieval timestamp, and raw payload for all ingested data.
- **REQ-DATA-005**: Explicit data state classification (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`) must be attached to all evidence items.

#### 2.3 MACHINE LEARNING REQUIREMENTS
- **REQ-ML-001**: Models must generate discrete outcome probabilities (Home, Draw, Away, Totals, BTTS).
- **REQ-ML-002**: LLMs MUST NOT invent or output numerical outcome probabilities directly.
- **REQ-ML-003**: Training data MUST use chronological time-aware splits (`event_timestamp < cutoff_timestamp`).
- **REQ-ML-004**: All features must strictly enforce zero future-data leakage (`feature_timestamp <= prediction_cutoff`).
- **REQ-ML-005**: Forecast probabilities MUST undergo probability calibration (Platt scaling / Isotonic regression) and evaluate Brier Score & Log Loss.
- **REQ-ML-006**: Model performance metrics (Log Loss, Brier Score, Calibration Error) must be tracked per model version and competition.

#### 2.4 WEB RESEARCH REQUIREMENTS
- **REQ-WEB-001**: Web research engine must collect news, injury updates, suspension notices, and press conferences for verified fixtures.
- **REQ-WEB-002**: Web research must output structured JSON containing source URL, retrieval timestamp, publication timestamp, and extracted facts.
- **REQ-WEB-003**: LLM parsing must classify information reliability and flag contradictions between sources.

#### 2.5 EVIDENCE AND PROVENANCE REQUIREMENTS
- **REQ-EVID-001**: Every current evidence item must link to an immutable source URL and retrieval timestamp.
- **REQ-EVID-002**: Contradictory evidence between sources must be preserved explicitly rather than merged or hidden.
- **REQ-EVID-003**: Evidence freshness scores must decay as match kickoff approaches.

#### 2.6 MARKET REQUIREMENTS
- **REQ-MKT-001**: Market catalogue shall define market types (1X2, Over/Under Goals, Both Teams To Score, Asian Handicap, Corners, Cards).
- **REQ-MKT-002**: Market Mapping Engine shall convert underlying match probabilities into market selections.
- **REQ-MKT-003**: Specialist markets shall remain INACTIVE until model validation and data density meet acceptance criteria.
- **REQ-MKT-004**: Bookmaker odds MUST NOT be used as predictive inputs in forecasting models.

#### 2.7 RISK AND NO-BET REQUIREMENTS
- **REQ-RISK-001**: System must calculate a composite Risk & Confidence Index prior to issuing predictions.
- **REQ-RISK-002**: System MUST return `NO BET / INSUFFICIENT EVIDENCE` if data completeness is below threshold or key player availability is uncertain.
- **REQ-RISK-003**: System MUST return `NO BET / INSUFFICIENT EVIDENCE` if model disagreement across ensemble members exceeds threshold.
- **REQ-RISK-004**: System MUST return `NO BET / INSUFFICIENT EVIDENCE` if probability calibration is unverified for the competition.

#### 2.8 REPORTING AND AUDIT REQUIREMENTS
- **REQ-REP-001**: System shall generate immutable audit records for every prediction request.
- **REQ-REP-002**: Audit records must store feature values, dataset version, model version, calibration version, evidence links, and risk scores.
- **REQ-REP-003**: Historical predictions must remain immutable and accessible for post-match evaluation.

#### 2.9 SECURITY REQUIREMENTS
- **REQ-SEC-001**: Server-only environment variables (API credentials, database connection strings) must never be exposed to the client/frontend.
- **REQ-SEC-002**: Admin, model training, and re-indexing endpoints must require secure authentication.
- **REQ-SEC-003**: All incoming client API inputs must be sanitized and validated against standard JSON schemas.

#### 2.10 TESTING REQUIREMENTS
- **REQ-TEST-001**: Automated unit tests must achieve test coverage across core feature engineering, data cleaning, and risk logic.
- **REQ-TEST-002**: Data leakage tests must verify that post-match statistics are impossible to ingest at prediction cutoff time.
- **REQ-TEST-003**: Synthetic/mock data used in automated tests must be strictly isolated from production inference pipelines.

#### 2.11 DEPLOYMENT REQUIREMENTS
- **REQ-DEP-001**: Web frontend and API layer shall be deployed on Vercel infrastructure.
- **REQ-DEP-002**: Heavy ML model training and background data ingestion tasks shall execute on dedicated async background infrastructure/workers separate from Vercel edge functions.
- **REQ-DEP-003**: Database migrations must be automated, versioned, and reversible.

#### 2.12 MONITORING REQUIREMENTS
- **REQ-MON-001**: System shall log all data ingestion failures, API response times, and model inference latencies.
- **REQ-MON-002**: Data drift and prediction calibration drift must be tracked across seasons and competitions.

#### 2.13 VERSIONING REQUIREMENTS
- **REQ-VER-001**: Feature engineering schemas must use strict semantic versioning (`v1.0.0`).
- **REQ-VER-002**: Statistical and ML models must be stored with explicit model artifacts, hyperparameter logs, and version IDs.
- **REQ-VER-003**: Market catalogue definitions must be version-controlled.

---

### SECTION 3: SYSTEM BOUNDARIES

#### 3.1 INSIDE THE PLATFORM
- **Web Interface / Dashboard**: Analytics UI, prediction viewer, match analysis, model performance dashboard.
- **API Server / Gateway**: Web request handling, fixture lookup API, prediction request API, audit log reader.
- **Entity Resolution Engine**: Canonical identifier mapping, alias lookup, entity linking.
- **Data Ingestion & Cleaning Pipeline**: Public API fetchers, data scrubbers, schema validators, missing value flaggers.
- **Feature Engineering Engine**: Chronological feature extractors, rolling average engines, rest day calculator.
- **Statistical & ML Forecasting Engine**: Poisson, Dixon-Coles, XGBoost/LightGBM predictors, probability generators.
- **Probability Calibration Module**: Isotonic/Platt calibration models and Brier score calculators.
- **Market Mapping Engine**: Probability-to-market translation engine.
- **Risk & NO-BET Engine**: Multi-factor uncertainty calculator and abstention decision tree.
- **Auditable Prediction Storage**: Database tables storing prediction records, snapshots, feature vectors, and evidence provenance.

#### 3.2 OUTSIDE THE PLATFORM
- **External Football Data Providers**: Public APIs, stats databases, official league feeds.
- **External Web Sources & Search Engines**: Public web sites, sports news feeds, official team announcements.
- **Bookmaker Odds Aggregators**: Third-party odds feeds (used exclusively for post-hoc user visual reference, never as predictive inputs).
- **Vercel Serverless Platform**: Hosted edge functions (handling UI and light API queries only).
- **External ML Compute Infrastructure**: Async task workers for heavy offline model training.

---

### SECTION 4: DATA CONTRACT PRINCIPLES & DATA STATES

#### 4.1 DATA STATES
Every piece of data ingested into the system must be tagged with one of five explicit data states:
1. `VERIFIED`: Confirmed by multiple independent primary sources or official league feeds.
2. `LIKELY`: Sourced from a highly reputable secondary source with high historical reliability.
3. `UNCERTAIN`: Single source, unconfirmed report, or recent breaking update.
4. `CONFLICTING`: Contradictory reports exist between two or more reputable sources.
5. `UNAVAILABLE`: Information missing or unobtainable; explicitly represented as `NULL`.

#### 4.2 ZERO-FABRICATION RULE
- Default fallback values (e.g., assuming `0` goals, `50%` possession, or `average` team strength when data is missing) are strictly forbidden in production pipelines.
- Missing values MUST remain `NULL`. Downstream feature extractors must handle `NULL` gracefully using documented missingness flags.

---

### SECTION 5: ML GOVERNANCE & LEAKAGE PREVENTION

#### 5.1 CHRONOLOGICAL VALIDATION MANDATE
- All model training and validation splits MUST be strictly chronological (`training_end_date < validation_start_date`).
- K-fold cross-validation with randomized shuffles across time is prohibited.

#### 5.2 ZERO FUTURE-DATA LEAKAGE
- Features for fixture $M$ at time $t$ MUST NOT use any statistics, match events, lineups, or external information recorded after $t$.
- Ingestion pipelines must validate `event_timestamp <= prediction_cutoff_timestamp`.

#### 5.3 PROBABILITY SOURCE MANDATE
- All numerical predictions (win/draw/loss probabilities, goal expectations) MUST be generated by statistical/ML models.
- LLMs are prohibited from outputting numerical probabilities directly. LLM outputs are limited to structured text extraction, alias resolution, and evidence classification.

---

### SECTION 6: PREDICTION LIFECYCLE

```
[USER/SYSTEM MATCH REQUEST]
             │
             ▼
 [1. FIXTURE VERIFICATION] ──(Unverified)──► [VERIFICATION FAILURE / STOP]
             │
         (Verified)
             ▼
   [2. DATA COLLECTION]
             │
             ▼
   [3. DATA VALIDATION] ──(State Tagging: VERIFIED/UNCERTAIN/CONFLICTING)
             │
             ▼
 [4. FEATURE ENGINEERING] ──(Check Cutoff Timestamp / Leakage Guard)
             │
             ▼
  [5. MODEL FORECASTING] ──(Statistical / ML Engine)
             │
             ▼
 [6. CALIBRATION & EVAL]
             │
             ▼
   [7. MARKET MAPPING]
             │
             ▼
  [8. RISK ASSESSMENT] ──(Uncertainty / Disagreement / Quality Check)
             │
    ┌────────┴────────┐
    ▼                 ▼
(Safe)           (High Risk / Data Gap)
    │                 │
    ▼                 ▼
[PREDICTION]     [NO BET / INSUFFICIENT EVIDENCE]
    │                 │
    └────────┬────────┘
             ▼
 [9. AUDIT LOG STORAGE] ──► [IMMUTABLE PREDICTION DB RECORD]
```

---

### SECTION 7: NO-BET GOVERNANCE

The system MUST issue `NO BET / INSUFFICIENT EVIDENCE` under any of the following conditions:
1. **Fixture Verification Defect**: Fixture entity cannot be resolved to canonical club/competition IDs.
2. **Data Completeness Defect**: Critical historical statistics (e.g., minimum match history) are below threshold.
3. **Severe Evidence Uncertainty**: Lineup or key player status is `UNCERTAIN` or `CONFLICTING` close to kickoff.
4. **Feature Availability Defect**: Core model features contain `NULL` values without valid imputation models.
5. **Model Reliability Defect**: Ensemble model variance/disagreement exceeds threshold.
6. **Uncalibrated Model Context**: Competition or market lacks historical calibration validation.
7. **High Risk Index**: Composite risk score exceeds allowable threshold.

---

### SECTION 8: MARKET GOVERNANCE

- The Market Catalogue defines market types, selection rules, and settlement criteria.
- Market engines map underlying statistical probabilities (e.g., Poisson lambda matrix) to market selections (e.g., Over 2.5 Goals).
- Market definitions DO NOT influence model training or probability generation.
- Bookmaker odds MUST NOT be supplied as predictive features into forecasting models.

---

### SECTION 9: DATA SOURCE GOVERNANCE

Selection of data sources must adhere to:
1. **Legitimacy & Licensing**: Only publicly available or legally licensed data feeds.
2. **Provenance Tracking**: Every record must retain source URL, provider name, and ingestion timestamp.
3. **Failure Resilience**: Ingestion pipelines must gracefully log provider outages without injecting fake fallback data.

---

### SECTION 10: REQUIREMENTS TRACEABILITY MATRIX

| Master Requirement ID | Category | Target Stage | Verification Method |
| :--- | :--- | :--- | :--- |
| REQ-FUNC-001 | Functional | Stage 8 / 20 | Integration Test |
| REQ-FUNC-002 | Functional | Stage 8 | Unit / Identity Test |
| REQ-DATA-001 | Data | Stage 4 / 6 | Schema Test |
| REQ-DATA-002 | Data | Stage 7 | Data Quality Test |
| REQ-DATA-003 | Data | Stage 8 | Entity Resolution Test |
| REQ-ML-001 | Machine Learning | Stage 10 / 11 | Model Unit Test |
| REQ-ML-002 | Machine Learning | Stage 14 / 15 | Prompt / Output Test |
| REQ-ML-003 | Machine Learning | Stage 12 | Backtest Split Test |
| REQ-ML-004 | Machine Learning | Stage 9 / 12 | Data Leakage Guard Test |
| REQ-ML-005 | Machine Learning | Stage 13 | Calibration Test |
| REQ-WEB-001 | Web Research | Stage 14 | Research Engine Test |
| REQ-RISK-001 | Risk / NO-BET | Stage 18 | Risk Decision Tree Test |
| REQ-RISK-002 | Risk / NO-BET | Stage 18 | Abstention Logic Test |
| REQ-REP-001 | Reporting | Stage 19 | Audit Database Test |
| REQ-SEC-001 | Security | Stage 3 / 24 | Secret Scanner Test |
| REQ-DEP-001 | Deployment | Stage 3 / 23 | Vercel Build Test |

---

### SECTION 11: STAGE DEPENDENCY MAP (STAGES 1–26)

- **STAGE 1 — Specification & Constitution**: Requires Master Control Prompt. Produces system spec & constitution.
- **STAGE 2 — Architecture & Technology Research**: Requires Stage 1. Produces stack architecture & deployment plan.
- **STAGE 3 — Skeleton & Vercel Foundation**: Requires Stage 2. Produces app structure, CI/CD, and Vercel foundation.
- **STAGE 4 — Database Schema & Contracts**: Requires Stage 3. Produces DB schemas, migration scripts, and entity tables.
- **STAGE 5 — Data Source Strategy**: Requires Stage 4. Produces source research and provider acquisition strategy.
- **STAGE 6 — Historical Dataset Ingestion**: Requires Stage 5. Ingests raw historical football records.
- **STAGE 7 — Data Cleaning & Validation**: Requires Stage 6. Cleans, normalizes, and validates historical data.
- **STAGE 8 — Football Entity Identification**: Requires Stage 7. Resolves canonical IDs, clubs, players, and fixtures.
- **STAGE 9 — Feature Engineering Engine**: Requires Stage 8. Computes pre-match features with 0 leakage.
- **STAGE 10 — Statistical Baseline Forecasting**: Requires Stage 9. Implements Poisson/Dixon-Coles models.
- **STAGE 11 — Machine-Learning Forecasting**: Requires Stage 9 & 10. Implements ML predictors (XGBoost/LightGBM).
- **STAGE 12 — Time-Aware Backtesting**: Requires Stage 11. Evaluates models chronologically.
- **STAGE 13 — Probability Calibration**: Requires Stage 12. Calibrates output probabilities.
- **STAGE 14 — Current-Match Web Research**: Requires Stage 8. Ingests current match news, lineups, injuries.
- **STAGE 15 — Evidence Validation**: Requires Stage 14. Validates current evidence and flags conflicts.
- **STAGE 16 — Current Feature Update Pipeline**: Requires Stage 9 & 15. Merges current evidence into pre-match feature vectors.
- **STAGE 17 — Market Catalogue & Mapping**: Requires Stage 13 & 16. Maps probabilities to supported markets.
- **STAGE 18 — Risk, Confidence & NO-BET Engine**: Requires Stage 17. Evaluates uncertainty and outputs prediction/NO BET.
- **STAGE 19 — Auditable Reporting**: Requires Stage 18. Stores traceable audit records for predictions.
- **STAGE 20 — Complete Prediction Integration**: Requires Stages 1–19. Integrates complete end-to-end forecasting pipeline.
- **STAGE 21 — Full System Audit**: Requires Stage 20. Validates compliance across all specifications.
- **STAGE 22 — Shadow Testing**: Requires Stage 21. Runs system in live shadow prediction mode.
- **STAGE 23 — Infrastructure Hardening**: Requires Stage 22. Hardens DB, queues, and Vercel edge deployment.
- **STAGE 24 — Security & Failure Handling**: Requires Stage 23. Audits security, logging, and recovery protocols.
- **STAGE 25 — Private Beta Testing**: Requires Stage 24. Conducts controlled testing with beta users.
- **STAGE 26 — Public Launch**: Requires Stage 25. Live production monitoring and operation.

---

### SECTION 12: OPEN TECHNICAL QUESTIONS REGISTER

1. **QUESTION**: What primary open football data provider offers the highest completeness for historical xG and detailed match event statistics?
   - *Why It Matters*: Dictates feature availability for specialist ML models.
   - *Target Stage*: Stage 5 (Data Source Strategy).
   - *Required Evidence*: Benchmarking report covering coverage, historical depth, rate limits, and licensing.

2. **QUESTION**: How should long-running ML background jobs (training/ingestion) be decoupled from Vercel's serverless execution timeout limits?
   - *Why It Matters*: Vercel edge functions have 10–60s execution limits; heavy ML training requires longer execution.
   - *Target Stage*: Stage 2 (Architecture & Technology Research).
   - *Required Evidence*: Architectural spike evaluating background worker platforms (e.g., Modal, AWS Lambda, or dedicated background workers).

3. **QUESTION**: What empirical variance threshold across ensemble model forecasts best optimizes Brier score while maintaining acceptable abstention rates?
   - *Why It Matters*: Prevents over-abstention while maintaining high reliability.
   - *Target Stage*: Stage 18 (Risk Engine).
   - *Required Evidence*: Backtested risk/abstention tuning curve across historical seasons.

---

### SECTION 13: PROJECT RISK REGISTER

| Risk ID | Category | Risk Description | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **RISK-001** | Data Availability | Historical xG or line-up data unavailable for lower-tier competitions. | HIGH | Restrict model activation or issue `NO BET` for data-sparse competitions. |
| **RISK-002** | Data Leakage | Post-match statistics accidentally included in pre-match feature vectors. | CRITICAL | Enforce immutable timestamp cutoffs and automated data leakage unit tests. |
| **RISK-003** | Web Research | News/injury scraper returns false or contradictory lineup reports. | MEDIUM | Classify evidence as `UNCERTAIN` and trigger NO-BET if critical key players are uncertain. |
| **RISK-004** | Calibration | Models produce overconfident probabilities on unobserved league contexts. | HIGH | Apply isotonic regression and enforce NO-BET when calibration error > threshold. |
| **RISK-005** | Infrastructure | Vercel serverless execution limits hit during match research queries. | MEDIUM | Offload heavy research parsing to asynchronous task queues. |
