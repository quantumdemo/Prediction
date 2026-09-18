# Stage 9 — Feature Dataset Documentation

## Dataset Specification: `STAGE9_FEATURE_DATASET_v1.0.0`

### Overview
`STAGE9_FEATURE_DATASET_v1.0.0` is the production-ready pre-match feature dataset generated from the Stage 8 canonical historical entity mappings (`STAGE8_ENTITY_MAPPING_v1.0.0`).

### Dataset Summary
- **Total Feature Vectors**: **238,837**
- **Feature Count**: **55 numerical features**
- **Target Variables**: `full_time_home_goals`, `full_time_away_goals`, `full_time_result`, `total_goals`, `btts`
- **Quarantined Matches Excluded**: **21 Stage 7 quarantined records**
- **Zero Future-Data Leakage**: Guaranteed via strict chronological pre-match cutoff ($T_{match} < T_{target}$).

### Schema Structure
Each record in the dataset is represented as a `MatchFeatureVector`:
```json
{
  "fixture_id": "uuid",
  "match_date": "YYYY-MM-DD",
  "competition_id": "uuid",
  "season_id": "uuid",
  "home_club_id": "uuid",
  "away_club_id": "uuid",
  "features": {
    "FEAT_FORM3_HOME": 6.0,
    "FEAT_CONGESTION_7_HOME": 1.0,
    ...
  },
  "feature_availability": {
    "FEAT_FORM3_HOME": "PRESENT",
    "FEAT_CORNERS_AVG5_HOME": "MISSING_SOURCE_DATA",
    ...
  },
  "targets": {
    "full_time_home_goals": 2,
    "full_time_away_goals": 1,
    "full_time_result": "H",
    "total_goals": 3,
    "btts": true
  },
  "feature_version": "STAGE9_FEATURE_DATASET_v1.0.0"
}
```

### Versioning Artifact
Metadata artifact exported to `stage9_feature_dataset_version.json` containing:
- Feature dataset version
- Input entity mapping version
- Created timestamp UTC
- Total fixtures processed
- Feature list and count
- Feature-level coverage report
- Leakage safeguards checklist
