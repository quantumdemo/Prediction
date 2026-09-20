# Production Troubleshooting & Failure Incident Guide

This guide covers 16 common operational failure scenarios across Vercel, FastAPI, Supabase PostgreSQL, Modal workers, and frontend-backend communications.

---

### Scenario 1: Vercel Build Failure
- **Symptom**: Vercel deployment fails during build step with workspace module error.
- **Likely Cause**: Incorrect root directory or missing build workspace command flag.
- **Check**: Inspect Vercel Project Settings -> Build Command.
- **Fix**: Set Build Command to `npm run build --workspace=apps/web` and Install Command to `npm ci`.
- **Verification**: Re-run Vercel deployment.

---

### Scenario 2: Next.js API Base URL Incorrect
- **Symptom**: Frontend fetch requests fail with `ERR_NAME_NOT_RESOLVED` or attempt to hit `http://localhost:8000` in production.
- **Likely Cause**: `NEXT_PUBLIC_API_BASE_URL` missing in Vercel environment variables or contains trailing slash.
- **Check**: Inspect Vercel Environment Variables and check browser console.
- **Fix**: Set `NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com` (no trailing slash) and re-deploy Next.js.
- **Verification**: Inspect Network tab in client browser.

---

### Scenario 3: CORS Policy Blocking Requests
- **Symptom**: Browser console displays `Access-Control-Allow-Origin` header missing or mismatch error.
- **Likely Cause**: FastAPI `CORSMiddleware` in `services/ml/app/main.py` does not include the Vercel production origin domain.
- **Check**: Run `curl -H "Origin: https://app.yourdomain.com" -I https://api.yourdomain.com/health`.
- **Fix**: Add Vercel domain to `allow_origins` array in `services/ml/app/main.py`.
- **Verification**: Confirm `Access-Control-Allow-Origin` header is returned in response.

---

### Scenario 4: FastAPI Service Unavailable (502 / 504)
- **Symptom**: Client receives HTTP 502 Bad Gateway or 504 Gateway Timeout.
- **Likely Cause**: Uvicorn service process crashed or system memory exhausted.
- **Check**: Inspect server systemd/docker logs: `journalctl -u ml-service -f` or `docker logs ml-service`.
- **Fix**: Restart FastAPI service (`systemctl restart ml-service`) and verify workers count.
- **Verification**: `curl -i https://api.yourdomain.com/health`.

---

### Scenario 5: Database Connection Failure (503 Readiness Error)
- **Symptom**: `/readiness` returns HTTP 503 `NOT_READY` and UI displays `SYSTEM ERROR`.
- **Likely Cause**: Invalid `DATABASE_URL`, database pool exhaustion, or Supabase SSL mode mismatch.
- **Check**: Inspect FastAPI structured JSON log for `DATABASE_CONNECTION_ERROR`.
- **Fix**: Ensure `DATABASE_URL` includes `?sslmode=require`, test password credentials, and increase pool size in `services/ml/app/db/session.py`.
- **Verification**: `curl https://api.yourdomain.com/readiness` returns HTTP 200 OK.

---

### Scenario 6: Supabase Connection Pooling Limit Reached
- **Symptom**: Log error `fatally closed connection` or `remaining connection slots reserved`.
- **Likely Cause**: Application connecting directly to Port 5432 instead of Supabase Transaction Pooler (Port 6543).
- **Check**: Inspect host port in `DATABASE_URL`.
- **Fix**: Switch `DATABASE_URL` host to Supabase Pooler endpoint on Port 6543.
- **Verification**: Query active pool connections in Supabase SQL Editor.

---

### Scenario 7: Alembic Migration Failure
- **Symptom**: Startup error `Target database is not up to date` or missing table error.
- **Likely Cause**: Migrations not executed against the live database instance prior to service launch.
- **Check**: Run `alembic current` inside `infrastructure/database/`.
- **Fix**: Run `alembic upgrade head` with target production `DATABASE_URL`.
- **Verification**: Confirm `alembic_version` table contains latest migration hash (`003`).

---

