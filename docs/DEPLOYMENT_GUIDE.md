# Football AI Intelligence Platform — Production Deployment Guide

## 1. Prerequisites
- **Node.js**: v20.x or v22.x LTS installed locally or in deployment environment.
- **Python**: Python 3.12.x installed.
- **Git**: Git repository access with commit authorization.
- **CLI Tools**: `npm`, `pip`, `alembic`, `vercel` CLI, `modal` CLI.

## 2. Accounts Required
- **Vercel Account**: For Next.js App Router hosting.
- **Supabase Account**: Managed PostgreSQL instance with SSL enabled.
- **Modal.com Account**: Python serverless worker execution platform.
- **GitHub / GitLab**: Git hosting connected to Vercel continuous deployment.

## 3. Required Services
- Supabase PostgreSQL Database (Managed Relational Storage).
- Vercel Web Hosting (Edge Node Network).
- Modal.com Compute Engine (Asynchronous Machine Learning Workers).

## 4. Required Software/Tools
```bash
node -v      # v20.x or v22.x required
python3 -V   # Python 3.12 required
npm -v       # npm 10+ required
pip -V       # pip 24+ required
```

## 5. Repository Preparation
Clone repository and prepare environment workspace:
```bash
git clone <repository-url>
cd football-ai-platform
npm ci
pip install -r services/ml/requirements.txt
```

