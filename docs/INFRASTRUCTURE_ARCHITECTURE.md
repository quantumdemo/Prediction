# INFRASTRUCTURE ARCHITECTURE
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. INFRASTRUCTURE SEPARATION PRINCIPLE

Vercel is an exceptional platform for web frontend hosting and serverless edge API routing, but it is **not** suitable for long-running data ingestion, heavy machine learning training, or high-memory model inference due to execution timeouts (10s–60s) and memory constraints.

#### 1.1 Vercel Responsibilities
- **Web Frontend**: Next.js App Router, SSR/ISR page rendering, tailwind UI presentation.
- **Serverless API Gateway**: HTTP request validation, session authentication, prediction retrieval queries, user UI interactions.
- **Edge Caching**: Caching static assets and public prediction audit logs.

#### 1.2 Non-Vercel Infrastructure Responsibilities
- **Relational Database**: Managed PostgreSQL (Supabase / AWS RDS PostgreSQL) providing transactional ACID support, PGVector (if semantic search needed), connection pooling (PgBouncer).
- **Object Storage**: AWS S3 / Cloudflare R2 for storing raw model artifacts, serialized feature matrices, backtest report logs, and research snapshots.
- **Async Python Workers**: Async ML Compute pool (Modal.com or AWS ECS/Fargate Python workers) for running Python workloads (pandas, scikit-learn, XGBoost, LightGBM, web scraping, and automated feature pipelines).
- **Background Job Scheduler**: Redis + Celery / QStash for handling scheduled historical data ingestions and web research jobs.

---

### 2. INFRASTRUCTURE TOPOLOGY DIAGRAM

```
                       ┌───────────────────────────────┐
                       │     User Browser / Client     │
                       └───────────────┬───────────────┘
                                       │ HTTPS
                                       ▼
                       ┌───────────────────────────────┐
                       │      Vercel Edge Network      │
                       │   (Next.js UI & API Gateway)  │
                       └───────┬───────────────┬───────┘
                               │               │
                     Database  │               │ HTTP / RPC
                   Connections │               │ Trigger
                               ▼               ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│       Managed PostgreSQL        │   │    Async Python Workers Pool    │
│     (Supabase / AWS RDS)        │   │    (Modal.com / AWS Fargate)    │
│  - Entity Tables & Matches      │   │  - Feature Engineering Engine   │
│  - Feature Snapshots            │   │  - Model Training & Inference   │
│  - Prediction Audit Logs        │   │  - Web Research Scrapers        │
└─────────────────────────────────┘   └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │   S3 / Cloudflare R2 Storage    │
                                      │  - Serialized Models (.pkl/xgb) │
                                      │  - Backtest Logs & Datasets     │
                                      └─────────────────────────────────┘
```
