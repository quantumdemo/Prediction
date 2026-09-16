# Database Migration & Local Setup Guide (Stage 4)

## Migration Tooling

Migrations are managed via **Alembic** (Python). Migration scripts are stored in `infrastructure/database/migrations/versions/`.

## Local Setup

### 1. Prerequisites
- PostgreSQL instance or SQLite (for local embedded development).
- Python environment with `alembic` and `sqlalchemy` installed (`pip install -r requirements.txt`).

### 2. Configuration
Configure `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/football_ai_db
```

### 3. Running Migrations

To apply all migrations up to head:
```bash
alembic -c infrastructure/database/alembic.ini upgrade head
```

To rollback the last migration:
```bash
alembic -c infrastructure/database/alembic.ini downgrade -1
```

## Production Migration Principles

1. **Zero Downtime**: Migrations must be backward-compatible (Add -> Migrate -> Deprecate -> Drop).
2. **Automated CI/CD**: Migrations execute automatically prior to application deployment.
3. **No Direct Production DDL**: Schema changes must be committed as versioned Alembic migration scripts.
