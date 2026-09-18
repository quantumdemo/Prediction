# Stage 9 — Feature Registry

## Executive Overview
This document contains the authoritative feature registry (`STAGE9_FEATURE_REGISTRY_v1.0.0`) for the Football AI Intelligence & Machine-Learning Platform.

The registry defines **55 pre-match numerical features** across 12 distinct feature families. Every feature is mathematically deterministic, uses strictly pre-match historical information ($T_{match} < T_{target}$), enforces explicit missingness rules without fabrication or silent imputation, and isolates prediction targets.

---

## Complete Feature Registry (55 Features)

| Feature ID | Feature Name | Family | Window Type | Minimum History | Source Fields | Missing Data Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FEAT_FORM3_HOME` | `home_recalculated_form3` | `FORM` | `ROLLING_3` | 3 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_HOME` | `home_recalculated_form5` | `FORM` | `ROLLING_5` | 5 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM3_AWAY` | `away_recalculated_form3` | `FORM` | `ROLLING_3` | 3 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_AWAY` | `away_recalculated_form5` | `FORM` | `ROLLING_5` | 5 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM3_DIFF` | `form3_difference` | `FORM` | `ROLLING_3` | 3 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_DIFF` | `form5_difference` | `FORM` | `ROLLING_5` | 5 matches | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_SCORED_AVG5_HOME` | `home_goals_scored_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_CONCEDED_AVG5_HOME` | `home_goals_conceded_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_SCORED_AVG5_AWAY` | `away_goals_scored_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_CONCEDED_AVG5_AWAY` | `away_goals_conceded_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_SCORED_AVG5_DIFF` | `goals_scored_avg5_difference` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_CONCEDED_AVG5_DIFF` | `goals_conceded_avg5_difference` | `GOALS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_REST_DAYS_HOME` | `home_rest_days` | `REST_CONGESTION` | `RECENT_MATCH` | 1 match | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_REST_DAYS_AWAY` | `away_rest_days` | `REST_CONGESTION` | `RECENT_MATCH` | 1 match | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_REST_DAYS_DIFF` | `rest_days_difference` | `REST_CONGESTION` | `RECENT_MATCH` | 1 match | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_7_HOME` | `home_matches_last_7_days` | `REST_CONGESTION` | `DAYS_7` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_14_HOME` | `home_matches_last_14_days` | `REST_CONGESTION` | `DAYS_14` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_30_HOME` | `home_matches_last_30_days` | `REST_CONGESTION` | `DAYS_30` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_7_AWAY` | `away_matches_last_7_days` | `REST_CONGESTION` | `DAYS_7` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_14_AWAY` | `away_matches_last_14_days` | `REST_CONGESTION` | `DAYS_14` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_30_AWAY` | `away_matches_last_30_days` | `REST_CONGESTION` | `DAYS_30` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_7_DIFF` | `matches_last_7_days_difference` | `REST_CONGESTION` | `DAYS_7` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_14_DIFF` | `matches_last_14_days_difference` | `REST_CONGESTION` | `DAYS_14` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_CONGESTION_30_DIFF` | `matches_last_30_days_difference` | `REST_CONGESTION` | `DAYS_30` | 0 matches | `match_date` | `INSUFFICIENT_HISTORY` |
| `FEAT_SHOTS_AVG5_HOME` | `home_shots_avg5` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots`, `away_shots` | `MISSING_SOURCE_DATA` |
| `FEAT_SHOTS_TARGET_AVG5_HOME` | `home_shots_on_target_avg5` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots_on_target`, `away_shots_on_target` | `MISSING_SOURCE_DATA` |
| `FEAT_SHOTS_AVG5_AWAY` | `away_shots_avg5` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots`, `away_shots` | `MISSING_SOURCE_DATA` |
| `FEAT_SHOTS_TARGET_AVG5_AWAY` | `away_shots_on_target_avg5` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots_on_target`, `away_shots_on_target` | `MISSING_SOURCE_DATA` |
| `FEAT_SHOTS_AVG5_DIFF` | `shots_avg5_difference` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots`, `away_shots` | `MISSING_SOURCE_DATA` |
| `FEAT_SHOTS_TARGET_AVG5_DIFF` | `shots_on_target_avg5_difference` | `SHOTS` | `ROLLING_5` | 5 matches | `home_shots_on_target`, `away_shots_on_target` | `MISSING_SOURCE_DATA` |
| `FEAT_CORNERS_AVG5_HOME` | `home_corners_avg5` | `CORNERS` | `ROLLING_5` | 5 matches | `home_corners`, `away_corners` | `MISSING_SOURCE_DATA` |
| `FEAT_CORNERS_AVG5_AWAY` | `away_corners_avg5` | `CORNERS` | `ROLLING_5` | 5 matches | `home_corners`, `away_corners` | `MISSING_SOURCE_DATA` |
| `FEAT_CORNERS_AVG5_DIFF` | `corners_avg5_difference` | `CORNERS` | `ROLLING_5` | 5 matches | `home_corners`, `away_corners` | `MISSING_SOURCE_DATA` |
| `FEAT_FOULS_AVG5_HOME` | `home_fouls_avg5` | `FOULS` | `ROLLING_5` | 5 matches | `home_fouls`, `away_fouls` | `MISSING_SOURCE_DATA` |
| `FEAT_FOULS_AVG5_AWAY` | `away_fouls_avg5` | `FOULS` | `ROLLING_5` | 5 matches | `home_fouls`, `away_fouls` | `MISSING_SOURCE_DATA` |
| `FEAT_FOULS_AVG5_DIFF` | `fouls_avg5_difference` | `FOULS` | `ROLLING_5` | 5 matches | `home_fouls`, `away_fouls` | `MISSING_SOURCE_DATA` |
| `FEAT_YELLOW_CARDS_AVG5_HOME` | `home_yellow_cards_avg5` | `CARDS` | `ROLLING_5` | 5 matches | `home_yellow_cards`, `away_yellow_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_YELLOW_CARDS_AVG5_AWAY` | `away_yellow_cards_avg5` | `CARDS` | `ROLLING_5` | 5 matches | `home_yellow_cards`, `away_yellow_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_YELLOW_CARDS_AVG5_DIFF` | `yellow_cards_avg5_difference` | `CARDS` | `ROLLING_5` | 5 matches | `home_yellow_cards`, `away_yellow_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_RED_CARDS_AVG5_HOME` | `home_red_cards_avg5` | `CARDS` | `ROLLING_5` | 5 matches | `home_red_cards`, `away_red_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_RED_CARDS_AVG5_AWAY` | `away_red_cards_avg5` | `CARDS` | `ROLLING_5` | 5 matches | `home_red_cards`, `away_red_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_RED_CARDS_AVG5_DIFF` | `red_cards_avg5_difference` | `CARDS` | `ROLLING_5` | 5 matches | `home_red_cards`, `away_red_cards` | `MISSING_SOURCE_DATA` |
| `FEAT_CLEAN_SHEET_RATE5_HOME` | `home_clean_sheet_rate5` | `CLEAN_SHEET` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_CLEAN_SHEET_RATE5_AWAY` | `away_clean_sheet_rate5` | `CLEAN_SHEET` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_CLEAN_SHEET_RATE5_DIFF` | `clean_sheet_rate5_difference` | `CLEAN_SHEET` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_FAILED_TO_SCORE_RATE5_HOME` | `home_failed_to_score_rate5` | `FAILED_TO_SCORE` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_FAILED_TO_SCORE_RATE5_AWAY` | `away_failed_to_score_rate5` | `FAILED_TO_SCORE` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_FAILED_TO_SCORE_RATE5_DIFF` | `failed_to_score_rate5_difference` | `FAILED_TO_SCORE` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_BTTS_RATE5_HOME` | `home_historical_btts_rate5` | `HISTORICAL_BTTS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_BTTS_RATE5_AWAY` | `away_historical_btts_rate5` | `HISTORICAL_BTTS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_BTTS_RATE5_DIFF` | `historical_btts_rate5_difference` | `HISTORICAL_BTTS` | `ROLLING_5` | 5 matches | `full_time_home_goals`, `full_time_away_goals` | `INSUFFICIENT_HISTORY` |
| `FEAT_H2H_HOME_WINS` | `h2h_home_wins` | `HEAD_TO_HEAD` | `ALL_TIME` | 1 match | `full_time_result` | `INSUFFICIENT_HISTORY` |
| `FEAT_ELO_PRE_MATCH_HOME` | `home_pre_match_elo` | `ELO` | `RECENT_MATCH` | 1 snapshot | `home_elo` | `MISSING_SOURCE_DATA` |
| `FEAT_ELO_PRE_MATCH_AWAY` | `away_pre_match_elo` | `ELO` | `RECENT_MATCH` | 1 snapshot | `away_elo` | `MISSING_SOURCE_DATA` |
| `FEAT_ELO_PRE_MATCH_DIFF` | `pre_match_elo_difference` | `ELO` | `RECENT_MATCH` | 1 snapshot | `home_elo`, `away_elo` | `MISSING_SOURCE_DATA` |

