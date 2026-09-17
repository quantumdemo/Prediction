# Stage 6A Production Data Acquisition & Import Plan

## Overview

This document specifies the concrete acquisition, entity resolution, and canonical database import strategy for incorporating the verified portions of the candidate historical dataset `xgabora/club-football-match-data` into the production database during subsequent authorized stages (Stage 7 / Stage 8).

---

## 1. Primary & Secondary Source Hierarchy

```
+-----------------------------------------------------------------------------------+
|                        PRODUCTION DATA ACQUISITION ARCHITECTURE                  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ PRIMARY HISTORICAL MATCH SOURCE ]                                              |
|  xgabora / Football-Data.co.uk Candidate Dataset (Matches.csv)                    |
|  --> Historical match scores, dates, and match statistics across 38 divisions.   |
|                                                                                   |
|  [ SECONDARY RATING SOURCE ]                                                      |
|  ClubElo.com (EloRatings.csv)                                                     |
|  --> Historical club Elo ratings (snapshots through June 1, 2025).                 |
|                                                                                   |
|  [ REFERENCE ENTITY RESOLUTION SOURCE ]                                           |
|  OpenFootball / Stage 8 Canonical Entity Mapping Table                            |
|  --> Canonical UUID resolution for 1,048 raw team names.                          |
|                                                                                   |
|  [ SUPPLEMENTAL LIVE DATA SOURCE (STAGE 10+) ]                                    |
|  API-Football (API-Sports)                                                        |
|  --> Live scheduled fixtures, starting XI lineups, injury reports, and real xG.  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Ingestion & Import Workflow Rules

1. **Raw Preservation**:
   * All raw candidate files remain permanently preserved in `services/ml/app/data/candidate_data/` with SHA-256 verification and `raw_source_payloads` entries.
2. **Entity Resolution Prerequisites**:
   * Prior to mass database insertion, Stage 8 Entity Resolution must build an alias mapping table resolving all 1,048 raw team string names in `Matches.csv` to canonical `clubs` UUID records.
3. **Canonical Table Persistence**:
   * Historical matches will be inserted into `matches`, match statistics into `match_statistics`, and pre-match Elo ratings into `team_ratings`.
4. **Strict Isolation of Rejected Fields**:
   * Bookmaker odds, synthetic expected goals, pre-calculated form averages, and cluster labels will be completely excluded from insertion into canonical ML training tables.
5. **Idempotent Reconciliation**:
   * The database insertion pipeline will execute idempotent UPSERT operations matching on `(competition_id, match_date, home_club_id, away_club_id)`, preserving existing Stage 6 records and filling unpopulated fields.
