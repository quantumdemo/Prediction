# Stage 9 — Feature Engineering Specification

## Executive Overview
This document specifies the exact feature engineering principles, mathematical calculations, and zero future-data leakage safeguards applied during **Stage 9 — Feature Engineering Engine**.

The engine transforms Stage 8 canonical historical entities and fixtures (`STAGE8_ENTITY_MAPPING_v1.0.0`) into prediction-time-safe numerical features (`STAGE9_FEATURE_DATASET_v1.0.0`).

---

## Core Directives & Zero Future-Data Leakage
1. **Strict Pre-Match Cutoff**: For any historical match $T$, feature calculations use strictly matches $< T$. Match $T$'s own outcome or post-match statistics are 100% excluded.
2. **Explicit Target Separation**: Feature vectors are strictly separated from target variables (`full_time_result`, `full_time_home_goals`, `full_time_away_goals`, `total_goals`, `btts`).
3. **No Unvalidated / Restricted Field Usage**:
   - Odds fields (`REJECTED_ODDS`) are 100% excluded.
   - Synthetic xG (`REJECTED_UNVERIFIED`) is 100% excluded.
   - Cluster labels (`REJECTED_LEAKAGE`) are 100% excluded.
   - Raw source form (`Form3Home`, `Form5Home`) is 100% excluded and recalculated from canonical match outcomes.
4. **Stage 7 Quarantined Matches Excluded**: All 21 quarantined Stage 7 matches remain excluded from feature calculations.
5. **No Imputation / Fabrication**: Missing source statistics and insufficient history states are recorded explicitly as `MISSING_SOURCE_DATA` or `INSUFFICIENT_HISTORY` without silent default imputation.

---

## Feature Family Mathematical Definitions

### 1. Form Features
- `FEAT_FORM3_HOME` / `FEAT_FORM3_AWAY`: Sum of points in previous 3 completed matches (Win=3, Draw=1, Loss=0).
- `FEAT_FORM5_HOME` / `FEAT_FORM5_AWAY`: Sum of points in previous 5 completed matches.
- `FEAT_FORM3_DIFF` / `FEAT_FORM5_DIFF`: Home Form minus Away Form.

### 2. Goals Features
- `FEAT_GOALS_SCORED_AVG5_HOME` / `AWAY`: Mean goals scored in previous 5 completed matches.
- `FEAT_GOALS_CONCEDED_AVG5_HOME` / `AWAY`: Mean goals conceded in previous 5 completed matches.
- `FEAT_GOALS_SCORED_AVG5_DIFF` / `FEAT_GOALS_CONCEDED_AVG5_DIFF`: Home average minus Away average.

### 3. Rest Days & Fixture Congestion
- `FEAT_REST_DAYS_HOME` / `AWAY`: Days elapsed between target match date and previous completed match date.
- `FEAT_REST_DAYS_DIFF`: Home rest days minus Away rest days.
- `FEAT_CONGESTION_7_HOME` / `AWAY`: Count of completed matches in previous 7 days ($0 < T_{target} - T_{match} \le 7$).
- `FEAT_CONGESTION_14_HOME` / `AWAY`: Count of completed matches in previous 14 days ($0 < T_{target} - T_{match} \le 14$).
- `FEAT_CONGESTION_30_HOME` / `AWAY`: Count of completed matches in previous 30 days ($0 < T_{target} - T_{match} \le 30$).
- `FEAT_CONGESTION_7_DIFF` / `14_DIFF` / `30_DIFF`: Home congestion count minus Away congestion count.

### 4. Shots & Target Features
- `FEAT_SHOTS_AVG5_HOME` / `AWAY`: Mean total shots over previous 5 matches with valid shot observations.
- `FEAT_SHOTS_TARGET_AVG5_HOME` / `AWAY`: Mean shots on target over previous 5 matches with valid target observations.
- `FEAT_SHOTS_AVG5_DIFF` / `FEAT_SHOTS_TARGET_AVG5_DIFF`: Home average minus Away average.

### 5. Corners Features
- `FEAT_CORNERS_AVG5_HOME` / `AWAY`: Mean corners awarded over previous 5 matches with valid corner statistics.
- `FEAT_CORNERS_AVG5_DIFF`: Home average corners minus Away average corners.

### 6. Fouls Features
- `FEAT_FOULS_AVG5_HOME` / `AWAY`: Mean fouls committed over previous 5 matches with valid foul statistics.
- `FEAT_FOULS_AVG5_DIFF`: Home average fouls minus Away average fouls.

### 7. Card Features
- `FEAT_YELLOW_CARDS_AVG5_HOME` / `AWAY`: Mean yellow cards over previous 5 matches with card statistics.
- `FEAT_YELLOW_CARDS_AVG5_DIFF`: Home yellow card average minus Away yellow card average.
- `FEAT_RED_CARDS_AVG5_HOME` / `AWAY`: Mean red cards over previous 5 matches with card statistics.
- `FEAT_RED_CARDS_AVG5_DIFF`: Home red card average minus Away red card average.

### 8. Clean-Sheet Features
- `FEAT_CLEAN_SHEET_RATE5_HOME` / `AWAY`: Rate of clean sheets over previous 5 completed matches ($\text{clean\_sheet} = 1 \text{ if } \text{opponent\_goals} == 0 \text{ else } 0$).
- `FEAT_CLEAN_SHEET_RATE5_DIFF`: Home clean sheet rate minus Away clean sheet rate.

### 9. Failed-To-Score Features
- `FEAT_FAILED_TO_SCORE_RATE5_HOME` / `AWAY`: Rate of matches failing to score over previous 5 completed matches ($\text{failed\_to\_score} = 1 \text{ if } \text{team\_goals} == 0 \text{ else } 0$).
- `FEAT_FAILED_TO_SCORE_RATE5_DIFF`: Home failed to score rate minus Away failed to score rate.

### 10. Historical BTTS Features
- `FEAT_BTTS_RATE5_HOME` / `AWAY`: Historical BTTS rate over previous 5 completed matches ($\text{btts} = 1 \text{ if } \text{team\_goals} > 0 \text{ and } \text{opponent\_goals} > 0 \text{ else } 0$).
- `FEAT_BTTS_RATE5_DIFF`: Home historical BTTS rate minus Away historical BTTS rate.

### 11. Head-to-Head Features
- `FEAT_H2H_HOME_WINS`: Count of wins by home team in past H2H meetings prior to match $T$.

### 12. Pre-Match Elo Features
- `FEAT_ELO_PRE_MATCH_HOME` / `AWAY`: Most recent Elo rating snapshot strictly prior to kickoff.
- `FEAT_ELO_PRE_MATCH_DIFF`: Home pre-match Elo minus Away pre-match Elo.
