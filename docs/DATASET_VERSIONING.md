# Dataset Snapshot Versioning (Stage 6)

## Overview

Reproducible dataset versioning allows machine learning models and feature extraction pipelines to reference fixed, immutable dataset snapshots.

## Dataset Version Schema

Each ingestion run produces a `dataset_versions` record:
- `id`: UUID Primary Key
- `version_label`: Semantic version tag (e.g., `v1.0-historical-20260916234004384640`)
- `cutoff_timestamp_utc`: Immutable UTC cutoff timestamp
- `record_count`: Number of verified match records in dataset snapshot
- `notes`: Metadata describing ingestion run and source scope

## Zero Future-Data Leakage Rule

Downstream feature extraction engines (Stage 9+) query matches where `scheduled_kickoff_utc <= dataset_versions.cutoff_timestamp_utc`.
