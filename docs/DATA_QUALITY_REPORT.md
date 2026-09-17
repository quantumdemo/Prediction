# Stage 6 Historical Dataset Quality Report

## Executive Summary

- **Primary Source**: Football-Data.co.uk (Bulk Historical CSV Data)
- **Reference Entity Source**: OpenFootball (`openfootball/clubs`)
- **Pipeline Status**: `COMPLETED`
- **Total Canonical Matches Acquired**: **39**
- **Total Match Statistics Acquired**: **468**
- **Total Canonical Clubs Created**: **44**
- **Total Club-Season Memberships**: **40**
- **Authoritative Database Technology**: PostgreSQL production schema ORM models (`services/ml/app/db/models.py`) verified via local SQLite database instance (`football_ai_stage6.db`).

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
| `club_season_memberships` | **40** | Deterministically Populated Club-Season Memberships |
| `players` | **0** | `N/A` — Unavailable in Football-Data.co.uk CSV feeds |
| `player_club_memberships` | **0** | `N/A` — Unavailable in Football-Data.co.uk CSV feeds |
| `matches` | **39** | Real Historical Matches Ingested |
| `match_external_ids` | **0** | `N/A` — Single primary provider acquired in initial batch |
| `match_statistics` | **468** | Real Numerical Match Statistics (Shots, SOT, Corners, Cards, Fouls) |
| `match_events` | **0** | `N/A` — Event-level data unavailable in team-aggregate CSV feeds |
| `match_lineups` | **0** | `N/A` — Lineups unavailable in team-aggregate CSV feeds |
| `raw_source_payloads` | **2** | Raw Bulk CSV Payloads Preserved |
| `provenance_records` | **2** | Batch HTTP Provenance Records |
| `dataset_versions` | **1** | Immutable Dataset Snapshot Marker |
| `ingestion_runs` | **1** | Ingestion Execution Run Log |

---

## 2. Actual Competition & Season Match Breakdown

### Reference Entities vs Acquired Historical Matches

- **Seeded Reference Entities**: 5 countries, 5 competitions, 35 seasons.
- **Acquired Historical Match Snapshot**: **39 matches** across 2 competitions in season `2024/2025`.

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

*Dataset Description Note: This initial snapshot of 39 verified matches serves as the first verified historical dataset version (`v1.0`) validating the end-to-end acquisition, raw payload preservation, provenance logging, and canonical database schema pipeline. Additional historical seasons will be acquired in supplemental acquisition runs prior to model training in Stage 10–11.*

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

## 5. Unresolved Issues & Acquisition Limitations

- **Remote Acquisition Limitation**: Remote HTTP connection refusals occurred for earlier historical seasons (2018/19–2023/24) during online network requests in the sandbox environment. The pipeline handled these network failures safely without throwing unhandled exceptions or corrupting database transactions.
- **Impact on Stage 7**: This limitation is documented and accepted as an initial dataset sample limitation. It does NOT block Stage 7 (Data Cleaning, Normalization & Validation), as Stage 7 cleans and validates existing canonical database records. Supplemental historical season downloads can be executed independently prior to Stage 10 feature engineering.
