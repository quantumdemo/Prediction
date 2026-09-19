# STAGE 14 — CURRENT-MATCH WEB RESEARCH ENGINE REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Code Identifier**: `STAGE14_WEB_RESEARCH_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 14 implements the platform's Current-Match Web Research Engine. Operating strictly on verified upcoming fixtures, the engine gathers, parses, structures, and classifies current pre-match information across 12 fact categories (Recent Form, League Position, Injuries, Suspensions, Expected/Confirmed Lineups, Tactical Changes, Manager Changes, Rest & Congestion, Travel Context, Head-to-Head, and Team News).

Every research item retains full source provenance (Source Name, URL, UTC Retrieval Timestamp, Publication Timestamp). Research items are explicitly classified into research states (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`, `UNAVAILABLE`). The engine detects opposing or contradictory claims across sources without silently inventing facts or picking a winner. Synthetic or fabricated data is strictly prohibited; missing information is explicitly marked as `UNAVAILABLE`. Crucially, the web research engine generates zero numerical prediction probabilities, preserving strict architectural isolation from downstream model stages.

---

## 2. Pipeline Architecture & Data Flow

```
[Target Fixture Parameters]
            │
            ▼
[1. Fixture Identity Verifier] ──► Resolves Team & Competition Aliases
            │                     (e.g., "Man Utd" -> CLUB_ENG_MANCHESTER_UNITED)
            ▼
[2. Verified Fixture Identity]
            │
            ▼
[3. Web Research Processor] ──► Gathers Facts Across 12 Categories
            │
            ▼
[4. Provenance Validator] ──► Validates Source URL + UTC Timestamp
            │
            ▼
[5. Contradiction Detector] ──► Flags Opposing Claims as CONFLICTING
            │
            ▼
[6. Structured Research Report] ──► Output ResearchReport JSON
```

---

## 3. Fact Categories & Research States

### 3.1 Supported Fact Categories
1. `RECENT_FORM`: Recent team results and performances.
2. `LEAGUE_POSITION`: Current standings and point differentials.
3. `INJURIES`: Player injury reports and medical updates.
4. `SUSPENSIONS`: Red card and yellow card accumulation bans.
5. `EXPECTED_LINEUPS`: Media and tactical predicted starting XI.
6. `CONFIRMED_LINEUPS`: Officially announced matchday lineups.
7. `TACTICAL_CHANGES`: Formation shifts and system adjustments.
8. `MANAGER_CHANGES`: Appointments, sackings, or interim managers.
9. `REST_CONGESTION`: Days between fixtures and travel fatigue.
10. `TRAVEL_CONTEXT`: Away match logistics and distance traveled.
11. `HEAD_TO_HEAD`: Historical matchup records between the two clubs.
12. `TEAM_NEWS`: Press conference quotes and general squad updates.

### 3.2 Explicit Research States
- `VERIFIED`: Confirmed by official club announcements or multiple reliable tier-1 sports news sources.
- `LIKELY`: Reported by credible sports journalists or reputable news outlets.
- `UNCERTAIN`: Single-source rumor or unconfirmed squad news.
- `CONFLICTING`: Opposing or contradictory information detected across multiple sources.
- `UNAVAILABLE`: Information for the specified category is absent in pre-match research.

---

## 4. Contradiction Handling & Provenance Rules

1. **Source Provenance Integrity**: Every research item must specify `source_name`, a valid `source_url` starting with `http://` or `https://`, and a `retrieval_timestamp_utc`.
2. **Explicit Contradiction Detection**: When source A reports a player is OUT injured while source B reports the player is FIT/available, both items are tagged as `ResearchState.CONFLICTING` and logged in `conflicting_items` with explicit `contradiction_details`. The engine NEVER invents or selects a claim.
3. **No Synthetic Data**: Missing information is recorded in `unavailable_categories`. Default or fabricated values are strictly rejected.
4. **Architectural Isolation**: Research items contain zero outcome win/loss probabilities, odds, market lines, or Kelly stakes.

---

## 5. Testing & Verification

Unit test suite (`services/ml/tests/test_stage14_web_research.py`) verifies:
- Canonical alias resolution for teams and competitions.
- Fixture identity verification and validation errors.
- Provenance URL and timestamp enforcement.
- Research state classification and contradiction detection.
- Rejection of invalid URLs and empty claims.
- Absence of numerical prediction probabilities.

---

## 6. Stage Boundary & Limitations

1. **No Market Mapping or Odds**: Odds ingestion, bookmaker mapping, and line movement belong to Stage 17.
2. **No Risk / Value / NO-BET Logic**: Value calculation, Kelly sizing, and abstention logic belong strictly to Stage 18.
3. **No Automated Prediction Reporting**: Final prediction generation belongs to Stage 20.
