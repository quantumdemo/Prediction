# Database Schema Specification (Stage 4)

## Overview

The Football AI Intelligence & Machine-Learning Platform uses a normalized PostgreSQL relational database schema to represent football entities, match statistics, event details, source provenance, and raw payloads.

## Core Schema Entities

```
+----------------+       +-------------------+       +------------------+
|   countries    |<------|   competitions    |<------|     seasons      |
+----------------+       +-------------------+       +------------------+
        ^                          ^                           ^
        |                          |                           |
+----------------+       +-------------------+                 |
|     venues     |       |club_season_mships |-----------------+
+----------------+       +-------------------+
        ^                          ^
        |                          |
+----------------+                 |
|     clubs      |-----------------+
+----------------+
   |   |     |
   |   |     +---------> club_aliases
   |   +---------------> club_external_ids
   |
   +---------------------------------------+
   | (Home / Away)                         |
   v                                       v
+---------------------------------------------------------------+
|                            matches                            |
+---------------------------------------------------------------+
   |               |                   |                  |
   v               v                   v                  v
match_ext_ids  match_stats        match_events       match_lineups
```

## Entity Descriptions

### 1. Source Registry (`sources`)
- Stores registered external data providers (e.g. `OPENFOOTBALL`, `FOOTBALL_DATA_UK`, `API_FOOTBALL`).
- Columns: `id` (UUID PK), `code` (UNIQUE), `name`, `source_type`, `base_url`, `license_notes`, `reliability_notes`, `is_active`, timestamps.

### 2. Countries (`countries`)
- Stores ISO country entities.
- Columns: `id` (UUID PK), `code` (3-char UNIQUE), `name` (UNIQUE), `region`, `is_active`, timestamps.

### 3. Competitions (`competitions`)
- Stores football competitions (leagues, cups, tournaments).
- Columns: `id` (UUID PK), `country_id` (FK), `code` (UNIQUE), `name`, `competition_type`, `governing_body`, `is_active`, timestamps.

### 4. Seasons (`seasons`)
- Stores competition season intervals.
- Columns: `id` (UUID PK), `competition_id` (FK), `label` (e.g., '2024/2025'), `start_date`, `end_date`, `is_current`, timestamps.
- Constraints: UNIQUE(`competition_id`, `label`).

### 5. Venues / Stadiums (`venues`)
- Stores stadium metadata.
- Columns: `id` (UUID PK), `country_id` (FK), `canonical_name`, `city`, `capacity`, `is_active`, timestamps.

### 6. Clubs (`clubs`)
- Stores canonical club entities. Populated purely by sports parameters; popularity or fanbase metrics are forbidden.
- Columns: `id` (UUID PK), `country_id` (FK), `canonical_name` (UNIQUE), `short_name`, `city`, `venue_id` (FK), `is_active`, timestamps.

### 7. Club Aliases (`club_aliases`)
- Stores alternate club names for entity resolution across different data feeds.
- Columns: `id` (UUID PK), `club_id` (FK), `alias_name` (UNIQUE), `source_id` (FK), timestamp.

### 8. Club External Identifiers (`club_external_ids`)
- Maps provider-specific club IDs (e.g. API-Football ID `40`) to canonical club UUIDs.
- Columns: `id` (UUID PK), `club_id` (FK), `source_id` (FK), `external_id`, `source_club_name`, timestamps.
- Constraints: UNIQUE(`source_id`, `external_id`).

### 9. Club Season Memberships (`club_season_memberships`)
- Tracks historical club participation in competitions per season.
- Columns: `id` (UUID PK), `club_id` (FK), `competition_id` (FK), `season_id` (FK), timestamp.
- Constraints: UNIQUE(`club_id`, `season_id`).

### 10. Players (`players`)
- Stores player entities.
- Columns: `id` (UUID PK), `country_id` (FK), `canonical_name`, `date_of_birth`, `position`, `is_active`, timestamps.

### 11. Player Club Memberships (`player_club_memberships`)
- Tracks historical player squad memberships.
- Columns: `id` (UUID PK), `player_id` (FK), `club_id` (FK), `season_id` (FK), `shirt_number`, `start_date`, `end_date`, timestamp.

### 12. Matches / Fixtures (`matches`)
- Core match entity.
- Columns: `id` (UUID PK), `competition_id` (FK), `season_id` (FK), `home_club_id` (FK), `away_club_id` (FK), `venue_id` (FK), `scheduled_kickoff_utc`, `actual_kickoff_utc`, `status` (Enum: `SCHEDULED`, `LIVE`, `COMPLETED`, `POSTPONED`, `CANCELLED`, `ABANDONED`, `SUSPENDED`, `UNKNOWN`), `home_score`, `away_score`, `validation_state` (Enum: `VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`), timestamps.
- Constraints: CHECK(`home_club_id <> away_club_id`).

### 13. Match External Identifiers (`match_external_ids`)
- Maps provider-specific match IDs to canonical match UUIDs.
- Columns: `id` (UUID PK), `match_id` (FK), `source_id` (FK), `external_match_id`, timestamp.
- Constraints: UNIQUE(`source_id`, `external_match_id`).

### 14. Match Statistics (`match_statistics`)
- Stores numerical statistics (goals, shots, shots on target, possession, corners, cards, fouls, xG, etc.).
- Columns: `id` (UUID PK), `match_id` (FK), `club_id` (FK), `stat_type`, `stat_value` (Numeric), `period`, `source_id` (FK), `validation_state`, timestamp.

### 15. Match Events (`match_events`)
- Stores granular match events (goals, cards, substitutions, penalties).
- Columns: `id` (UUID PK), `match_id` (FK), `club_id` (FK), `player_id` (FK), `event_category`, `minute`, `extra_minute`, `source_id` (FK), `validation_state`, timestamp.

### 16. Match Lineups (`match_lineups`)
- Stores starting lineups and bench designations.
- Columns: `id` (UUID PK), `match_id` (FK), `club_id` (FK), `player_id` (FK), `role` (`STARTING`, `BENCH`, `MANAGER`), `position`, `shirt_number`, `source_id` (FK), timestamp.

### 17. Raw Source Payloads (`raw_source_payloads`)
- Preserves exact raw JSON payloads from external source API responses before normalization.
- Columns: `id` (UUID PK), `source_id` (FK), `entity_type`, `external_identifier`, `raw_payload_json` (TEXT/JSONB), `retrieved_at_utc`, `ingestion_run_id`.

### 18. Provenance Records (`provenance_records`)
- Links every database record to its source URL, retrieval time, and validation state.
- Columns: `id` (UUID PK), `entity_type`, `entity_id` (UUID), `source_id` (FK), `source_url`, `retrieved_at_utc`, `validation_state`, `notes`.

### 19. Dataset Versions (`dataset_versions`)
- Stores immutable dataset snapshot markers for zero-leakage model training and backtesting.
- Columns: `id` (UUID PK), `version_label` (UNIQUE), `cutoff_timestamp_utc`, `record_count`, `notes`, timestamp.

### 20. Ingestion Runs (`ingestion_runs`)
- Logs background ingestion execution status and metrics.
- Columns: `id` (UUID PK), `source_id` (FK), `status` (`STARTED`, `COMPLETED`, `FAILED`, `PARTIAL`), `records_ingested`, `error_log`, `started_at_utc`, `completed_at_utc`.
