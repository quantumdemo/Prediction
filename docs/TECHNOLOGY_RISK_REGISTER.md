# TECHNOLOGY RISK REGISTER
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. ARCHITECTURAL RISK MATRIX

| Risk ID | Risk Category | Description | Severity | Probability | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TECH-RISK-001** | Infrastructure | Vercel serverless execution timeouts during web research parsing. | HIGH | HIGH | Offload web research scraping and feature processing to async workers (Modal/Celery). |
| **TECH-RISK-002** | Data Licensing | API providers restricting commercial redistribution of detailed event stats. | HIGH | MEDIUM | Restrict data usage to internal feature computation; do not re-expose raw provider feeds. |
| **TECH-RISK-003** | Data Integrity | Missing xG/shot data in historical datasets leading to biased features. | MEDIUM | HIGH | Enforce explicit `NULL` handling and flag missingness in feature vectors; trigger NO-BET when required. |
| **TECH-RISK-004** | Security | Indirect prompt injection via scraped web research articles manipulating LLM fact extraction. | HIGH | LOW | Strip HTML/scripts, isolate text parsing via strict Pydantic schemas, and prevent LLM outputs from affecting probabilities. |
| **TECH-RISK-005** | Model Drift | Performance decay of statistical models across season transitions. | MEDIUM | HIGH | Implement chronological backtests per season and continuous Brier score calibration monitoring. |

---

### 2. UNRESOLVED TECHNICAL QUESTIONS

1. **QUESTION**: What is the precise memory footprint of the trained XGBoost ensemble when loaded in Modal serverless Python containers?
   - *Target Stage*: Stage 11 (ML Forecasting).
   - *Action Plan*: Benchmark inference memory and cold-start latency during Stage 11 model prototyping.

2. **QUESTION**: Should the historical dataset store raw provider CSV payloads in Cloudflare R2 object storage or exclusively inside PostgreSQL JSONB tables?
   - *Target Stage*: Stage 4 (Database Schema & Contracts).
   - *Action Plan*: Evaluate payload size vs query performance in Stage 4 database design.