### Scenario 8: Modal Worker Failure or Timeout
- **Symptom**: Web research step fails or pipeline falls back to `INSUFFICIENT_EVIDENCE`.
- **Likely Cause**: Modal token expired or worker function timed out.
- **Check**: Inspect Modal Dashboard logs at `https://modal.com/logs`.
- **Fix**: Re-authenticate Modal CLI (`modal setup`) and deploy updated worker (`modal deploy`).
- **Verification**: Test worker invocation directly via python test script.

---

### Scenario 9: Missing Environment Variable
- **Symptom**: FastAPI fails to start or throws `ValidationError` on Pydantic `Settings`.
- **Likely Cause**: Required variable (e.g., `DATABASE_URL`) missing from environment.
- **Check**: Run `python3 -c "from services.ml.app.config import settings; print(settings)"`.
- **Fix**: Export missing environment variable in server shell or `.env`.
- **Verification**: FastAPI starts cleanly without configuration errors.

---

### Scenario 10: Unhandled 500 Application Exception
- **Symptom**: API returns JSON `{"code": "INTERNAL_INFRASTRUCTURE_FAILURE"}` with correlation ID.
- **Likely Cause**: Unexpected code error in pipeline or unhandled library exception.
- **Check**: Search server logs for matching `correlation_id`.
- **Fix**: Inspect traceback linked to correlation ID in structured JSON logs and apply patch.
- **Verification**: Re-run failed request payload with identical correlation ID.

---

### Scenario 11: Frontend Blank Page / Hydration Error
- **Symptom**: Web browser displays blank white page or React hydration mismatch warning in console.
- **Likely Cause**: Client/Server component boundary mismatch or window object access during SSR.
- **Check**: Open browser Web Developer Tools -> Console.
- **Fix**: Wrap client-only browser APIs inside `useEffect` or add `"use client"` directive.
- **Verification**: Re-build Next.js app (`npm run build --workspace=apps/web`).

---

### Scenario 12: Prediction Request Blocked (`BLOCKED` Status)
- **Symptom**: Pipeline returns `BLOCKED (EVIDENCE CONFLICT / UNVERIFIED)`.
- **Likely Cause**: Research fact items contain contradictory claims or fixture fail alias resolution.
- **Check**: Inspect `prediction_report.provenance.contradictions` array in JSON response.
- **Fix**: Correct conflicting pre-match fact items or verify team names against verified alias map.
- **Verification**: Re-submit prediction request.

---

### Scenario 13: History Retrieval Failure
- **Symptom**: `/history` page displays 0 reports despite previous predictions being generated.
- **Likely Cause**: DB persistence transaction rolled back or fixture timestamp filter mismatch.
- **Check**: Query `SELECT count(*) FROM prediction_reports;` in Supabase SQL Editor.
- **Fix**: Ensure `db_transaction()` context manager commits cleanly in `PredictionHistoryRepository`.
- **Verification**: Refresh `/history` route.

---

### Scenario 14: SSL / HTTPS Certificate Issue
- **Symptom**: Browser warns `Your connection is not private` (`NET::ERR_CERT_COMMON_NAME_INVALID`).
- **Likely Cause**: DNS CNAME record not pointing correctly to Vercel/FastAPI domain proxy.
- **Check**: Run `dig +short app.yourdomain.com`.
- **Fix**: Update DNS CNAME record to point to `cname.vercel-dns.com`.
- **Verification**: Access domain over HTTPS.

---

### Scenario 15: Timeout on Long Research Queries
- **Symptom**: HTTP 504 timeout when running current-match prediction pipeline.
- **Likely Cause**: Web research HTTP requests exceeding server proxy timeout threshold.
- **Check**: Measure research step execution time in server logs.
- **Fix**: Set HTTP client timeout limits in research engine and use asynchronous Modal compute workers.
- **Verification**: Complete prediction request within < 5.0s window.

---

### Scenario 16: Secret Exposure in Client Logs
- **Symptom**: API key or database password visible in browser console or server logs.
- **Likely Cause**: Environment variable prefixed with `NEXT_PUBLIC_` or `JSONStructuredFormatter` missing key.
- **Check**: Search client bundles and logs for secret patterns.
- **Fix**: Remove `NEXT_PUBLIC_` prefix from server-only variables and update `JSONStructuredFormatter`.
- **Verification**: Verify clean output via `test_stage24_security_observability.py`.
