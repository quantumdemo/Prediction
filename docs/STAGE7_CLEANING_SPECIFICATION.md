# Stage 7 — Data Cleaning Specification

## Executive Overview
This document specifies the exact cleaning, transformation, and normalization rules applied during **Stage 7 — Data Cleaning, Normalization & Validation**.

The pipeline ingests candidate historical records from `Matches.csv` (238,858 records) and `EloRatings.csv` (273,972 records) preserved from Stage 6A.

## Cleaning Directives & Principles
1. **Raw Data Immutability**: Source raw files in `candidate_data/` remain untouched. Cryptographic SHA-256 hashes (`d724472b...` for Matches, `e9f6020b...` for Elo) are verified prior to ingestion.
2. **Zero Invalidation / Zero Fabrication**: Cleaning never invents missing information or replaces missing statistics with default zeros.
3. **Traceability**: Every record preserves source dataset name, source file, row index, SHA-256 checksum, pipeline version (`v1.0.0-stage7`), and UTC transformation timestamp.
4. **Isolation of Restricted Fields**: Odds fields (`REJECTED_ODDS`), pre-calculated form (`REQUIRES_RECALCULATION`), synthetic xG (`REJECTED_UNVERIFIED`), and cluster labels (`REJECTED_LEAKAGE`) are isolated from production ML feature sets.

## Ingestion & Pipeline Pipeline Architecture
* Ingestion engine: `services/ml/app/data/stage7/ingestion.py`
* Field mappings: `services/ml/app/data/stage7/mappings.py`
* Cleaning & validation engine: `services/ml/app/data/stage7/pipeline.py`
* Dataset versioning exporter: `services/ml/app/data/stage7/versioning.py`
