# Stage 6 Historical Dataset Acquisition Plan (Stage 5)

## 1. ACQUISITION SCOPE & TARGETS

### 1.1 Priority Competitions (Top 5 European Leagues)
1. **English Premier League** (`EPL` / `E0`)
2. **Spanish La Liga** (`LALIGA` / `SP1`)
3. **Italian Serie A** (`SERIEA` / `I1`)
4. **German Bundesliga** (`BUNDESLIGA` / `D1`)
5. **French Ligue 1** (`LIGUE1` / `F1`)

### 1.2 Target Seasons
- **Minimum Viable Coverage**: 10 Seasons (2015/2016 – 2024/2025)
- **Preferred Historical Coverage**: 20 Seasons (2005/2006 – 2024/2025)

---

## 2. FIELD MAPPING & SOURCE ASSIGNMENTS

| Field Category | Target Database Column | Required / Optional | Primary Source | Fallback Source |
| :--- | :--- | :--- | :--- | :--- |
| Match Score (FT) | `matches.home_score`, `away_score` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Scheduled Kickoff | `matches.scheduled_kickoff_utc` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Match Status | `matches.status` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Shots & Shots on Target | `match_statistics.stat_value` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Corners & Cards | `match_statistics.stat_value` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Fouls | `match_statistics.stat_value` | **REQUIRED** | Football-Data.co.uk | API-Football |
| Possession % | `match_statistics.stat_value` | OPTIONAL | API-Football | Football-Data.org |
| xG / xGA | `match_statistics.stat_value` | OPTIONAL | API-Football | StatsBomb Open Data |
| Lineups & Squads | `match_lineups.player_id` | OPTIONAL | API-Football | Official League Feeds |

---

## 3. STAGE 6 EXECUTION SEQUENCE

When Stage 6 is authorized, ingestion will proceed in strict order:

1. **Register Data Sources**: Insert `sources` records for `FOOTBALL_DATA_UK`, `API_FOOTBALL`, `FOOTBALL_DATA_ORG`, `OPENFOOTBALL`.
2. **Download Historical CSV Batches**: Retrieve CSV files from Football-Data.co.uk for priority leagues and seasons.
3. **Persist Raw Payloads**: Store exact CSV/JSON text into `raw_source_payloads` linked to an `ingestion_runs` UUID.
4. **Log Provenance**: Create `provenance_records` entries for every fetched batch.
5. **Tag Validation States**: Mark raw ingested records as `VERIFIED` or `LIKELY`.
6. **Create Dataset Snapshot Marker**: Create `dataset_versions` entry (e.g., `v1.0-historical-2015-2025`) with strict cutoff timestamp.

***
*Confirmation: Stage 5 is research + strategy only. No historical datasets have been downloaded or imported during Stage 5.*
