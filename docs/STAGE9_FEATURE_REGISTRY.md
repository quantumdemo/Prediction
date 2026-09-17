# Stage 9 — Feature Registry

## Registered Feature Definitions

| Feature ID | Feature Name | Family | Window | Minimum History | Missing Data Policy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FEAT_FORM3_HOME` | `home_recalculated_form3` | `FORM` | `ROLLING_3` | 3 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_HOME` | `home_recalculated_form5` | `FORM` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM3_AWAY` | `away_recalculated_form3` | `FORM` | `ROLLING_3` | 3 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_AWAY` | `away_recalculated_form5` | `FORM` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM3_DIFF` | `form3_difference` | `FORM` | `ROLLING_3` | 3 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_FORM5_DIFF` | `form5_difference` | `FORM` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_SCORED_AVG5_HOME` | `home_goals_scored_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_CONCEDED_AVG5_HOME` | `home_goals_conceded_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_SCORED_AVG5_AWAY` | `away_goals_scored_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_GOALS_CONCEDED_AVG5_AWAY` | `away_goals_conceded_avg5` | `GOALS` | `ROLLING_5` | 5 matches | `INSUFFICIENT_HISTORY` |
| `FEAT_REST_DAYS_HOME` | `home_rest_days` | `REST_CONGESTION` | `RECENT_MATCH` | 1 match | `INSUFFICIENT_HISTORY` |
| `FEAT_REST_DAYS_AWAY` | `away_rest_days` | `REST_CONGESTION` | `RECENT_MATCH` | 1 match | `INSUFFICIENT_HISTORY` |
| `FEAT_H2H_HOME_WINS` | `h2h_home_wins` | `HEAD_TO_HEAD` | `ALL_TIME` | 1 match | `INSUFFICIENT_HISTORY` |
| `FEAT_ELO_PRE_MATCH_HOME` | `home_pre_match_elo` | `ELO` | `RECENT_MATCH` | 1 snapshot | `MISSING` |
| `FEAT_ELO_PRE_MATCH_AWAY` | `away_pre_match_elo` | `ELO` | `RECENT_MATCH` | 1 snapshot | `MISSING` |
| `FEAT_ELO_PRE_MATCH_DIFF` | `pre_match_elo_difference` | `ELO` | `RECENT_MATCH` | 1 snapshot | `MISSING` |
