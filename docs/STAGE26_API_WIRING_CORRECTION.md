# Stage 26 API Wiring Correction Report

## STAGE
Stage 26 — Public Launch + Continuous Monitoring (Pre-Deployment API Wiring Correction)

## STATUS
IMPLEMENTED & TESTED LOCALLY — NOT DEPLOYED — NOT LIVE VERIFIED

## OBJECTIVE
Expose the existing Python prediction pipeline (`EndToEndPredictionPipeline`) and prediction history repository (`PredictionHistoryRepository`) as real, production-ready FastAPI HTTP endpoints in `services/ml/app/main.py`.

## API ROUTES ADDED
1. **`POST /api/v1/predict`**
   - **File**: `services/ml/app/main.py`
   - **Function**: `predict_match()`
   - **Request Payload**: `PredictionPipelineRequest` (`fixture_id`, `home_team`, `away_team`, `competition`, `season`, `match_date`, `raw_research_inputs`, `base_features`)
   - **Handler Execution**: Invokes `EndToEndPredictionPipeline.run()` executing all 9 prediction stages.
   - **Response Output**: `EndToEndPredictionResponse` containing `report_id`, `audit_hash`, `decision_status`, 1X2 probabilities, mapped market decisions, risk flags, and full `AuditablePredictionReport`.
2. **`GET /api/v1/history`**
   - **File**: `services/ml/app/main.py`
   - **Function**: `get_prediction_history()`
   - **Query Parameters**: `limit` (default 20, max 100), `offset` (default 0), `status` (alias for `decision_status`), `fixture_id`.
   - **Handler Execution**: Invokes `PredictionHistoryRepository.query_history()`.
   - **Response Output**: List of `AuditablePredictionReport` JSON objects.

## PREDICTION FLOW
```
USER (Next.js UI at apps/web/src/app/predict/page.tsx)
  ↓ HTTP POST `${NEXT_PUBLIC_API_URL}/api/v1/predict`
FastAPI Endpoint (`POST /api/v1/predict` in services/ml/app/main.py)
  ↓ Request schema validation
EndToEndPredictionPipeline.run() (services/ml/app/integration/pipeline.py)
  ├─ Step 1: Fixture Verification (services/ml/app/research/verifier.py)
  ├─ Step 2: Web Research Fact Collection (services/ml/app/research/engine.py)
  ├─ Step 3: Evidence Validation Safeguards (services/ml/app/evidence/validator.py)
  ├─ Step 4: Current Feature Vector Updating (services/ml/app/pipeline/updater.py)
  ├─ Step 5: Model Forecasting via xgboost_platt (services/ml/app/pipeline/forecaster.py)
  ├─ Step 6: Market Mapping for 8 Supported Markets (services/ml/app/markets/mapper.py)
  ├─ Step 7: Risk, Confidence & NO-BET Evaluation (services/ml/app/risk/engine.py)
  ├─ Step 8: Auditable Report Generation & SHA256 Hash (services/ml/app/reporting/generator.py)
  └─ Step 9: DB Persistence via SQLAlchemy (services/ml/app/reporting/repository.py)
  ↓
HTTP 200 JSON Response (`EndToEndPredictionResponse`)
```

## HISTORY FLOW
```
USER (Next.js UI at apps/web/src/app/history/page.tsx)
  ↓ HTTP GET `${NEXT_PUBLIC_API_URL}/api/v1/history?limit=20`
FastAPI Endpoint (`GET /api/v1/history` in services/ml/app/main.py)
  ↓ PredictionHistoryFilter query parsing
PredictionHistoryRepository.query_history() (services/ml/app/reporting/repository.py)
  ↓ DB session query on `prediction_reports`
HTTP 200 JSON Response (`AuditablePredictionReport[]`)
```

## CORS
Configured via `CORSMiddleware` in `services/ml/app/main.py`. Environment variable `ALLOWED_ORIGINS` (comma-separated list of origins) controls production cross-origin access (e.g. `ALLOWED_ORIGINS="https://app.yourdomain.com,https://your-vercel-app.vercel.app"`). Defaults to `["*"]` in development.

## ENVIRONMENT VARIABLES
- `NEXT_PUBLIC_API_URL`: Frontend client API URL (e.g. `https://api.yourdomain.com`).
- `DATABASE_URL`: Supabase PostgreSQL connection string.
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins for FastAPI.

## TESTS RUN & RESULTS
- **Test File**: `services/ml/tests/test_main.py`
- **Command**: `python3 -m unittest services/ml/tests/test_main.py`
- **Result**: 7/7 tests passed cleanly (valid predict, invalid request 422 validation, empty/query history, status filtering, health, readiness, and correlation ID propagation).

## SECURITY
- Log credential sanitization (`JSONStructuredFormatter`).
- SSRF protections rejecting loopback (`127.0.0.0/8`, `::1`), RFC1918 private IPv4 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and local domains.
- Correlation ID propagation (`x-correlation-id`).
- Unhandled 500 exception trace masking.

## KNOWN LIMITATIONS
- Live cloud deployment to Vercel, Supabase PostgreSQL, and Modal compute remains an external human deployment step requiring live cloud account credentials.

## UNRESOLVED ISSUES
- None.

## DEPLOYMENT STATUS
- Local verification complete; ready for human owner cloud deployment.

## NEXT STEP
- Execute human deployment steps according to `docs/DEPLOYMENT_GUIDE.md`.
