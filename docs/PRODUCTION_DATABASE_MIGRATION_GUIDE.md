# Production Supabase PostgreSQL Database Migration Guide

## Current Database State
- **Production Supabase Database**: EMPTY (No application tables currently present).
- **Target Status**: Apply complete 21-table schema DDL and performance indexes.

---

## Migration Revisions Reviewed
1. **`001_stage4_core_football_schema`**: Creates core relational football entities (sources, countries, competitions, seasons, venues, clubs, club_aliases, club_external_ids, club_season_memberships, players, player_club_memberships, matches, match_external_ids, match_statistics, match_events, match_lineups, raw_source_payloads, provenance_records, dataset_versions, ingestion_runs).
2. **`002_stage20_prediction_history_schema`**: Creates `prediction_reports` table for immutable report storage and SHA256 audit hashing.
3. **`003_stage23_production_indexes`**: Adds production performance hardening indexes (`idx_matches_kickoff_status`, `idx_matches_clubs`, `idx_pred_reports_fixture_ts`, `idx_pred_reports_status_ts`, `idx_club_aliases_name`).

---

## Tables Expected After Migration (21 Tables Total)
- `sources`
- `countries`
- `competitions`
- `seasons`
- `venues`
- `clubs`
- `club_aliases`
- `club_external_ids`
- `club_season_memberships`
- `players`
- `player_club_memberships`
- `matches`
- `match_external_ids`
- `match_statistics`
- `match_events`
- `match_lineups`
- `raw_source_payloads`
- `provenance_records`
- `dataset_versions`
- `ingestion_runs`
- `prediction_reports`
- `alembic_version` (Metadata table containing revision `003_stage23_production_indexes`)

---

## Production Migration Execution Procedure

### **Option A: Via Supabase SQL Editor (Recommended One-Time Direct Execution)**
1. Open your [Supabase Dashboard](https://supabase.com).
2. Select your production project and open the **SQL Editor** from the sidebar.
3. Click **New Query**.
4. Copy the entire contents of `docs/PRODUCTION_SUPABASE_MIGRATION.sql`.
5. Paste into the query window and click **Run**.

### **Option B: Via Alembic CLI (Automated Migration)**
Export your Supabase connection string and execute Alembic from your terminal:
```bash
export DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
cd infrastructure/database
alembic upgrade head
```

---

## Verification Queries

Execute these SQL statements in the Supabase SQL Editor to confirm successful migration:

```sql
-- 1. Verify Table Count (Should return 22 tables including alembic_version)
SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';

-- 2. Verify Alembic Version
SELECT * FROM alembic_version;

-- 3. Verify Indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;
```

---

## Important Clarifications
- **Data Ingestion**: This migration applies table structure, foreign key constraints, and indexes ONLY. No historical football data or fake sample data is inserted. Data ingestion remains a separate, controlled pipeline operation.
- **Rollback Procedure**: In case of a migration issue on an empty database, execute `DROP TABLE IF EXISTS prediction_reports, matches, clubs, competitions, countries, sources CASCADE;` and re-run `docs/PRODUCTION_SUPABASE_MIGRATION.sql`.
