# ARCHITECTURE DECISION RECORDS (ADRs)
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### ADR-001: FRONTEND & WEB LAYER ARCHITECTURE
- **Status**: APPROVED
- **Context**: The web application requires high-performance UI rendering, SEO for match analysis views, and seamless integration with serverless deployment platforms.
- **Options Considered**:
  1. Next.js (TypeScript) App Router
  2. React Single Page Application (Vite)
  3. SvelteKit
- **Decision**: Selected **Next.js (TypeScript) App Router**.
- **Rationale**: Direct compatibility with Vercel edge deployment, built-in server-side rendering for data pages, and strong TypeScript type safety across API boundaries.
- **Consequences**: Serverless API execution times must remain under Vercel function timeouts (<10s). Heavy Python ML workloads must be offloaded.
- **Revisit Conditions**: If Vercel edge deployment costs or function execution constraints impede scaling.

---

### ADR-002: BACKEND & API ARCHITECTURE
- **Status**: APPROVED
- **Context**: The platform requires lightweight HTTP gateway services for web UI requests and high-performance Python services for ML inference and feature calculation.
- **Options Considered**:
  1. FastAPI (Python) for core API + Next.js Server Actions for UI Edge Gateway
  2. Pure Node.js Express monolith
  3. Pure Django monolithic framework
- **Decision**: Selected **Hybrid Architecture**: Next.js API Routes for UI Gateway + **FastAPI (Python 3.11+)** for ML/Data services.
- **Rationale**: FastAPI natively interfaces with the Python ML stack (pandas, scikit-learn, XGBoost) and provides Pydantic data validation and auto-generated OpenAPI contracts.
- **Consequences**: Requires maintaining clean contract boundaries between Next.js edge functions and FastAPI ML workers.

---

### ADR-003: DATABASE SELECTION
- **Status**: APPROVED
- **Context**: Football data requires strict relational integrity (Countries -> Competitions -> Seasons -> Clubs -> Matches -> Stats), ACID transactions for prediction logging, and JSONB capability for audit snapshots.
- **Options Considered**:
  1. Managed PostgreSQL (Supabase / AWS RDS)
  2. MongoDB / Document Store
  3. SQLite
- **Decision**: Selected **Managed PostgreSQL**.
- **Rationale**: Native relational integrity, support for complex analytical SQL queries, JSONB column support for flexible audit snapshots, and broad ORM support in Python (`psycopg3`/`SQLAlchemy`).
- **Consequences**: Requires structured SQL migration scripts and index management for timestamp-based fixture queries.

---

### ADR-004: MACHINE LEARNING FORECASTING ENGINE
- **Status**: APPROVED
- **Context**: Forecasting requires parametric statistical baseline models (Poisson / Dixon-Coles) alongside advanced gradient boosted decision trees (XGBoost / LightGBM) for tabular match statistics.
- **Options Considered**:
  1. Hybrid Statistical Baseline (Poisson/Dixon-Coles via `statsmodels`) + ML Ensemble (XGBoost/LightGBM via `scikit-learn`)
  2. Deep Learning Neural Networks (PyTorch)
  3. LLM-only probability generation
- **Decision**: Selected **Hybrid Statistical Baseline + ML Ensemble**.
- **Rationale**: Tabular sports data consistently performs best with Dixon-Coles and Gradient Boosted Trees. LLM-only generation is strictly forbidden by the Master Specification.
- **Consequences**: Requires probability calibration (Isotonic/Platt) on validation sets to ensure well-calibrated probabilities.

---

### ADR-005: ASYNCHRONOUS WORKER & BACKGROUND JOB ARCHITECTURE
- **Status**: APPROVED
- **Context**: Data ingestion, web research scraping, feature matrix computation, and model training exceed Vercel HTTP timeouts.
- **Options Considered**:
  1. Modal.com (Serverless Python Worker Pool) + QStash Scheduler
  2. Self-hosted Celery + Redis on EC2
  3. AWS Lambda Python runtime
- **Decision**: Selected **Modal.com + Upstash QStash**.
- **Rationale**: Modal provides instant serverless Python container execution with zero infrastructure maintenance, pay-per-second billing, and native Python environment isolation.
- **Consequences**: Cloud execution costs must be monitored as job volume grows.

---

### ADR-006: OBJECT & ARTIFACT STORAGE
- **Status**: APPROVED
- **Context**: Serialized ML models (.pkl / .json), raw dataset CSV dumps, and backtest logs require immutable storage.
- **Options Considered**:
  1. AWS S3 / Cloudflare R2
  2. Storing raw artifacts inside PostgreSQL bytea columns
  3. Local disk storage
- **Decision**: Selected **S3-compatible Object Storage (AWS S3 / Cloudflare R2)**.
- **Rationale**: Infinite scalability, zero database load, low storage cost, and native SDK integration in Python (`boto3`).

---

### ADR-007: DEPLOYMENT INFRASTRUCTURE
- **Status**: APPROVED
- **Context**: Need cost-effective, scalable deployment for frontend, API, database, and ML workers.
- **Options Considered**:
  1. Vercel (Frontend/API) + Supabase (PostgreSQL) + Modal (ML Workers)
  2. Single monolithic EC2 instance
  3. Full Kubernetes cluster (EKS)
- **Decision**: Selected **Vercel + Supabase + Modal**.
- **Rationale**: Ideal separation of concerns; zero DevOps overhead for MVP and private beta phase; clear scaling path.

---

### ADR-008: SYSTEM MONITORING & OBSERVABILITY
- **Status**: APPROVED
- **Context**: Must track application errors, API latency, ML model calibration drift, and background job failures.
- **Options Considered**:
  1. Sentry (Error Tracking) + PostgreSQL Logging Tables + OpenTelemetry
  2. Prometheus + Grafana self-hosted stack
- **Decision**: Selected **Sentry + Structured PostgreSQL Logging Tables**.
- **Rationale**: Low setup effort, real-time error alerting, and direct auditability within the primary database.

---

### ADR-009: FOOTBALL DATA SOURCE INTEGRATION STRATEGY
- **Status**: APPROVED
- **Context**: Need reliable historical match statistics and live fixture feeds without licensing violations.
- **Options Considered**:
  1. Primary Historical: Football-Data.co.uk CSVs; Primary Live/Fixture: API-Football (RapidAPI)
  2. Direct Web Scraping of commercial betting sites
- **Decision**: Selected **Football-Data.co.uk (Historical) + API-Football (Live/Fixture)**.
- **Rationale**: Legitimate open historical data combined with structured commercial API access; eliminates scraping legal/reliability risks. Direct web scraping of betting sites is rejected.
