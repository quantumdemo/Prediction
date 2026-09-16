# Football Data Source Research & Provider Evaluation (Stage 5)

## Overview

This document presents the formal evaluation of primary, secondary, reference, and specialized football data providers for the Football AI Intelligence & Machine-Learning Platform. Each source has been evaluated based on authoritative provider documentation, historical depth, statistical completeness, legal licensing, update latency, rate limits, and technical integration requirements.

---

## 1. EVALUATED DATA SOURCES

### 1.1 Football-Data.co.uk
- **Verification Status**: `VERIFIED`
- **Source Type**: Open Historical CSV Data Warehouse (Third-Party Aggregator)
- **Official / Third-Party**: Third-Party Aggregator
- **Historical Results**: Complete match results (Full Time FT, Half Time HT) for 25+ seasons across 22 major European leagues.
- **Historical Statistics**: Shots, Shots on Target, Corners, Fouls, Yellow Cards, Red Cards available for top 5 European leagues (EPL, La Liga, Serie A, Bundesliga, Ligue 1) since ~2000.
- **xG / xGA**: `UNAVAILABLE` (xG is not provided in CSV downloads).
- **Lineups & Player Stats**: `UNAVAILABLE` (Team-level aggregate match stats only).
- **Injuries, Suspensions & News**: `UNAVAILABLE`.
- **Historical Depth**: Excellent (>25 seasons, 1993–present).
- **Update Frequency**: Weekly batch downloads during active seasons.
- **Access Method**: Direct HTTP bulk CSV file downloads.
- **Rate Limits & API Constraints**: No API rate limit (file-based HTTP GET).
- **Free Tier / Cost**: 100% Free. Commercial licensing requires provider citation.
- **Licensing & Terms**: Permitted for research and commercial modeling provided citation is preserved. Redistribution of raw files requires attribution.
- **Reliability Assessment**: High for match scores and basic team statistics. Minimal downtime.
- **Data Quality Concerns**: Minor team name spelling inconsistencies across seasons (resolved via Stage 8 Entity Resolution / `club_aliases`).
- **Recommended Role**: **PRIMARY HISTORICAL MATCH STATISTICS SOURCE** (Results, Shots, Corners, Cards).

---

### 1.2 API-Football / API-Sports (RapidAPI)
- **Verification Status**: `VERIFIED`
- **Source Type**: Commercial REST API
- **Official / Third-Party**: Third-Party Commercial Aggregator
- **Historical Results**: Live scores and historical match results for 1000+ leagues globally (>10 seasons).
- **Historical Statistics**: Shots, Shots on Target, Possession, Corners, Cards, Fouls, Offsides, expected goals (xG) available for recent seasons (2020–present).
- **xG / xGA**: `VERIFIED` (Available via `/fixtures/statistics` endpoint for top competitions since 2021).
- **Lineups & Player Stats**: `VERIFIED` (Starting XI, substitutes, formations, player minutes, ratings, passes, tackles).
- **Injuries, Suspensions & News**: `VERIFIED` (Player injury endpoint `/injuries` updated daily).
- **Historical Depth**: Moderate to High (10–15 seasons depending on competition).
- **Update Frequency**: Real-time (WebSocket / 1-minute HTTP polling).
- **Access Method**: RESTful JSON API via RapidAPI / API-Sports Gateway.
- **Rate Limits & API Constraints**: Free tier: 100 requests/day. Paid tiers: 7,500–150,000 requests/month (rate limit 10–30 req/sec).
- **Free Tier / Cost**: Free tier for development; $19–$39/month for production inference pipelines.
- **Licensing & Terms**: Commercial use permitted under paid subscription tiers. API key authentication required.
- **Reliability Assessment**: High uptime (99.9% SLA on paid tiers).
- **Data Quality Concerns**: Occasional rate-limiting on burst queries; requires caching and raw payload preservation (`raw_source_payloads`).
- **Recommended Role**: **PRIMARY LIVE / FIXTURE & CURRENT-MATCH RESEARCH SOURCE** (Fixtures, Lineups, xG, Injuries).

---

