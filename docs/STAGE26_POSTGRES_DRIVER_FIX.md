# PostgreSQL Driver Dialect Correction Report

## ROOT CAUSE
On production Vercel, requests to `GET /health` returned HTTP 500 with:
`ModuleNotFoundError: No module named 'psycopg2'`
Traceback:
`services/ml/app/db/session.py` -> `create_engine(DATABASE_URL)` -> `sqlalchemy.dialects.postgresql.psycopg2` -> `import psycopg2`

Because the Supabase connection string used the generic `postgresql://` or `postgres://` prefix, SQLAlchemy default behavior attempted to import the legacy `psycopg2` driver. However, the repository uses `psycopg` (psycopg v3, `psycopg[binary]>=3.1.18`).

## FILE(S) MODIFIED
- `services/ml/app/db/session.py`
- `services/ml/tests/test_main.py`
- `docs/STAGE26_POSTGRES_DRIVER_FIX.md`

## EXACT FIX
1. Added `normalize_database_url()` helper in `services/ml/app/db/session.py`:
   ```python
   def normalize_database_url(raw_url: Optional[str] = None) -> str:
       url = raw_url or settings.database_url or os.getenv("DATABASE_URL", "sqlite:///:memory:")
       if not url:
           return "sqlite:///:memory:"

       if url.startswith("postgres://"):
           return "postgresql+psycopg://" + url[len("postgres://"):]
       elif url.startswith("postgresql://"):
           return "postgresql+psycopg://" + url[len("postgresql://"):]

       return url
   ```
2. Automatically converts raw Supabase URLs starting with `postgres://` or `postgresql://` into explicit `postgresql+psycopg://` strings, forcing SQLAlchemy to use the installed `psycopg` (v3) driver.
3. Preserves `sqlite://` URLs and existing custom dialect specifications.

## TESTS RUN & RESULTS
- **Postgres Dialect Normalization Test**: `test_database_url_normalization_psycopg3` in `services/ml/tests/test_main.py` -> **PASSED**
- **Test Command**: `python3 -m unittest services.ml.tests.test_main services.ml.tests.test_vercel_entrypoint services.ml.tests.test_migration_execution services.ml.tests.test_stage24_security_observability services.ml.tests.test_stage25_beta_integration`
- **Result**: 23/23 tests passed.

## POSTGRES DRIVER VERIFIED
Confirmed that `services/ml/app/db/session.py` resolves PostgreSQL connection strings using `postgresql+psycopg://`, ensuring compatibility with `psycopg` (v3) without requiring legacy `psycopg2`.

## KNOWN LIMITATIONS
- Live database health status depends on the human operator configuring a valid Supabase `DATABASE_URL` in Vercel Project Settings.
