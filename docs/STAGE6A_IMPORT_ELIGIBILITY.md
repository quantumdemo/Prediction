# Stage 6A Field Import Eligibility & Group Classification

## Overview

Based on the evidence gathered during Stage 6A, all 56 fields from `Matches.csv` and 6 fields from `EloRatings.csv` are grouped into three strict import eligibility classifications:

* **GROUP A — SAFE CANDIDATE DATA**: Approved for historical ingestion into canonical production database tables following Stage 7/8 cleaning and entity resolution.
* **GROUP B — REQUIRES TRANSFORMATION / RECOMPUTATION**: Excluded from direct database import, but approved for deterministic recomputation in Stage 9 (Feature Engineering Engine).
* **GROUP C — REJECTED**: Strictly prohibited from entering the production ML feature pipeline.

---

## 1. GROUP A — SAFE CANDIDATE DATA (Approved for Import)

| Field Name | Source | Database Destination Table | Column Type | Ingestion Treatment |
| :--- | :--- | :--- | :--- | :--- |
| `Division` | Football-Data.co.uk | `competitions` | Identification | Map code to canonical competition ID. |
| `MatchDate` | Football-Data.co.uk | `matches.match_date` | Date | Parse to ISO DATE. |
| `MatchTime` | Football-Data.co.uk | `matches.kickoff_time` | Time | Parse to TIME (where available). |
| `HomeTeam` | Football-Data.co.uk | `matches.home_club_id` | Foreign Key | Resolve to canonical club UUID in Stage 8. |
| `AwayTeam` | Football-Data.co.uk | `matches.away_club_id` | Foreign Key | Resolve to canonical club UUID in Stage 8. |
| `FTHome` | Football-Data.co.uk | `matches.home_score` | Target | Ground-truth full-time home goals. |
| `FTAway` | Football-Data.co.uk | `matches.away_score` | Target | Ground-truth full-time away goals. |
| `FTResult` | Football-Data.co.uk | `matches.outcome` | Target | Ground-truth match outcome (`H`, `D`, `A`). |
| `HTHome` | Football-Data.co.uk | `matches.ht_home_score` | Result | Half-time home goals (where available). |
| `HTAway` | Football-Data.co.uk | `matches.ht_away_score` | Result | Half-time away goals (where available). |
| `HTResult` | Football-Data.co.uk | `matches.ht_outcome` | Result | Half-time outcome (`H`, `D`, `A`). |
| `HomeShots` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `SHOTS_TOTAL` (Home). |
| `AwayShots` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `SHOTS_TOTAL` (Away). |
| `HomeTarget` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `SHOTS_ON_TARGET` (Home). |
| `AwayTarget` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `SHOTS_ON_TARGET` (Away). |
| `HomeFouls` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `FOULS` (Home). |
| `AwayFouls` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `FOULS` (Away). |
| `HomeCorners` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `CORNERS` (Home). |
| `AwayCorners` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `CORNERS` (Away). |
| `HomeYellow` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `YELLOW_CARDS` (Home). |
| `AwayYellow` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `YELLOW_CARDS` (Away). |
| `HomeRed` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `RED_CARDS` (Home). |
| `AwayRed` | Football-Data.co.uk | `match_statistics` | Statistic | Ingest as `RED_CARDS` (Away). |
| `HomeElo` | ClubElo.com | `team_ratings` | Reference | Ingest as pre-match Elo rating snapshot. |
| `AwayElo` | ClubElo.com | `team_ratings` | Reference | Ingest as pre-match Elo rating snapshot. |

---

## 2. GROUP B — REQUIRES TRANSFORMATION / RECOMPUTATION

| Field Name | Reason for Exclusion from Direct Import | Stage 9 Recomputation Strategy |
| :--- | :--- | :--- |
| `Form3Home` | Pre-calculated author feature. | Recompute rolling 3-match points average chronologically. |
| `Form5Home` | Pre-calculated author feature. | Recompute rolling 5-match points average chronologically. |
| `Form3Away` | Pre-calculated author feature. | Recompute rolling 3-match points average chronologically. |
| `Form5Away` | Pre-calculated author feature. | Recompute rolling 5-match points average chronologically. |
| `HomeElo_Diff` | Simple differential arithmetic. | Compute as `HomeElo - AwayElo` during feature building. |
| `Form3_Diff` | Simple differential arithmetic. | Compute as `Form3Home - Form3Away`. |
| `Form5_Diff` | Simple differential arithmetic. | Compute as `Form5Home - Form5Away`. |
| `ShotAccuracyHome` | Post-match derived ratio. | Compute as `HomeTarget / HomeShots`. |
| `ShotAccuracyAway` | Post-match derived ratio. | Compute as `AwayTarget / AwayShots`. |

---

## 3. GROUP C — REJECTED (Forbidden from Production Feature Pipeline)

| Field / Group Name | Field Classification Code | Primary Rejection Reason |
| :--- | :--- | :--- |
| `OddHome`, `OddDraw`, `OddAway` | `REJECTED_ODDS` | Forbidden as ML feature under **REQ-MKT-004** & **REQ-ML-001**. |
| `MaxHome`, `MaxDraw`, `MaxAway` | `REJECTED_ODDS` | Forbidden as ML feature under **REQ-MKT-004** & **REQ-ML-001**. |
| `Over25`, `Under25` | `REJECTED_ODDS` | Forbidden as ML feature under **REQ-MKT-004** & **REQ-ML-001**. |
| `HandiHome`, `HandiAway`, `HandiLine` | `REJECTED_ODDS` | Forbidden as ML feature under **REQ-MKT-004** & **REQ-ML-001**. |
| `ImpliedProbHome`, `Draw`, `Away` | `REJECTED_ODDS` | Directly derived from bookmaker odds prices. |
| `ExpectedGoalsHome`, `Away` | `REJECTED_UNVERIFIED` | Synthetic linear estimate derived from odds & shots. |
| `ClusterLabel`, `ClusterProb` | `REJECTED_LEAKAGE` | Global dataset clustering introduces future-data leakage. |
| `HomeRating`, `AwayRating` | `REQUIRES_RECALCULATION` | Author proprietary composite formula unknown. |
