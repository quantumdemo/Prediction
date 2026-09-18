# Stage 9 — Feature Quality Report

## Executive Summary
* **Input Entity Mapping Version**: `STAGE8_ENTITY_MAPPING_v1.0.0`
* **Output Feature Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
* **Total Canonical Target Fixtures Processed**: **238,837**
* **Total Feature Vectors Generated**: **238,837**
* **Registered Feature Definitions**: **55**
* **Stage 7 Quarantined Matches Excluded**: **21 / 21 (100.0%)**

---

## Measured Feature-Level Coverage Report (All 238,837 Target Fixtures)

| Feature ID | Feature Name | Family | PRESENT | INSUFFICIENT_HISTORY | MISSING_SOURCE_DATA | Coverage % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FEAT_FORM3_HOME` | `home_recalculated_form3` | FORM | 237,037 | 1,800 | 0 | 99.2% |
| `FEAT_FORM5_HOME` | `home_recalculated_form5` | FORM | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_FORM3_AWAY` | `away_recalculated_form3` | FORM | 236,997 | 1,840 | 0 | 99.2% |
| `FEAT_FORM5_AWAY` | `away_recalculated_form5` | FORM | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_FORM3_DIFF` | `form3_difference` | FORM | 236,137 | 2,700 | 0 | 98.9% |
| `FEAT_FORM5_DIFF` | `form5_difference` | FORM | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_GOALS_SCORED_AVG5_HOME` | `home_goals_scored_avg5` | GOALS | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_GOALS_CONCEDED_AVG5_HOME` | `home_goals_conceded_avg5` | GOALS | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_GOALS_SCORED_AVG5_AWAY` | `away_goals_scored_avg5` | GOALS | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_GOALS_CONCEDED_AVG5_AWAY` | `away_goals_conceded_avg5` | GOALS | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_GOALS_SCORED_AVG5_DIFF` | `goals_scored_avg5_difference` | GOALS | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_GOALS_CONCEDED_AVG5_DIFF` | `goals_conceded_avg5_difference` | GOALS | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_REST_DAYS_HOME` | `home_rest_days` | REST_CONGESTION | 238,227 | 610 | 0 | 99.7% |
| `FEAT_REST_DAYS_AWAY` | `away_rest_days` | REST_CONGESTION | 238,226 | 611 | 0 | 99.7% |
| `FEAT_REST_DAYS_DIFF` | `rest_days_difference` | REST_CONGESTION | 237,911 | 926 | 0 | 99.6% |
| `FEAT_CONGESTION_7_HOME` | `home_matches_last_7_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_14_HOME` | `home_matches_last_14_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_30_HOME` | `home_matches_last_30_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_7_AWAY` | `away_matches_last_7_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_14_AWAY` | `away_matches_last_14_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_30_AWAY` | `away_matches_last_30_days` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_7_DIFF` | `matches_last_7_days_difference` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_14_DIFF` | `matches_last_14_days_difference` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_CONGESTION_30_DIFF` | `matches_last_30_days_difference` | REST_CONGESTION | 238,837 | 0 | 0 | 100.0% |
| `FEAT_SHOTS_AVG5_HOME` | `home_shots_avg5` | SHOTS | 140,242 | 3,020 | 95,575 | 58.7% |
| `FEAT_SHOTS_TARGET_AVG5_HOME` | `home_shots_on_target_avg5` | SHOTS | 140,242 | 3,020 | 95,575 | 58.7% |
| `FEAT_SHOTS_AVG5_AWAY` | `away_shots_avg5` | SHOTS | 140,240 | 3,013 | 95,584 | 58.7% |
| `FEAT_SHOTS_TARGET_AVG5_AWAY` | `away_shots_on_target_avg5` | SHOTS | 140,240 | 3,013 | 95,584 | 58.7% |
| `FEAT_SHOTS_AVG5_DIFF` | `shots_avg5_difference` | SHOTS | 134,317 | 4,435 | 100,085 | 56.2% |
| `FEAT_SHOTS_TARGET_AVG5_DIFF` | `shots_on_target_avg5_difference` | SHOTS | 134,317 | 4,435 | 100,085 | 56.2% |
| `FEAT_CORNERS_AVG5_HOME` | `home_corners_avg5` | CORNERS | 139,730 | 3,020 | 96,087 | 58.5% |
| `FEAT_CORNERS_AVG5_AWAY` | `away_corners_avg5` | CORNERS | 139,731 | 3,013 | 96,093 | 58.5% |
| `FEAT_CORNERS_AVG5_DIFF` | `corners_avg5_difference` | CORNERS | 133,889 | 4,435 | 100,513 | 56.1% |
| `FEAT_FOULS_AVG5_HOME` | `home_fouls_avg5` | FOULS | 139,149 | 3,020 | 96,668 | 58.3% |
| `FEAT_FOULS_AVG5_AWAY` | `away_fouls_avg5` | FOULS | 139,149 | 3,013 | 96,675 | 58.3% |
| `FEAT_FOULS_AVG5_DIFF` | `fouls_avg5_difference` | FOULS | 133,404 | 4,435 | 100,998 | 55.9% |
| `FEAT_YELLOW_CARDS_AVG5_HOME` | `home_yellow_cards_avg5` | CARDS | 141,523 | 3,020 | 94,294 | 59.3% |
| `FEAT_YELLOW_CARDS_AVG5_AWAY` | `away_yellow_cards_avg5` | CARDS | 141,521 | 3,013 | 94,303 | 59.2% |
| `FEAT_YELLOW_CARDS_AVG5_DIFF` | `yellow_cards_avg5_difference` | CARDS | 136,485 | 4,435 | 97,917 | 57.1% |
| `FEAT_RED_CARDS_AVG5_HOME` | `home_red_cards_avg5` | CARDS | 141,523 | 3,020 | 94,294 | 59.3% |
| `FEAT_RED_CARDS_AVG5_AWAY` | `away_red_cards_avg5` | CARDS | 141,521 | 3,013 | 94,303 | 59.2% |
| `FEAT_RED_CARDS_AVG5_DIFF` | `red_cards_avg5_difference` | CARDS | 136,485 | 4,435 | 97,917 | 57.1% |
| `FEAT_CLEAN_SHEET_RATE5_HOME` | `home_clean_sheet_rate5` | CLEAN_SHEET | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_CLEAN_SHEET_RATE5_AWAY` | `away_clean_sheet_rate5` | CLEAN_SHEET | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_CLEAN_SHEET_RATE5_DIFF` | `clean_sheet_rate5_difference` | CLEAN_SHEET | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_FAILED_TO_SCORE_RATE5_HOME` | `home_failed_to_score_rate5` | FAILED_TO_SCORE | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_FAILED_TO_SCORE_RATE5_AWAY` | `away_failed_to_score_rate5` | FAILED_TO_SCORE | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_FAILED_TO_SCORE_RATE5_DIFF` | `failed_to_score_rate5_difference` | FAILED_TO_SCORE | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_BTTS_RATE5_HOME` | `home_historical_btts_rate5` | HISTORICAL_BTTS | 235,817 | 3,020 | 0 | 98.7% |
| `FEAT_BTTS_RATE5_AWAY` | `away_historical_btts_rate5` | HISTORICAL_BTTS | 235,824 | 3,013 | 0 | 98.7% |
| `FEAT_BTTS_RATE5_DIFF` | `historical_btts_rate5_difference` | HISTORICAL_BTTS | 234,402 | 4,435 | 0 | 98.1% |
| `FEAT_H2H_HOME_WINS` | `h2h_home_wins` | HEAD_TO_HEAD | 216,101 | 22,736 | 0 | 90.5% |
| `FEAT_ELO_PRE_MATCH_HOME` | `home_pre_match_elo` | ELO | 160,383 | 0 | 78,454 | 67.2% |
| `FEAT_ELO_PRE_MATCH_AWAY` | `away_pre_match_elo` | ELO | 160,345 | 0 | 78,492 | 67.1% |
| `FEAT_ELO_PRE_MATCH_DIFF` | `pre_match_elo_difference` | ELO | 145,812 | 0 | 93,025 | 61.0% |

---

## Missingness Policy Analysis
1. **Explicit Missingness Classification**:
   - `INSUFFICIENT_HISTORY`: The team lacks the minimum required historical matches prior to the target match $T$.
   - `MISSING_SOURCE_DATA`: The team has sufficient match history, but the underlying source dataset lacks specific statistics (e.g. corners, fouls, cards, shots) for those matches.
2. **Zero Imputation / Fabrication Prohibition**:
   - No missing source statistics or insufficient history states are silently filled with mean, median, zero, synthetic xG, or bookmaker odds.
