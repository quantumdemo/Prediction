# Data Ingestion Pipeline Architecture (Stage 6)

## Pipeline Flow

```
[Football-Data.co.uk CSV]
           │
           ▼
[1. FootballDataUKAdapter] ──(HTTP Fetch with Exponential Backoff)
           │
           ▼
[2. Raw Payload Storage] ──(Insert raw JSON/CSV into raw_source_payloads)
           │
           ▼
[3. Source Provenance Logging] ──(Insert source_url & timestamp into provenance_records)
           │
           ▼
[4. Entity Resolution & Mapping] ──(Lookup club_external_ids / club_aliases)
           │
           ▼
[5. Idempotent Match Persistence] ──(Insert/Update matches & match_statistics)
           │
           ▼
[6. Ingestion Run & Dataset Marker] ──(Update ingestion_runs & dataset_versions)
```

## Idempotency Rules

- Match lookup uses composite natural key: (`competition_id`, `season_id`, `home_club_id`, `away_club_id`, `scheduled_kickoff_utc`).
- Re-running the pipeline on identical raw source data produces 0 duplicate records (`total_duplicates` incremented, scores and stats updated idempotently).
