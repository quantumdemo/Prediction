# Vercel Setuptools Package Discovery Build Correction Report

## ROOT CAUSE
When Vercel builds Python projects, `uv` invokes `setuptools` build hooks over the repository root `pyproject.toml`. Because the monorepo root layout contains multiple non-Python package subdirectories (`api`, `apps`, `packages`, `services`, `infrastructure`, `node_modules`), setuptools' auto-discovery mechanism threw:
`error: Multiple top-level packages discovered in a flat-layout: ['api', 'apps', 'packages', 'services', 'node_modules', 'infrastructure']`
Setuptools halted the build because no explicit package discovery boundaries were declared in `pyproject.toml`.

## EXACT CHANGE MADE
In root `pyproject.toml`, added explicit setuptools package discovery configuration:
```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["api*", "services*"]
exclude = ["apps*", "packages*", "infrastructure*", "tests*", "docs*"]
```

## WHY THE CHANGE IS SAFE
1. **Preserves Architecture**: The single-project Next.js + Python serverless architecture (`api/index.py` → `services.ml.app.main`) is fully preserved without moving or renaming directories.
2. **Explicit Package Scoping**: Tells setuptools exactly which Python modules to discover (`api` and `services`), while ignoring JavaScript/TypeScript frontend workspaces (`apps`, `packages`) and infrastructure SQL/Alembic migrations (`infrastructure`).
3. **No Code/ML Changes**: Zero changes were made to ML forecasting models, probability calibration, features, risk rules, or Next.js frontend components.

## FILES MODIFIED
- `pyproject.toml`
- `docs/STAGE26_VERCEL_BUILD_FIX.md`

## TESTS RUN & RESULTS
1. **Python Wheel Build Test**: `python3 -m build --wheel` -> **PASSED** (Generated `dist/football_ai_platform-0.1.0-py3-none-any.whl` with zero setuptools flat-layout discovery errors).
2. **Monorepo Build**: `npm run build --workspace=packages/contracts && npm run build --workspace=apps/web` -> **PASSED** (Compiled Next.js App Router pages clean in 6.7s).
3. **Python Test Suite**: `python3 -m unittest services.ml.tests.test_vercel_entrypoint services.ml.tests.test_main services.ml.tests.test_migration_execution services.ml.tests.test_stage24_security_observability services.ml.tests.test_stage25_beta_integration` -> **PASSED** (21/21 tests passed).

## VERCEL-SPECIFIC VERIFICATION
- Simulated Vercel setuptools build process using `python3 -m build --wheel`.
- Verified that `api/index.py` imports `services.ml.app.main:app` cleanly without packaging conflicts.

## REMAINING DEPLOYMENT LIMITATIONS
- Live cloud deployment to Vercel requires the human operator to connect the repository and supply the `DATABASE_URL` environment variable for Supabase PostgreSQL persistence.
