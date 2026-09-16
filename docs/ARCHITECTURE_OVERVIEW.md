# ARCHITECTURE OVERVIEW
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. EXECUTIVE SUMMARY & ARCHITECTURAL PATTERN

The Football AI Intelligence & Machine-Learning Platform is designed as a **Modular Monolith** for its initial implementation phase, transitioning to a hybrid service-oriented pattern as ML compute requirements expand.

#### Architectural Choice: Modular Monolith
- **Reasoning**: Minimizes operational overhead during early stages while maintaining strict logical and physical module boundaries.
- **Service Boundaries**:
  1. `identity`: User auth, role-based permissions, API rate-limiting tokens.
  2. `fixture`: Fixture lookup, canonical team/competition verification, schedule tracking.
  3. `football_data`: Historical match ingestion, result feeds, xG/shots statistics storage.
  4. `web_research`: Current match news, lineups, injury scraper, evidence classification.
  5. `feature_engineering`: Pre-match feature vectors, rolling stats, rest-day metrics with strict zero-leakage guards.
  6. `forecasting`: Statistical baseline models (Poisson/Dixon-Coles) & ML models (XGBoost/LightGBM).
  7. `calibration`: Probability calibration (Platt scaling, Isotonic regression) and Brier scoring.
  8. `market_mapping`: Mapping probability matrices to supported football betting markets.
  9. `risk_engine`: Uncertainty metrics, model disagreement evaluation, NO-BET decision logic.
  10. `audit_reporting`: Immutable record logging of prediction features, models, versions, and evidence.

---

### 2. END-TO-END DATA FLOW DIAGRAMS

#### 2.1 Prediction Inference Pipeline
```
[USER MATCH REQUEST]
         │
         ▼
[1. FIXTURE SERVICE] ──(Unverified Fixture)──► [VERIFICATION FAILURE / NO BET]
         │
     (Verified)
         ▼
[2. WEB RESEARCH SERVICE] ──► [3. EVIDENCE VALIDATION]
         │                               │
         ▼                               ▼
[4. HISTORICAL DATA SERVICE] ──► [5. FEATURE ENGINE (Cutoff Guard)]
                                         │
                                         ▼
                             [6. FORECASTING ENGINE]
                                 (Poisson / ML)
                                         │
                                         ▼
                            [7. PROBABILITY CALIBRATION]
                                         │
                                         ▼
                             [8. MARKET MAPPING]
                                         │
                                         ▼
                             [9. RISK & NO-BET ENGINE]
                                         │
                       ┌─────────────────┴─────────────────┐
                       ▼                                   ▼
              (Safe Confidence)                     (High Uncertainty)
                       │                                   │
                       ▼                                   ▼
             [VALID PREDICTION]             [NO BET / INSUFFICIENT EVIDENCE]
                       │                                   │
                       └─────────────────┬─────────────────┘
                                         ▼
                            [10. AUDIT RECORD LOGGING]
                                         │
                                         ▼
                               [POSTGRESQL AUDIT DB]
```

#### 2.2 Offline Model Training Pipeline
```
[HISTORICAL DB] ──► [TIME-AWARE CHRONOLOGICAL SPLIT]
                             │
                             ▼
                 [FEATURE EXTRACTOR (t < cutoff)]
                             │
                             ▼
                 [TRAINING DATASET MATRIX]
                             │
                             ▼
                 [MODEL FIT (Poisson / XGBoost)]
                             │
                             ▼
                 [PROBABILITY CALIBRATION (Validation Set)]
                             │
                             ▼
                 [BRIER SCORE & LOG LOSS EVALUATION]
                             │
                       ┌─────┴─────┐
                       ▼           ▼
                   (Passed)     (Failed)
                       │           │
                       ▼           ▼
               [MODEL REGISTRY]  [REJECT / RE-TUNE]
```

---

### 3. SYNCHRONOUS VS ASYNCHRONOUS WORKLOADS

| Workload Type | Execution Model | Hosting / Component | Max Latency Target |
| :--- | :--- | :--- | :--- |
| Match Verification Lookup | Synchronous API | Vercel Edge / Serverless API | < 200 ms |
| Prediction Inference (Cached Feature Vector) | Synchronous API | Vercel Edge / Serverless API | < 1.5 s |
| Current Match Web Research Parsing | Asynchronous Task | Async Worker (Modal / Celery) | < 15 s |
| Feature Vector Calculation (Fresh) | Asynchronous Task | Async Worker (Modal / Celery) | < 3 s |
| Offline Model Training & Calibration | Asynchronous Job | Batch Worker Infrastructure | Minutes - Hours |
| Historical Data Ingestion & Cleaning | Scheduled Cron Job | Scheduled Worker / GitHub Action | Minutes |