### 1.3 Football-Data.org
- **Verification Status**: `VERIFIED`
- **Source Type**: RESTful JSON API
- **Official / Third-Party**: Third-Party Aggregator
- **Historical Results**: Major European competitions and FIFA World Cup (>10 seasons).
- **Historical Statistics**: Match scores, halftime scores, standings, team rosters. Detailed match stats (shots, corners) limited on free tier.
- **xG / xGA**: `UNAVAILABLE`.
- **Lineups & Player Stats**: `LIKELY` (Basic squad rosters and match lineups available on paid tier).
- **Injuries, Suspensions & News**: `UNAVAILABLE`.
- **Historical Depth**: Moderate (10+ seasons).
- **Update Frequency**: Near real-time.
- **Access Method**: REST API with X-Auth-Token header.
- **Rate Limits & API Constraints**: Free tier: 10 requests/minute. Paid tier (€15–€49/mo): 100 requests/minute.
- **Free Tier / Cost**: Free tier available for development; paid tier required for higher rate limits.
- **Licensing & Terms**: Standard API terms of service. Non-commercial and commercial tiers available.
- **Reliability Assessment**: High reliability for European league fixtures and standings.
- **Recommended Role**: **SECONDARY BACKUP SOURCE** (Fixture verification and fallback score provider).

---

### 1.4 StatsBomb Open Data
- **Verification Status**: `VERIFIED`
- **Source Type**: Open-Source GitHub Repository / JSON Event Files
- **Official / Third-Party**: Specialized Analytics Provider
- **Historical Results**: Selected high-profile historical tournaments (World Cups 2018/2022, Euros, Champions League finals, Lionel Messi career dataset, NWSL).
- **Historical Statistics**: High-density event data (3,000+ events per match: shot freeze frames, pass end-locations, xG models, pressure events, defensive actions).
- **xG / xGA**: `VERIFIED` (Industry-standard shot-level xG model outputs).
- **Lineups & Player Stats**: `VERIFIED` (Full starting XI, tactical formations, player event coordinates).
- **Injuries, Suspensions & News**: `UNAVAILABLE`.
- **Historical Depth**: Selective (Complete coverage for specific tournament seasons; not full league seasons).
- **Update Frequency**: Periodic open-source releases.
- **Access Method**: Git repository clone or Python SDK (`statsbombpy`).
- **Rate Limits & API Constraints**: No API rate limit (local JSON files).
- **Free Tier / Cost**: 100% Free under StatsBomb Open Data License.
- **Licensing & Terms**: Strictly **Non-Commercial / Evaluation Use Only**. Explicit StatsBomb attribution mandatory.
- **Reliability Assessment**: Highest data density and accuracy in sports analytics.
- **Recommended Role**: **RESEARCH & xG BASELINE CALIBRATION SOURCE** (Used for offline model benchmarking; not for live commercial inference).

---

### 1.5 OpenFootball (`openfootball/clubs`)
- **Verification Status**: `VERIFIED`
- **Source Type**: Open-Source Public Domain Text Files
- **Official / Third-Party**: Open-Source Community Reference
- **Historical Results**: `UNAVAILABLE` in `clubs` repository (Results exist in separate `world` repositories, but lack detailed match statistics).
- **Historical Statistics**: `UNAVAILABLE`.
- **xG / Lineups / Injuries**: `UNAVAILABLE`.
- **Club & Stadium References**: `VERIFIED` (Canonical club names, short codes, cities, stadium names, country relationships).
- **Historical Depth**: N/A (Static reference datasets).
- **Access Method**: Plain-text files in GitHub repository.
- **Licensing & Terms**: Public Domain (CC0 1.0 Universal).
- **Reliability Assessment**: High for country and club alias mapping.
- **Recommended Role**: **REFERENCE / ENTITY RESOLUTION SOURCE** (Informs `clubs`, `club_aliases`, `venues`, and `countries` schema mapping. NOT a match statistics source).

---

### 1.6 Kaggle Historical Football Datasets
- **Verification Status**: `LIKELY` (Varies by specific dataset upload)
- **Source Type**: User-Contributed CSV Datasets
- **Historical Results & Stats**: Varies (e.g. European Football Database 25,000+ matches 2008–2016 based on SQLite dump).
- **Licensing & Terms**: `UNCERTAIN` / Mixed CC licenses. Original provenance must be verified per dataset.
- **Recommended Role**: **REFERENCE BENCHMARK ONLY** (Used strictly if original source provenance is established; otherwise avoided in favor of direct primary feeds).

---

### 1.7 Official League & Club Feeds (e.g., PremierLeague.com, UEFA.com)
- **Verification Status**: `VERIFIED`
- **Source Type**: Official First-Party League Outlets
- **Capabilities**: Official kickoff times, confirmed lineups, official match reports, referee assignments.
- **Licensing & Terms**: Web scraping strictly restricted by terms of service / `robots.txt`. Direct API access requires commercial licensing.
- **Recommended Role**: **CURRENT MATCH CONTEXT / OFFICIAL VERIFICATION SOURCE** (Accessed via authorized API endpoints or compliant research scrapers adhering to legal rate limits).
