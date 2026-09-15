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

### 1. CORE PRODUCT

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

---

### 2. FUNDAMENTAL ARCHITECTURE

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
The LLM may assist with:
- extracting information from unstructured sources
- structuring information
- resolving aliases
- classifying evidence
- summarizing evidence
- identifying contradictions

The LLM MUST NOT invent numerical probabilities.
Numerical forecasts MUST come from the statistical/ML forecasting engine.

---

### 3. REAL DATA ONLY

Production predictive functionality must use real football data.

Never fabricate:
- match results, goals, xG, shots, shots on target, possession, corners, cards, fouls, offsides, injuries, suspensions, lineups, player statistics, league positions, fixtures, sources, historical records, probabilities.

If information is unavailable, represent it as unavailable/missing and handle it explicitly.
Never silently substitute fake/default football values.
Development fixtures or synthetic data may only be used for automated software tests where clearly isolated from production predictive datasets and explicitly labelled as test data.

---

### 4. FOOTBALL ENTITY SYSTEM

Team names are identifiers, not predictive features.

The system must support canonical identifiers for:
- countries
- competitions
- seasons
- clubs
- players
- matches

Support:
- canonical names
- aliases
- external provider IDs where legally/technically available
- country
- competition membership
- season membership
- historical identity information

Never use popularity, prestige, reputation, badge value, fanbase size, or media fame as predictive features.
Team strength must be learned mathematically from football performance.

---

### 5. FIXTURE VERIFICATION

Before forecasting a match, verify where possible:
- home team
- away team
- competition
- season
- date
- kickoff
- venue
- match status
- canonical team identifiers
- fixture identity

If the fixture cannot be reliably verified: STOP. Return an appropriate verification failure rather than guessing.

---

### 6. HISTORICAL DATA

Where genuinely available, the system should support:
- match results, goals for/against, home/away performance, shots, shots on target, possession, corners, cards, fouls, offsides, xG/xGA, BTTS, clean sheets, rest days, fixture congestion, opponent strength, competition context, player information, and other validated football statistics.

Data availability must be documented. Do not assume that every source provides every variable.

---

### 7. CURRENT MATCH RESEARCH

For a verified upcoming match, research current information where legitimately available:
- recent form, current league position, injuries, suspensions, expected/confirmed lineups, manager information, tactical changes, fixture congestion, rest, travel/context, relevant H2H, current team news, credible public discussion, other relevant current evidence.

Every important evidence item must retain:
- source, source URL where available, publication time/date where available, retrieval timestamp, evidence classification, validation status.

---

### 8. DATA VALIDATION

Information must be classified using explicit states such as:
VERIFIED, LIKELY, UNCERTAIN, CONFLICTING, UNAVAILABLE.

Validate: source quality, freshness, correctness, duplicates, contradictions, impossible values, missing values, identity matching.
Do not silently resolve contradictory information. Contradictions must remain visible and affect reliability where appropriate.

---

### 9. FEATURE ENGINEERING

Create reproducible numerical features.
Possible feature categories include:
- recent form, home/away strength, goals for/against, xG/xGA, shots, shots on target, possession, corners, cards, fouls, offsides, rest, opponent strength, injuries, player availability, tactical indicators, competition context, other validated variables.

Every production feature must have documentation describing:
- name, definition, calculation, source, time window, missing-data handling, whether it is available before prediction time, version.

NO FUTURE-DATA LEAKAGE. A feature may only use information available at the time the prediction would actually have been made.

---

### 10. FORECASTING ENGINE

Build a genuine forecasting system.
Potential models include: Poisson, Dixon-Coles, Logistic Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM, specialist models where sufficient data exists.

Do not use complex ML merely for appearance. Model selection must be evidence-based.
The system must output probabilities (e.g., Home Win: 47%, Draw: 29%, Away Win: 24%). Those numbers must originate from the forecasting engine.

---

### 11. TIME-AWARE VALIDATION

