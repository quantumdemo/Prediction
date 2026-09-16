# DEPLOYMENT ARCHITECTURE & SCALING STRATEGY
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. CI/CD PIPELINE ARCHITECTURE

```
[GIT PUSH / PR] ──► [GITHUB ACTIONS CI]
                          │
                          ├─► 1. Linting & Formatting Check
                          ├─► 2. Automated Unit & Integration Tests (`tests/`)
                          ├─► 3. Data Leakage & Schema Tests
                          │
                    (Tests Pass)
                          │
                          ▼
            ┌─────────────┴─────────────┐
            ▼                           ▼
  [VERCEL PREVIEW BUILD]      [ASYNC WORKER DEPLOYMENT]
  (Frontend & Edge API)       (Modal.com / Container Registry)
```

---

### 2. DATABASE MIGRATION STRATEGY

- Migrations are managed via **Alembic** (Python) or **Prisma/dbmate** (SQL).
- Schema changes MUST be backward-compatible (zero-downtime deployment pattern: Add -> Migrate -> Deprecate -> Drop).
- Production database migrations execute automatically in CI/CD prior to code deployment.

---

### 3. SCALING TIERS

| Growth Phase | Web Layer | Database Layer | ML & Worker Layer | Estimated Monthly Cost |
| :--- | :--- | :--- | :--- | :--- |
| **MVP / Private Beta** | Vercel Hobby / Pro | Supabase Free / Micro Tier | Modal Serverless Pay-as-you-go | $0 – $25 / mo |
| **Production Scale (v1.0)** | Vercel Pro | Supabase Pro / AWS RDS PostgreSQL (db.t4g.medium) | Modal / AWS ECS Fargate Workers | $50 – $200 / mo |
| **High Volume Scaling** | Vercel Enterprise | Managed Multi-AZ PostgreSQL + Read Replicas | Dedicated GPU/CPU Worker Instances | Scale with traffic |
