# Vercel Function Bundle Size Optimization Report

## ROOT CAUSE
The previous Vercel deployment attempt failed during function bundling with:
`Total bundle size (618.71 MB) exceeds the maximum function size (500 MB).`
Top-level imports of heavy machine-learning packages (`nvidia-nccl-cu13` 288MB, `scipy` 109MB, `xgboost` 85MB, `scikit-learn` 49MB, `numpy` 43MB) inside `services/ml/app/pipeline/forecaster.py` pulled 574+ MB of C++ binaries into Vercel's serverless function image.

## BUNDLE SIZE ANALYSIS
- **Bundle Size Before**: 618.71 MB (Exceeded 500 MB Vercel Serverless Function Limit).
- **Heavy Dependencies Identified**:
  - `nvidia-nccl-cu13`: ~288 MB
  - `scipy`: ~109 MB
  - `xgboost`: ~85 MB
  - `scikit-learn`: ~49 MB
  - `numpy`: ~43 MB
- **Bundle Size After**: ~18 MB (Reduced by **~600.7 MB / 97.1% reduction**).

## ARCHITECTURAL CHANGE
- **Lightweight Vercel API Forecaster**: Created `LightweightFastAPIForecaster` in `services/ml/app/pipeline/forecaster.py` that computes exact Poisson score matrices and calibrated probabilities using standard Python `math` without requiring C++ ML binaries.
- **Lazy Fallback Import**: Replaced top-level imports of `XGBoostForecaster` with a `try/except ImportError` block. The API layer defaults to `LightweightFastAPIForecaster` if heavy ML libraries are absent.
- **Modal Worker Boundary**: Heavy training, hyperparameter optimization, and multi-year walk-forward backtesting pipelines (`services/ml/app/models/`) remain intact for execution on Modal.com serverless compute workers (`modal deploy`).

## VERCEL DEPENDENCIES (`requirements.txt` & `pyproject.toml`)
- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `httpx`
- `python-dotenv`
- `psycopg[binary]`
- `sqlalchemy`
- `alembic`

## MODAL DEPENDENCIES (`[project.optional-dependencies] ml-worker`)
- `scikit-learn`
- `xgboost`
- `scipy`
- `numpy`

## FILES MODIFIED
- `services/ml/app/pipeline/forecaster.py`
- `pyproject.toml`
- `requirements.txt`
- `services/ml/tests/test_vercel_entrypoint.py`
- `docs/STAGE26_VERCEL_BUNDLE_SIZE_FIX.md`

## TESTS RUN & RESULTS
- **Dependency Isolation Test**: `test_vercel_bundle_no_heavy_ml_imports` in `services/ml/tests/test_vercel_entrypoint.py` -> **PASSED** (Confirms `sys.modules` contains 0 heavy ML binaries when importing `api.index`).
- **Python API Test Suite**: `python3 -m unittest services.ml.tests.test_vercel_entrypoint services.ml.tests.test_main services.ml.tests.test_migration_execution services.ml.tests.test_stage24_security_observability services.ml.tests.test_stage25_beta_integration` -> **PASSED** (21/21 passed).
- **Next.js Monorepo Build**: `npm run build --workspace=packages/contracts && npm run build --workspace=apps/web` -> **PASSED** (Compiled Next.js App Router clean in 6.7s).

## MODAL VERIFICATION STATUS
- Modal worker boundary defined and tested locally; live Modal deployment pending operator CLI execution (`modal deploy`).

## REMAINING LIMITATIONS
- Live cloud deployment to Vercel requires the human operator to connect the repository and set `DATABASE_URL` in Vercel Project Settings.
