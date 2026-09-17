# Stage 9 — Feature Quality Report

## Feature Generation Summary
* **Input Dataset Version**: `STAGE8_ENTITY_MAPPING_v1.0.0`
* **Output Feature Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
* **Total Canonical Fixtures Processed**: **238,837**
* **Total Feature Vectors Created**: **238,837**
* **Registered Feature Definitions**: **16**
* **Stage 7 Quarantined Matches Excluded**: **21 / 21 (100.0%)**

## Missingness & Availability Analysis
* **First Matches (No Prior History)**: Explicitly assigned `INSUFFICIENT_HISTORY` (None) without fake default zeros.
* **Established Teams (>= 5 Matches)**: 100.0% feature availability across Form3, Form5, Goals, Rest Days, and H2H metrics.
* **Feature Stability Test**: Sequential reruns over immutable Stage 8 data produce 100.0% identical feature vectors and checksums.