---

## Metadata Standard
Every registered feature definition strictly adheres to the following metadata schema:
- **feature_id**: Unique UPPERCASE internal identifier starting with `FEAT_`.
- **name**: Lowercase snake_case human-readable feature name.
- **family**: Higher-level domain grouping (FORM, GOALS, REST_CONGESTION, SHOTS, CORNERS, FOULS, CARDS, CLEAN_SHEET, FAILED_TO_SCORE, HISTORICAL_BTTS, HEAD_TO_HEAD, ELO).
- **description**: Mathematical and operational description.
- **calculation_formula**: Deterministic formula representation.
- **window_type**: Rolling window classification (ROLLING_3, ROLLING_5, DAYS_7, DAYS_14, DAYS_30, RECENT_MATCH, ALL_TIME).
- **minimum_history_required**: Integer minimum past matches or snapshots required.
- **source_fields**: Explicit list of underlying Stage 7 canonical fields used.
- **missing_data_rule**: Explicit availability state assigned when data or history is incomplete (`INSUFFICIENT_HISTORY`, `MISSING_SOURCE_DATA`).
- **availability_cutoff**: `STRICTLY_BEFORE_MATCH_KICKOFF`
- **leakage_status**: `SAFE_PRE_MATCH`
- **version**: `STAGE9_FEATURE_DATASET_v1.0.0`
- **prediction_time_available**: `True`
