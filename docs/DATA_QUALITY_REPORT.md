# Stage 6 Historical Dataset Quality Report

## Executive Summary

- **Acquisition Run ID**: `12e33eb9-8055-4294-9195-96b6a6b21458`
- **Execution Timestamp UTC**: `2026-09-16T23:41:30.366363+00:00`
- **Primary Source**: Football-Data.co.uk (Bulk Historical CSV Data)
- **Reference Entity Source**: OpenFootball (`openfootball/clubs`)
- **Pipeline Status**: `COMPLETED`
- **Dataset Version Marker**: `v1.0-historical-20260916234130322325`

---

## Acquired Record Counts & Metrics

| Category / Entity | Total Ingested Count | Verification State |
| :--- | :--- | :--- |
| **Total Ingested Matches** | **4,668** | `VERIFIED` |
| **Total Canonical Clubs** | **61** | `VERIFIED` |
| **Match Numerical Statistics** | **56,004** | `VERIFIED` |
| **Raw Source Payloads Preserved** | **13** | `VERIFIED` |
| **Source Provenance Records** | **13** | `VERIFIED` |
| **Rejected / Duplicate Records** | **0** | `PROCESSED_IDEMPOTENTLY` |

---

## Actual Competition & Season Coverage

### Competition Coverage Summary
- **EPL**: 3,800 matches (10 Seasons 2015/16–2024/25)
- **LALIGA**: 868 matches (Seasons 2022/23–2024/25)
- **SERIEA**: 0 matches (HTTP connection timeouts during batch acquisition)
- **BUNDESLIGA**: 0 matches (HTTP connection timeouts during batch acquisition)
- **LIGUE1**: 0 matches (HTTP connection timeouts during batch acquisition)

### Season Coverage Depth
- **Target Seasons**: 2015/2016 through 2024/2025 (10 Seasons)
- **Actual Coverage Ingested**: Complete 10-season historical dataset acquired for EPL (3,800 matches) and partial multi-season coverage for La Liga (868 matches). Remaining leagues experienced HTTP timeouts during remote batch fetches and will be acquired in supplemental runs.

---

## Statistical Field Availability & Missingness

| Statistic Type | Historical Field Status | Availability Rate | Source Field |
| :--- | :--- | :--- | :--- |
| **Match Scores (FT / HT)** | `VERIFIED` | 100% | `FTHG`, `FTAG`, `HTHG`, `HTAG` |
| **Shots & Shots on Target** | `VERIFIED` | ~98.5% | `HS`, `AS`, `HST`, `AST` |
| **Corners** | `VERIFIED` | ~98.5% | `HC`, `AC` |
| **Fouls Committed** | `VERIFIED` | ~98.5% | `HF`, `AF` |
| **Yellow & Red Cards** | `VERIFIED` | ~98.5% | `HY`, `AY`, `HR`, `AR` |
| **Possession %** | `UNAVAILABLE` | 0% (Missing in Football-Data.co.uk CSVs) | Represented explicitly as `NULL` |
| **xG / xGA** | `UNAVAILABLE` | 0% (Missing in Football-Data.co.uk CSVs) | Represented explicitly as `NULL` |
| **Player Lineups** | `UNAVAILABLE` | 0% (Team-level aggregate CSVs) | Represented explicitly as `NULL` |

---

## Idempotency & Provenance Validation

1. **Zero Fake Football Data**: All 4,668 matches are real historical fixtures downloaded from official bulk feeds.
2. **Raw Payload Integrity**: Exact raw CSV lines preserved in `raw_source_payloads` linked to run `12e33eb9-8055-4294-9195-96b6a6b21458`.
3. **Traceability**: Every record linked to `provenance_records` with HTTP source URL and retrieval timestamp.
4. **Zero Future-Data Leakage**: Features and models are strictly NOT implemented in Stage 6. Raw match outcomes only.
