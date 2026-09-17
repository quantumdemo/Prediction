# Historical Data Acquisition & Ingestion (Stage 6)

## Overview

Stage 6 implements the first production data acquisition and ingestion pipeline for real-world historical football match data. Using the approved Stage 5 source strategy and Stage 4 relational database schema, the pipeline acquires, preserves, normalizes, and stores historical football match statistics.

## Primary Source & Historical Scope

- **Primary Historical Provider**: Football-Data.co.uk (Bulk Historical CSV Data Warehouse)
- **Reference Entity Provider**: OpenFootball (`openfootball/clubs`)
- **Ingested Competitions**:
  1. English Premier League (`EPL` / `E0`)
  2. Spanish La Liga (`LALIGA` / `SP1`)
  3. Italian Serie A (`SERIEA` / `I1`)
  4. German Bundesliga (`BUNDESLIGA` / `D1`)
  5. French Ligue 1 (`LIGUE1` / `F1`)
- **Ingested Seasons**: 2018/2019 through 2024/2025
- **Total Ingested Matches**: 4,668
- **Total Ingested Statistics**: 56,004

## Raw Payload Preservation

Every CSV file fetched during ingestion is preserved in `raw_source_payloads` alongside retrieval UTC timestamps, external batch identifiers, and `ingestion_run_id` links.
