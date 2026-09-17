# Data Acquisition Runbook (Stage 6)

## Execution Command

To run the historical data acquisition pipeline and populate `football_ai_stage6.db`:

```bash
python3 scripts/ingest_historical_data.py
```

## Expected Output

1. Creates/connects to `football_ai_stage6.db`.
2. Registers sources in `sources` table.
3. Ingests reference entities and bulk CSV match data.
4. Stores raw CSV payloads in `raw_source_payloads`.
5. Logs provenance records in `provenance_records`.
6. Creates dataset snapshot version in `dataset_versions`.
7. Generates data quality report at `docs/DATA_QUALITY_REPORT.md`.
