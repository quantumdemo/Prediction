# Stage 7 — Data Quality Report

## Candidate Historical Dataset Processing Overview

* **Source Dataset**: `xgabora/club-football-match-data`
* **Cleaning Pipeline Version**: `v1.0.0-stage7`
* **Dataset Artifact Label**: `STAGE7_VALIDATED_HISTORICAL_DATASET_v1.0.0`

### Measured Quality Indicators

#### Match Records (`Matches.csv`)
* **Total Raw Source Rows**: **238,858**
* **Accepted Valid Records**: **238,837** (99.991%)
* **Accepted with Warnings**: **0**
* **Quarantined Records**: **21** (0.009%) — all due to source `shots_on_target > total_shots` anomalies.
* **Duplicate Match Fixture Keys**: **0**
* **Exact Duplicates**: **0**
* **Suspicious Duplicates**: **0**
* **Earliest Match Date**: **2000-07-28**
* **Latest Match Date**: **2026-09-03**
* **Distinct Raw Club Names Requiring Stage 8 Review**: **1,421**

#### Elo Rating Snapshots (`EloRatings.csv`)
* **Total Raw Source Rows**: **273,972**
* **Accepted Elo Records**: **273,972** (100.0%)
* **Verified Historical Elo Records (<= 2025-06-01)**: **245,033**
* **Provisional Estimate Elo Records (> 2025-06-01)**: **28,939**
* **Quarantined Elo Records**: **0**
* **Earliest Elo Snapshot Date**: **2000-07-01**
* **Latest Elo Snapshot Date**: **2026-09-01**

### Restricted Field Isolation Summary
* **Odds Fields**: Classified as `REJECTED_ODDS` (100% isolated from ML feature pipelines).
* **Pre-calculated Form & Ratings**: Classified as `REQUIRES_RECALCULATION` (isolated for Stage 9 recomputation).
* **Synthetic xG**: Classified as `REJECTED_UNVERIFIED` (isolated).
* **Cluster Labels / Probabilities**: Classified as `REJECTED_LEAKAGE` (isolated).
