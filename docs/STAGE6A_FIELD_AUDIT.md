# Stage 6A Field-Level Data Audit & Classification

## Overview

This document presents the exhaustive field-level audit of all 56 columns in the candidate dataset `Matches.csv` (238,858 rows) and all 6 columns in `EloRatings.csv` (273,972 rows). Every field is classified into a strict production status according to the project's **Master Control Specification** and **Engineering Constitution**.

---

## 1. Column Inventory & Population Statistics (`Matches.csv`)

| Column Name | Populated Count | Missing Count | Populated % | Field Category | Stated Source | Production Status | Classification Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Division` | 238,858 | 0 | 100.0% | Identification | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Essential competition code. |
| `MatchDate` | 238,858 | 0 | 100.0% | Identification | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Canonical date (`YYYY-MM-DD`). |
| `MatchTime` | 134,812 | 104,046 | 56.4% | Identification | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Kickoff time (where available). |
| `HomeTeam` | 238,858 | 0 | 100.0% | Identification | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Raw home club entity name. |
| `AwayTeam` | 238,858 | 0 | 100.0% | Identification | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Raw away club entity name. |
| `FTHome` | 238,858 | 0 | 100.0% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Full-time home goals target. |
| `FTAway` | 238,858 | 0 | 100.0% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Full-time away goals target. |
| `FTResult` | 238,858 | 0 | 100.0% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Full-time result (`H`, `D`, `A`). |
| `HTHome` | 227,118 | 11,740 | 95.1% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Half-time home goals. |
| `HTAway` | 227,118 | 11,740 | 95.1% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Half-time away goals. |
| `HTResult` | 227,118 | 11,740 | 95.1% | Result | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Half-time result (`H`, `D`, `A`). |
| `HomeShots` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Total home shots. |
| `AwayShots` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Total away shots. |
| `HomeTarget` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Home shots on target. |
| `AwayTarget` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Away shots on target. |
| `HomeFouls` | 122,810 | 116,048 | 51.4% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Home fouls committed. |
| `AwayFouls` | 122,810 | 116,048 | 51.4% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Away fouls committed. |
| `HomeCorners` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Home corners won. |
| `AwayCorners` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Away corners won. |
| `HomeYellow` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Home yellow cards. |
| `AwayYellow` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Away yellow cards. |
| `HomeRed` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Home red cards. |
| `AwayRed` | 128,512 | 110,346 | 53.8% | Statistics | Football-Data.co.uk | **APPROVED_HISTORICAL_FIELD** | Away red cards. |
| `HomeElo` | 238,858 | 0 | 100.0% | Rating | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Sourced pre-match Elo rating. |
| `AwayElo` | 238,858 | 0 | 100.0% | Rating | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Sourced pre-match Elo rating. |
| `HomeElo_Diff` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REQUIRES_RECALCULATION** | Pre-calculated differential (`HomeElo - AwayElo`). |
| `Form3Home` | 238,858 | 0 | 100.0% | Form | Author-Derived | **REQUIRES_RECALCULATION** | Must be computed in Stage 9 feature engine. |
| `Form5Home` | 238,858 | 0 | 100.0% | Form | Author-Derived | **REQUIRES_RECALCULATION** | Must be computed in Stage 9 feature engine. |
| `Form3Away` | 238,858 | 0 | 100.0% | Form | Author-Derived | **REQUIRES_RECALCULATION** | Must be computed in Stage 9 feature engine. |
| `Form5Away` | 238,858 | 0 | 100.0% | Form | Author-Derived | **REQUIRES_RECALCULATION** | Must be computed in Stage 9 feature engine. |
| `Form3_Diff` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REQUIRES_RECALCULATION** | Recalculated in Stage 9. |
| `Form5_Diff` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REQUIRES_RECALCULATION** | Recalculated in Stage 9. |
| `OddHome` | 238,858 | 0 | 100.0% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `OddDraw` | 238,858 | 0 | 100.0% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `OddAway` | 238,858 | 0 | 100.0% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `MaxHome` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `MaxDraw` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `MaxAway` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `Over25` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `Under25` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `HandiHome` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `HandiAway` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `HandiLine` | 182,410 | 56,448 | 76.4% | Odds/Market | Football-Data.co.uk | **REJECTED_ODDS** | Forbidden as ML feature by REQ-MKT-004. |
| `ImpliedProbHome` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REJECTED_ODDS** | Derived directly from bookmaker odds. |
| `ImpliedProbDraw` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REJECTED_ODDS** | Derived directly from bookmaker odds. |
| `ImpliedProbAway` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REJECTED_ODDS** | Derived directly from bookmaker odds. |
| `ExpectedGoalsHome` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REJECTED_UNVERIFIED** | Synthetic linear estimate based on odds & shots. |
| `ExpectedGoalsAway` | 238,858 | 0 | 100.0% | Derived | Author-Derived | **REJECTED_UNVERIFIED** | Synthetic linear estimate based on odds & shots. |
| `HomeRating` | 238,858 | 0 | 100.0% | Rating | Author-Derived | **REQUIRES_RECALCULATION** | Derived composite strength rating. |
| `AwayRating` | 238,858 | 0 | 100.0% | Rating | Author-Derived | **REQUIRES_RECALCULATION** | Derived composite strength rating. |
| `ClusterLabel` | 238,858 | 0 | 100.0% | Cluster | Author-Derived | **REJECTED_LEAKAGE** | Pre-calculated K-Means cluster assignment. |
| `ClusterProb` | 238,858 | 0 | 100.0% | Cluster | Author-Derived | **REJECTED_LEAKAGE** | Pre-calculated cluster confidence score. |
| `ShotAccuracyHome` | 128,512 | 110,346 | 53.8% | Statistics | Author-Derived | **REQUIRES_RECALCULATION** | Derived (`HomeTarget / HomeShots`). |
| `ShotAccuracyAway` | 128,512 | 110,346 | 53.8% | Statistics | Author-Derived | **REQUIRES_RECALCULATION** | Derived (`AwayTarget / AwayShots`). |
| `DefensivePressureHome` | 122,810 | 116,048 | 51.4% | Statistics | Author-Derived | **REQUIRES_RECALCULATION** | Derived (`HomeFouls + HomeYellow*2 + HomeRed*5`). |
| `DefensivePressureAway` | 122,810 | 116,048 | 51.4% | Statistics | Author-Derived | **REQUIRES_RECALCULATION** | Derived (`AwayFouls + AwayYellow*2 + AwayRed*5`). |

---

## 2. Column Inventory (`EloRatings.csv`)

| Column Name | Populated Count | Missing Count | Populated % | Stated Source | Production Status | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Rank` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Global club ranking snapshot. |
| `Team` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Raw club entity name. |
| `Country` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Country string identifier. |
| `Level` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Division tier level (1, 2, etc.). |
| `Elo` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Historical Elo rating score. |
| `Date` | 273,972 | 0 | 100.0% | ClubElo.com | **APPROVED_REFERENCE_FIELD** | Snapshot date (`YYYY-MM-DD`). |
