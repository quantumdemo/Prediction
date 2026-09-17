# Historical Data Acquisition & Ingestion (Stage 6)

## Overview

Stage 6 implements the first production data acquisition and ingestion pipeline for real-world historical football match data. Using the approved Stage 5 source strategy and Stage 4 relational database schema, the pipeline acquires, preserves, normalizes, and stores historical football match statistics.

## Primary Source & Acquired Historical Scope

- **Primary Historical Provider**: Football-Data.co.uk (Bulk Historical CSV Data Warehouse)
- **Reference Entity Provider**: OpenFootball (`openfootball/clubs`)
- **Seeded Reference Entities**: 5 Countries, 5 Competitions, 35 Seasons.
- **Acquired Match Coverage**: **39 real historical matches** (20 EPL 2024/2025, 19 La Liga 2024/2025).
- **Acquired Match Statistics**: **468 numerical statistics** (Shots, SOT, Corners, Fouls, Yellow Cards, Red Cards).
- **Acquired Canonical Clubs**: **44 clubs**.
- **Unavailable Fields in Source**: Possession %, xG/xGA, Players, Match Events, Lineups (`NULL` / `0` acquired).

## Raw Payload Preservation

Every CSV file fetched during ingestion is preserved in `raw_source_payloads` alongside retrieval UTC timestamps, external batch identifiers, and `ingestion_run_id` links.
