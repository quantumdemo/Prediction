# Stage 6 Historical Dataset Quality Report

## Executive Summary

- **Primary Source**: Football-Data.co.uk (Bulk Historical CSV Data)
- **Reference Entity Source**: OpenFootball (`openfootball/clubs`)
- **Pipeline Status**: `COMPLETED`
- **Total Canonical Matches Acquired**: **39**
- **Total Match Statistics Acquired**: **468**
- **Total Canonical Clubs Created**: **44**

---

## 1. Authoritative Record Counts Across All 20 Database Tables

| Table Name | Canonical Record Count | Data Category / Entity Role |
| :--- | :--- | :--- |
| `sources` | **3** | Registered Source Metadata (`FOOTBALL_DATA_UK`, `OPENFOOTBALL`, `API_FOOTBALL`) |
| `countries` | **5** | Seeded Reference Countries (`ENG`, `ESP`, `ITA`, `GER`, `FRA`) |
| `competitions` | **5** | Seeded Reference Competitions (`EPL`, `LALIGA`, `SERIEA`, `BUNDESLIGA`, `LIGUE1`) |
| `seasons` | **35** | Seeded Reference Seasons (7 Seasons per Competition) |
| `venues` | **0** | `UNAVAILABLE` in Football-Data.co.uk CSV feeds |
| `clubs` | **44** | Canonical Club Entities |
| `club_aliases` | **58** | Alternate Club Names & Variant Mappings |
| `club_external_ids` | **34** | Provider External Identifiers |
| `club_season_memberships` | **0** | Reserved for future structured membership tracking |
| `players` | **0** | `N/A` — Unavailable in Football-Data.co.uk CSV feeds |
| `player_club_memberships` | **0** | `N/A` — Unavailable in Football-Data.co.uk CSV feeds |
| `matches` | **39** | Real Historical Matches Ingested |
| `match_external_ids` | **0** | Reserved for multi-provider external match mappings |
| `match_statistics` | **468** | Real Numerical Match Statistics (Shots, SOT, Corners, Cards, Fouls) |
| `match_events` | **0** | `N/A` — Event-level data unavailable in team-aggregate CSV feeds |
| `match_lineups` | **0** | `N/A` — Lineups unavailable in team-aggregate CSV feeds |
| `raw_source_payloads` | **2** | Raw Bulk CSV Payloads Preserved |
| `provenance_records` | **2** | Batch HTTP Provenance Records |
| `dataset_versions` | **2** | Immutable Dataset Snapshot Markers |
| `ingestion_runs` | **2** | Ingestion Execution Run Logs |

---

## 2. Actual Competition & Season Match Breakdown

### Reference Entities vs Acquired Historical Matches

- **Seeded Reference Entities**: 5 countries, 5 competitions, 35 seasons.
- **Acquired Historical Match Coverage**: **39 matches** across 2 competitions in season `2024/2025`.

### Competition & Season Match Matrix

| Competition Code | Competition Name | Season Label | Acquired Match Count |
| :--- | :--- | :--- | :--- |
| `EPL` | English Premier League | `2024/2025` | **20** |
| `EPL` | English Premier League | `2018/2019` – `2023/2024` | 0 (Remote connection refused) |
| `LALIGA` | Spanish La Liga | `2024/2025` | **19** |
| `LALIGA` | Spanish La Liga | `2018/2019` – `2023/2024` | 0 (Remote connection refused) |
| `SERIEA` | Italian Serie A | `2018/2019` – `2024/2025` | 0 (Remote connection refused) |
| `BUNDESLIGA` | German Bundesliga | `2018/2019` – `2024/2025` | 0 (Remote connection refused) |
| `LIGUE1` | French Ligue 1 | `2018/2019` – `2024/2025` | 0 (Remote connection refused) |
| **TOTAL** | — | — | **39 Matches** |

---

## 3. Match Statistics Breakdown & Availability

Total Statistic Records in `match_statistics`: **468** (39 matches × 12 stat types = 468 rows).

| Statistic Type | Stat Category | Acquired Count | Availability Rate | Source Field |
| :--- | :--- | :--- | :--- | :--- |
| `SHOTS` | Team Shots | **78** (39 Home / 39 Away) | 100% | `HS`, `AS` |
| `SHOTS_ON_TARGET` | Shots on Target | **78** (39 Home / 39 Away) | 100% | `HST`, `AST` |
| `CORNERS` | Corner Kicks | **78** (39 Home / 39 Away) | 100% | `HC`, `AC` |
| `FOULS` | Fouls Committed | **78** (39 Home / 39 Away) | 100% | `HF`, `AF` |
| `YELLOW_CARDS` | Yellow Cards | **78** (39 Home / 39 Away) | 100% | `HY`, `AY` |
| `RED_CARDS` | Red Cards | **78** (39 Home / 39 Away) | 100% | `HR`, `AR` |
| `POSSESSION` | Possession % | **0** | `UNAVAILABLE` | Missing in source CSVs |
| `XG` / `XGA` | Expected Goals | **0** | `UNAVAILABLE` | Missing in source CSVs |

---

## 4. Provenance & Raw Payload Coverage

- **Canonical Matches**: 39
- **Matches Traceable to Raw Payloads**: 39 (100% Coverage)
- **Raw Payloads Preserved**: 2 (`EPL_2425`, `LALIGA_2425` raw CSVs stored in `raw_source_payloads`)
- **Provenance Records**: 2 (HTTP URL + retrieval timestamp UTC in `provenance_records`)

---

## 5. Idempotency & Validation Summary

1. **Zero Fake Football Data**: All 39 match records are real historical fixtures.
2. **Idempotency**: Re-running ingestion pipeline on identical raw source data produces 0 duplicate matches.
3. **Zero Future-Data Leakage**: Feature engineering and prediction models are strictly NOT implemented in Stage 6. Raw match outcomes only.
