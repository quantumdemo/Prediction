# FOOTBALL DATA SOURCES & PROVIDER RESEARCH
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. PROVIDER EVALUATION SUMMARY

*Research Date: September 2026*

| Provider Name | Status | Coverage & Depth | Data Categories | API Limits & Costs | Licensing & Terms |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Football-Data.co.uk** | **VERIFIED (Primary Historical)** | Major European leagues (EPL, La Liga, Serie A, Bundesliga, Ligue 1) since 1993. | Results, goals, half-time goals, shots, SOT, fouls, corners, cards, betting odds history. CSV downloads. | **FREE / Open Access**. No API rate limit (bulk CSV). | Non-commercial & research use permitted. Redistribution terms require citation. |
| **API-Football (RapidAPI)** | **VERIFIED (Primary Live/Fixture)** | 1000+ leagues worldwide. Historical results & live updates. | Fixtures, live scores, lineups, player stats, injuries, team stats, odds. | Free Tier: 100 requests/day. Paid: $19–$39/mo for 7,500–150,000 req/mo. | Commercial plans available. API key required. |
| **Football-Data.org** | **VERIFIED (Secondary Backup)** | Major European competitions & international tournaments. | Fixtures, standings, team rosters, match results. | Free Tier: 10 requests/min. Paid: €15–€49/mo. | Standard commercial & non-commercial API tiers. |
| **StatsBomb Open Data** | **VERIFIED (Research/xG Baseline)** | Selected historical tournaments (World Cups, Euros, Champions League finals). | Event-level data (passes, shots, xG, pressure, freeze frames). | GitHub repository clone / Direct download. | Non-commercial evaluation license only. Explicit StatsBomb attribution required. |

---

### 2. DATA CATEGORY AVAILABILITY MATRIX

| Variable Category | Football-Data.co.uk | API-Football | Football-Data.org | StatsBomb Open Data |
| :--- | :--- | :--- | :--- | :--- |
| Match Results (FT/HT) | YES | YES | YES | YES |
| Match Shots & Shots on Target | YES (Top 5) | YES | Partial | YES |
| Corners & Cards | YES (Top 5) | YES | Partial | YES |
| xG / xGA Statistics | NO | YES (Recent seasons) | NO | YES (Selected tournaments) |
| Starting Lineups & Substitutions | NO | YES | YES | YES |
| Player Injury / Suspension Status | NO | YES | NO | NO |
| Historical Depth (Leagues) | > 25 Seasons | > 10 Seasons | > 10 Seasons | Selected Tournaments |

---

### 3. LEGAL & LICENSING COMPLIANCE MANDATES
1. **No Scraping Off Commercial Terms**: The platform MUST NOT scrape proprietary commercial sports sites in violation of `robots.txt` or terms of service.
2. **Provider Attribution**: Credit must be maintained in data provenance records (`source_id`, `provider_name`).
3. **Third-Party Odds Constraint**: Historical betting odds provided in datasets (e.g., Football-Data.co.uk) are restricted to post-hoc model evaluation or market mapping benchmark displays. They MUST NOT be fed into ML models as predictive features.
