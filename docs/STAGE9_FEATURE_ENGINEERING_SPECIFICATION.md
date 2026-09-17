# Stage 9 — Feature Engineering Specification

## Executive Overview
This document specifies the exact feature engineering principles, mathematical calculations, and zero future-data leakage safeguards applied during **Stage 9 — Feature Engineering Engine**.

The engine transforms Stage 8 canonical historical entities and fixtures (`STAGE8_ENTITY_MAPPING_v1.0.0`) into prediction-time-safe numerical features (`STAGE9_FEATURE_DATASET_v1.0.0`).

## Core Directives & Zero Future-Data Leakage
1. **Strict Pre-Match Cutoff**: For any historical match $T$, feature calculations use strictly matches $< T$. Match $T$'s own outcome or post-match statistics are 100% excluded.
2. **Explicit Target Separation**: Feature vectors are strictly separated from target variables (`full_time_result`, `full_time_home_goals`, `full_time_away_goals`).
3. **No Unvalidated / Restricted Field Usage**:
   - Odds fields (`REJECTED_ODDS`) are 100% excluded.
   - Synthetic xG (`REJECTED_UNVERIFIED`) is 100% excluded.
   - Cluster labels (`REJECTED_LEAKAGE`) are 100% excluded.
   - Raw source form (`Form3Home`, `Form5Home`) is 100% excluded and recalculated from canonical match outcomes.
4. **Stage 7 Quarantined Matches Excluded**: All 21 quarantined Stage 7 matches remain excluded from feature calculations.