Do NOT randomly mix future matches into training.
Use chronological/time-aware validation.
The system must evaluate using appropriate metrics including Log Loss, Brier Score, accuracy, MAE, RMSE, calibration, market-specific performance, abstention/NO-BET performance, competition-specific performance.

---

### 12. PROBABILITY CALIBRATION

Forecast probabilities must be calibrated where appropriate.
Possible calibration methods include Platt scaling, isotonic regression, and other statistically justified methods.
Calibration must be evaluated on data that does not contaminate training. Models, datasets, feature versions, calibration methods, and evaluation results must be versioned.

---

### 13. MARKET SYSTEM

A market catalogue defines supported markets and settlement/selection rules.
The market catalogue is NOT a prediction source.
The forecasting system first produces football probabilities. The market engine then maps those forecasts into supported markets.
Do NOT allow bookmaker odds or bookmaker predictions to become predictive inputs.

---

### 14. SPECIALIST MARKETS

Potential specialist markets include: goals, BTTS, corners, cards, offsides, fouls, shots, shots on target, player markets, timing markets, correct score, combination markets, half-by-half markets.
A market may only become active when:
1. sufficient real data exists
2. the required features exist
3. a valid model exists
4. historical validation exists
5. calibration/reliability is acceptable
UI support alone is NOT sufficient.

---

### 15. RISK, CONFIDENCE AND NO BET

NO BET is a first-class output.
The system must assess: data quality, missing information, model reliability, model disagreement, lineup uncertainty, conflicting sources, evidence quality, competition reliability, feature availability, historical model performance.
If reliability is insufficient: NO BET / INSUFFICIENT EVIDENCE.

---

### 16. AUDITABILITY

Every production prediction must be traceable.
Store: match identity, prediction timestamp, current evidence, source URLs, evidence timestamps, relevant statistics, feature values, feature version, dataset version, model version, calibration version, model probabilities, market probabilities, risk assessment, confidence assessment, conflicting evidence, NO-BET decision, system/software version.

---

### 17. WEBSITE

The website should look like a professional AI/data/analytics product.
It must NOT look like a sportsbook, casino, gambling advertisement, or flashy betting interface.
Only implement areas when their underlying functionality actually exists. Do not create fake dashboards representing nonexistent ML performance.

---

### 18. VERCEL

Web project will be deployed on Vercel.
Distinguish between frontend/UI, web/API layer, database, data ingestion, scheduled/background jobs, ML training, ML inference, web research, storage.
Infrastructure decisions must be documented.

---

### 19. SECURITY

Never expose API secrets, database credentials, private keys, provider credentials, or server-only environment variables in client-side code.
Validate user input. Protect administrative/model-training functionality.

---

20. VERSIONING

Version: datasets, schemas, feature definitions, models, calibration, market definitions, prediction pipeline, important configuration, production predictive logic.

---

### 21. TESTING

Automated tests for each stage. Tests must actually execute. Do not claim "tested" merely because test files were created.

---

### 22. DATA AND RESEARCH RULE

When implementation requires unestablished information, research it. Do not guess. Never bypass licensing or access restrictions.

---

### 23. DEVELOPMENT STAGES

Stage-gated execution from STAGE 1 through STAGE 26.

---

### 24. STAGE CONTROL

Work ONLY on the current stage unless explicit authorization for preparatory work is given.

---

### 25. COMPLETION STANDARD

COMPLETE = IMPLEMENTED + TESTED + VERIFIED + DOCUMENTED + ACCEPTANCE CRITERIA PASSED.

---

### 26. NO INVENTION RULE

Never manufacture certainty or default fake data.

---

### 27. STANDARD STAGE HANDOFF REPORT

Use exact 27-section schema for stage handoff reports.

---

### 28. COMMUNICATION RULE

Be factual and technical. Report measurable facts.

---

### 29. MASTER PRINCIPLE

Prioritize DATA INTEGRITY → SCIENTIFIC VALIDITY → REPRODUCIBILITY → AUDITABILITY → SAFETY → RELIABILITY → PRODUCT QUALITY over appearance, speed, or quantity of predictions.
