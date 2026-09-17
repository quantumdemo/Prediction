# Stage 6A Cross-Source Match Reconciliation

## Overview

During Stage 6, the platform ingested **39 canonical historical matches** (EPL 2024/25: 20 matches; La Liga 2024/25: 19 matches) into `football_ai_stage6.db` directly from raw Football-Data.co.uk CSV files.

This document presents the deterministic cross-source reconciliation comparing those 39 independently acquired Stage 6 database records against the candidate dataset `Matches.csv`.

---

## 1. Reconciliation Audit Results

| Audit Dimension | Measured Metric | Result / Discrepancy Status |
| :--- | :--- | :--- |
| **Stage 6 Database Baseline Count** | **39 matches** | 20 EPL 2024/25, 19 La Liga 2024/25 |
| **Candidate Dataset Matches Found** | **39 matches** | **100.0% Match Rate** (39 / 39 matches identified) |
| **Exact Score Alignment** | **39 matches** | **100.0% Score Agreement** (0 score conflicts) |
| **Full-Time Goal Conflicts** | **0 conflicts** | Perfect 1:1 match across all home and away goals. |
| **Half-Time Goal Conflicts** | **0 conflicts** | Perfect 1:1 match across all half-time scores. |
| **Match Statistic Conflicts** | **0 conflicts** | Shots, Corners, Fouls, Cards align exactly with Stage 6 DB. |
| **Date & Competition Conflicts** | **0 conflicts** | All match dates and league codes match exactly. |

---

## 2. Overlapping Match Sample Verification

Below is an explicit sample comparison of 5 matches across English Premier League and Spanish La Liga between the Stage 6 PostgreSQL database and the candidate dataset `Matches.csv`:

| Competition | Match Date | Home Club | Away Club | Stage 6 DB Score | Candidate Score | Reconciliation Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Premier League | `2024-08-16` | Manchester United | Fulham | `1 - 0` | `1 - 0` | **EXACT MATCH** |
| Premier League | `2024-08-17` | Ipswich Town | Liverpool | `0 - 2` | `0 - 2` | **EXACT MATCH** |
| Premier League | `2024-08-17` | Arsenal | Wolverhampton Wanderers | `2 - 0` | `2 - 0` | **EXACT MATCH** |
| La Liga | `2024-08-15` | Athletic Club | Getafe | `1 - 1` | `1 - 1` | **EXACT MATCH** |
| La Liga | `2024-08-17` | Valencia | Barcelona | `1 - 2` | `1 - 2` | **EXACT MATCH** |

---

## 3. Preservation Policy

1. **Stage 6 Database Integrity**:
   * The existing 39 Stage 6 database matches remain completely untouched in `football_ai_stage6.db`.
2. **Canonical Deduplication Rules**:
   * During future Stage 7/8 import operations, candidate matches overlapping with existing Stage 6 records will be matched on `(competition_id, match_date, home_club_id, away_club_id)`. Existing records will be retained with primary priority, and candidate fields will populate missing secondary attributes.
