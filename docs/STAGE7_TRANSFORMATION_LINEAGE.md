# Stage 7 — Transformation Lineage Specification

## Transformation Lineage Diagram

```
[RAW SOURCE DATA]
  │
  ├── Matches.csv (238,858 rows) SHA-256: d724472b...
  └── EloRatings.csv (273,972 rows) SHA-256: e9f6020b...
  │
  ▼
[STAGE 7 STREAMING INGESTION & PROVENANCE INJECTION]
  │ (Attach Source Provenance: file, row_index, SHA-256, UTC timestamp)
  ▼
[SCHEMA & STRING NORMALIZATION]
  │ (Map Canonical Fields, Trim/Collapse Club Names, ISO Dates/Times)
  ▼
[VALIDATION & CROSS-FIELD CHECKS]
  │ (Score/Result Check, Shots-on-Target Check, Temporal Boundaries)
  ▼
[FIELD CLASSIFICATION & RESTRICTED FIELD ISOLATION]
  │ ├── Odds -> REJECTED_ODDS
  │ ├── Form/Rating -> REQUIRES_RECALCULATION
  │ ├── Synthetic xG -> REJECTED_UNVERIFIED
  │ ├── Clusters -> REJECTED_LEAKAGE
  │ └── Post-June 2025 Elo -> PROVISIONAL_ESTIMATE
  ▼
[DUPLICATE DETECTION & QUARANTINE ROUTING]
  │ ├── Quarantined Matches: 21 records
  │ └── Quarantined Elo: 0 records
  ▼
[STAGE7_VALIDATED_HISTORICAL_DATASET_v1.0.0]
```
