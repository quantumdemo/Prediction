# Data Acquisition & Overlap Strategy (Stage 5)

## 1. ACQUISITION PIPELINE ARCHITECTURE

The acquisition pipeline specifies the sequential flow from external APIs down to canonical database storage.

```
[EXTERNAL SOURCE API / CSV]
            │
            ▼
[1. ACQUISITION ADAPTER] ──(Per-source fetcher with rate limiting)
            │
            ▼
[2. RAW PAYLOAD STORAGE] ──(Store exact unparsed JSON/CSV into raw_source_payloads)
            │
            ▼
[3. SOURCE METADATA & PROVENANCE] ──(Log ingestion_run_id, source_url, timestamp_utc)
            │
            ▼
[4. DATA VALIDATION & STATE TAGGING] ──(Attach VERIFIED / LIKELY / CONFLICTING)
            │
            ▼
[5. ENTITY RESOLUTION / NORMALIZATION] ──(Map team names via club_aliases and club_external_ids)
            │
            ▼
[6. CANONICAL DB PERSISTENCE] ──(Insert into matches, match_statistics, match_lineups)
```

---

## 2. DATA OVERLAP & DUPLICATE RESOLUTION

### 2.1 Matching Keys
Matches from different sources are matched using composite key logic:
- `normalized_home_club_id` + `normalized_away_club_id` + `scheduled_date_utc` + `competition_id`

### 2.2 Entity Identity Resolution
When ingesting from a new source (e.g., API-Football ID `40` vs Football-Data.co.uk team `Liverpool`):
1. Lookup `club_external_ids` for (`source_id`, `external_id`).
2. If not found, lookup `club_aliases` for string matching.
3. If canonical club exists, bind external ID to `club_external_ids`.
4. If no canonical match exists, create a new canonical `clubs` entry or flag for review.

### 2.3 Conflict Resolution Rules
When two sources report different values for the same match statistic:
- **Final Scores / Goals**: Primary source value takes precedence if `VERIFIED`. If conflicting, log both raw payloads into `raw_source_payloads` and set `validation_state = CONFLICTING`.
- **Advanced Stats (xG / Shots)**: Store each source stat tagged with its `source_id` in `match_statistics`.

---

## 3. RAW DATA PRESERVATION MANDATES

Every ingestion run MUST preserve:
1. `source_id`: Reference to registered `sources` entry.
2. `entity_type`: Target entity (`MATCH`, `CLUB`, `LINEUP`, `INJURY`).
3. `external_identifier`: Provider's native record ID.
4. `raw_payload_json`: Exact unparsed response payload (JSON/CSV text).
5. `retrieved_at_utc`: Precise UTC retrieval timestamp.
6. `ingestion_run_id`: UUID linking to `ingestion_runs` table.
7. Secrets Exclusion: API tokens and credentials MUST NOT be logged inside `raw_source_payloads` or error logs.
