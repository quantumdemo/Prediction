# Vercel FastAPI Deployment & Serverless Integration Guide

## 1. Vercel Architecture Overview
The platform deploys as a unified monorepo on Vercel:
- **Frontend**: Next.js 15 App Router web application (`apps/web`).
- **Backend API**: FastAPI Python application (`services/ml/app/main.py`) exposed via Vercel's Python Serverless Function entry point at `api/index.py`.
- **Database**: Supabase PostgreSQL managed relational storage.
- **Asynchronous Worker Compute**: Modal.com serverless Python compute platform for heavy web research or async jobs.

---

## 2. Vercel Monorepo Configuration (`vercel.json`)
The root `vercel.json` maps incoming HTTP routes to the Next.js frontend and Python serverless API:
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "buildCommand": "npm run build --workspace=packages/contracts && npm run build --workspace=apps/web",
  "outputDirectory": "apps/web/.next",
  "rewrites": [
    {
      "source": "/api/v1/:path*",
      "destination": "/api/index.py"
    },
    {
      "source": "/health",
      "destination": "/api/index.py"
    },
    {
      "source": "/readiness",
      "destination": "/api/index.py"
    }
  ]
}
```

---

## 3. Serverless Entry Point (`api/index.py`)
Vercel automatically detects `api/index.py` and executes the exported ASGI `app`:
```python
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
contracts_path = os.path.join(repo_root, "packages", "contracts", "python")

for path in [repo_root, contracts_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from services.ml.app.main import app

app = app
```

---

## 4. Required Production Environment Variables
| Variable Name | Component | Location | Description |
|---|---|---|---|
| `DATABASE_URL` | FastAPI & Alembic | Vercel Project Settings | Supabase PostgreSQL connection string (`postgresql://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`). |
| `NEXT_PUBLIC_API_URL` | Next.js Frontend | Vercel Project Settings | Production public URL of the deployed application (e.g. `https://app.yourdomain.com`). Used by client browser `fetch()` calls. |
| `ALLOWED_ORIGINS` | FastAPI CORS | Vercel Project Settings | Comma-separated list of allowed CORS origin domains (e.g., `https://app.yourdomain.com,https://football-ai-platform.vercel.app`). |
| `API_FOOTBALL_KEY` | Research Engine | Vercel Project Settings | Optional external web research API key. |
| `MODAL_TOKEN` | Modal Workers | Vercel Project Settings | Modal.com authentication token for async worker compute. |

---

## 5. Supabase Database & Alembic Migration Integration
- **Database Connection**: `DATABASE_URL` must point to Supabase Transaction Pooler (Port 6543) with `?sslmode=require`.
- **Alembic Override**: `infrastructure/database/migrations/env.py` automatically inspects `DATABASE_URL` and overrides the local `alembic.ini` URL for online and offline migrations.
- **Migration Command**: Run `alembic upgrade head` from CI/CD or local CLI prior to public launch.

---

## 6. Frontend → Backend Connectivity
- Frontend pages (`/predict`, `/history`, `/status`) execute client browser `fetch()` requests targeting `${NEXT_PUBLIC_API_URL}/api/v1/...`.
- When deployed on Vercel, requests to `/api/v1/predict`, `/api/v1/history`, `/health`, and `/readiness` are seamlessly rewritten to `api/index.py`.

---

## 7. Serverless Execution Boundaries & Modal's Role
- **Vercel Timeout Limits**: Vercel Serverless Functions enforce a 15-second execution timeout on Hobby plans (up to 60s/300s on Pro/Enterprise plans).
- **Inference Latency**: The 9-stage `EndToEndPredictionPipeline` runs synchronously within ~0.4s to 1.5s when using pre-collected research facts or cached features.
- **Modal Compute Boundary**: Heavy asynchronous web research, multi-year backtesting, or model retraining jobs must be delegated to Modal.com compute workers (`modal deploy`) to avoid exceeding serverless function timeout limits.

---

## 8. Deployment Step-by-Step
1. **GitHub Connection**: Push changes to GitHub.
2. **Import Project**: In Vercel Dashboard, import `football-ai-platform`.
3. **Configure Build Settings**: Framework = `Next.js`, Root Directory = `./`.
4. **Set Environment Variables**: Add `DATABASE_URL`, `NEXT_PUBLIC_API_URL`, and `ALLOWED_ORIGINS`.
5. **Deploy**: Click **Deploy**. Vercel compiles Next.js frontend pages and builds the Python serverless API function.
6. **Verify Health**: Query `https://app.yourdomain.com/health` and verify HTTP 200 OK.