## 6. Supabase Project Creation
1. Log into [Supabase Dashboard](https://supabase.com).
2. Click **New Project** and name it `football-ai-platform-prod`.
3. Set a strong database password and choose your preferred cloud region.
4. Note your database credentials and connection strings.

## 7. Supabase PostgreSQL Configuration
- Copy connection strings from **Settings -> Database -> Connection string**.
- Use **Transaction Pooler** connection string for `DATABASE_URL` (Port 6543) or direct connection (Port 5432).
- Ensure SSL mode is enabled (`?sslmode=require`).

## 8. Database Connection String Format
```
postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
```

## 9. Alembic Configuration
Check `infrastructure/database/alembic.ini` configuration. Set `sqlalchemy.url` dynamically via `DATABASE_URL` environment variable.

## 10. Running Migrations
Execute Alembic migrations sequentially from the repo root or ML directory:
```bash
export DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
cd infrastructure/database
alembic upgrade head
```

## 11. Verifying Database Tables
Verify tables and indexes created in Supabase SQL Editor:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```
Expected tables:
- `matches`
- `clubs`
- `competitions`
- `seasons`
- `prediction_reports`
- `club_aliases`
- `alembic_version`

## 12. FastAPI Deployment
The FastAPI service handles ML prediction execution, risk scoring, probability calibration, and health endpoints.
- **Runtime**: Python 3.12
- **Process Manager**: Uvicorn / Gunicorn with `uvicorn.workers.UvicornWorker`
- **Command**: `uvicorn services.ml.app.main:app --host 0.0.0.0 --port 8000 --workers 4`

## 13. FastAPI Environment Variables
| Variable | Purpose | Location | Secret/Public |
|---|---|---|---|
| `ENVIRONMENT` | Deployment stage (`production`) | FastAPI Server Environment | Public |
| `LOG_LEVEL` | Log verbosity (`INFO`) | FastAPI Server Environment | Public |
| `PORT` | HTTP Listening Port (`8000`) | FastAPI Server Environment | Public |
| `DATABASE_URL` | Supabase PostgreSQL Connection String | FastAPI Server Environment | Secret |
| `API_FOOTBALL_KEY` | External Research Fact Provider Key | FastAPI Server Environment | Secret |
| `MODAL_TOKEN` | Modal worker authentication token | FastAPI Server Environment | Secret |

## 14. Modal Account / Setup
1. Register account at [Modal.com](https://modal.com).
2. Install Modal CLI: `pip install modal`.
3. Authenticate: `modal setup`.

## 15. Modal Worker Deployment / Configuration
Deploy heavy research and pipeline workers:
```bash
modal deploy services/ml/app/workers/modal_pipeline_worker.py
```
*Note: Modal worker integration serves as an architectural boundary. IMPLEMENTATION/DEPLOYMENT VERIFICATION REQUIRED.*

## 16. Vercel Project Creation
1. Go to [Vercel Dashboard](https://vercel.com).
2. Click **Add New -> Project**.
3. Import the `football-ai-platform` repository.

## 17. Vercel Project Configuration
- **Framework Preset**: Next.js
- **Root Directory**: `./`
- **Build Command**: `npm run build --workspace=apps/web`
- **Output Directory**: `apps/web/.next`
- **Install Command**: `npm ci`

## 18. Vercel Environment Variables
| Variable | Purpose | Where Set | Type | Example |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | FastAPI Backend Endpoint Base URL | Vercel Project Settings | Public | `https://api.football-ai.domain.com` |

## 19. API Base URL Configuration
Ensure `NEXT_PUBLIC_API_BASE_URL` points to the live FastAPI HTTPS endpoint without a trailing slash.

## 20. CORS Configuration
In `services/ml/app/main.py`, configure `CORSMiddleware` to restrict allowed origins in production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

## 21. Domain Configuration
Assign custom production domains (e.g., `app.football-ai.com` and `api.football-ai.com`) in Vercel and your DNS provider.

## 22. HTTPS
All traffic between Vercel, client browsers, FastAPI, Supabase, and Modal must communicate strictly over TLS/HTTPS (SSL Mode `require`).

## 23. Production Build
Verify Next.js build clean status locally prior to deployment:
```bash
npm run build --workspace=apps/web
```

## 24. Database Verification
Execute verification query on Supabase:
```sql
SELECT version();
SELECT current_setting('server_version');
SELECT count(*) FROM alembic_version;
```

## 25. Backend Health Verification
Query FastAPI health endpoints:
```bash
curl -i https://api.football-ai.domain.com/health
curl -i https://api.football-ai.domain.com/readiness
```

## 26. Frontend Verification
Navigate to `https://app.football-ai.com` and verify the Dashboard loads without console errors.

## 27. End-to-End Prediction Test
1. Navigate to `/predict`.
2. Input fixture details (`Home Club`, `Away Club`, `Kickoff ISO Timestamp`).
3. Submit and observe status badges: `PREDICTION (ELIGIBLE)`, `NO BET`, or `BLOCKED`.

## 28. Prediction History Verification
Navigate to `/history` and confirm the generated report is persisted with matching SHA256 audit hash.

## 29. Error-State Testing
Test database disconnection or unverified fixture payloads; confirm application gracefully transitions to `SYSTEM ERROR` or `BLOCKED` states without leaking internal stack traces.

## 30. Monitoring
- Configure Vercel Analytics and Log Drains.
- Monitor structured FastAPI JSON logs for correlation IDs and 5xx errors.

## 31. Backups
- Supabase provides automated daily snapshots and 7-day Point-in-Time Recovery (PITR) for Pro plans.

## 32. Recovery
To restore from Supabase Point-in-Time Recovery:
1. Navigate to Supabase Dashboard -> **Database -> Backups**.
2. Select target recovery timestamp and restore to new database instance.
3. Update `DATABASE_URL` on FastAPI service.

## 33. Rollback
- **Vercel**: Instant rollback to previous deployment build via Vercel Dashboard.
- **FastAPI**: Re-deploy previous release container image or commit hash.
- **Database**: Run `alembic downgrade -1` if migration is non-destructive.

## 34. Security Checklist
- [x] No plain-text passwords or secret keys committed to Git.
- [x] `JSONStructuredFormatter` redacting secrets and database strings from logs.
- [x] SSRF protections rejecting loopback, RFC1918 private IPv4/IPv6 ranges, and non-HTTP schemes.
- [x] Unhandled 500 exceptions masked with `x-correlation-id`.
- [x] Zero bookmaker/sportsbook odds used as predictive forecaster inputs.

## 35. Final Launch Checklist
- [x] Frontend workspace build compiles clean with 0 errors.
- [x] Full Python test suite (195 tests) verified.
- [x] Alembic migrations 001, 002, 003 verified.
- [x] App Router routes (`/`, `/predict`, `/history`, `/status`) visually verified via Playwright.
- [ ] Live Vercel production deployment (`OWNER ACTION REQUIRED`).
- [ ] Live Supabase production database creation & migration execution (`OWNER ACTION REQUIRED`).
