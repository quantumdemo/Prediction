# Data Source Hierarchy & Fallback Strategy (Stage 5)

## 1. SOURCE HIERARCHY ROLES

| Hierarchy Tier | Source Name | Role & Scope | Primary Rationale |
| :--- | :--- | :--- | :--- |
| **PRIMARY HISTORICAL** | **Football-Data.co.uk** | Bulk historical match results, goals, shots, corners, cards, fouls (25+ seasons). | 100% free open dataset, no API rate limits, deep historical consistency across top European leagues. |
| **PRIMARY LIVE / FIXTURE** | **API-Football (API-Sports)** | Live fixtures, starting lineups, player ratings, xG, injury updates, current team news. | High reliability (99.9% SLA), global league coverage (1000+), REST API integration with real-time updates. |
| **SECONDARY BACKUP** | **Football-Data.org** | Fallback fixture verification, backup score verification, league standings. | Independent European score verification backing up API-Football. |
| **RESEARCH / xG BASELINE** | **StatsBomb Open Data** | Shot-level xG model evaluation, offline probability calibration benchmarking. | Gold-standard event data for offline calibration validation (non-commercial evaluation tier). |
| **ENTITY / REFERENCE** | **OpenFootball (`clubs`)** | Canonical club names, short names, city references, stadium metadata, country mappings. | Public domain (CC0), canonical name standardization, alias resolution baseline. |
| **OFFICIAL VERIFICATION** | **Official League Feeds** | Official kickoff time verification, match postponement/cancellation confirmations. | Authoritative single source of truth for fixture schedule verification. |

---

## 2. FALLBACK & ABSTENTION LOGIC

```
                           [MATCH QUERY REQUEST]
                                     │
                                     ▼
                   [FETCH FROM PRIMARY SOURCE: API-Football]
                                     │
                   ┌─────────────────┴─────────────────┐
                   ▼                                   ▼
          (Successful Return)                   (API Failure / Timeout)
                   │                                   │
                   ▼                                   ▼
        [VERIFY MATCH DATA]                 [TRIGGER SECONDARY FALLBACK]
                   │                        (Football-Data.org / FD UK)
         ┌─────────┴─────────┐                         │
         ▼                   ▼                         ▼
   (Data Verified)   (Data Missing/Conflict)    [DATA RETRIEVED?]
         │                   │                   ┌─────┴─────┐
         ▼                   ▼                   ▼           ▼
  [PROCEED TO          [ISSUE NO BET /         (Yes)       (No)
   PIPELINE]            INSUFFICIENT            │           │
                        EVIDENCE]               ▼           ▼
                                            [MARK AS     [ISSUE
                                            SECONDARY]   NO BET]
```

## Fallback Rules

1. **Fixture Schedule Defect**: If primary live source (API-Football) fails or times out, query secondary backup (Football-Data.org). If both fail, flag fixture status as `UNVERIFIED` and return `NO BET`.
2. **Missing Historical Statistics**: If a match is missing shots or corners in Football-Data.co.uk, attempt enrichment from API-Football. If still missing, mark field as `NULL` (never substitute fake averages).
3. **Contradictory Match Results**: If primary and secondary sources report conflicting scores or red cards, set match `validation_state` to `CONFLICTING`. If unresolvable prior to prediction cutoff, trigger `NO BET`.
