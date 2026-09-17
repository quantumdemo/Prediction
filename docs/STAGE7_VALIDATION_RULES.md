# Stage 7 — Validation Rules

## Validation Checks Matrix

| Rule Code | Target Fields | Condition | Action on Failure |
| :--- | :--- | :--- | :--- |
| `DATE_INVALID_CALENDAR` | `MatchDate` | Valid calendar date YYYY-MM-DD | QUARANTINE |
| `FT_RESULT_INVALID` | `FTResult` | Must be 'H', 'D', or 'A' | QUARANTINE |
| `FT_RESULT_SCORE_MISMATCH` | `FTHome`, `FTAway`, `FTResult` | `FTHome > FTAway` => 'H', equal => 'D', less => 'A' | QUARANTINE |
| `HT_GOALS_EXCEED_FT` | `HTHome`, `HTAway`, `FTHome`, `FTAway` | Half-time goals cannot exceed full-time goals | QUARANTINE |
| `HOME_SHOTS_ON_TARGET_EXCEEDS_SHOTS` | `HomeTarget`, `HomeShots` | Shots on target <= total shots | QUARANTINE |
| `AWAY_SHOTS_ON_TARGET_EXCEEDS_SHOTS` | `AwayTarget`, `AwayShots` | Shots on target <= total shots | QUARANTINE |
| `STATISTIC_NEGATIVE` | Any numeric stat | Must be >= 0 | QUARANTINE |
| `SAME_HOME_AWAY_CLUB` | `HomeTeam`, `AwayTeam` | Normalized home team != normalized away team | QUARANTINE |
| `DUPLICATE_FIXTURE` | Match key | Division + MatchDate + NormHome + NormAway unique | QUARANTINE |
