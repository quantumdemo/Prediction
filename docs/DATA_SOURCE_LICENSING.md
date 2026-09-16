# Data Source Licensing, Compliance & Cost Analysis (Stage 5)

## 1. LEGAL & TERMS OF SERVICE SUMMARY

| Source Name | License / Terms Status | Commercial Use Permitted? | Redistribution Terms | Attribution Required? |
| :--- | :--- | :--- | :--- | :--- |
| **Football-Data.co.uk** | Open Data / Provider Citation | YES (Non-exclusive modeling permitted) | Raw CSV redistribution requires source citation. | YES ("Data sourced from Football-Data.co.uk") |
| **API-Football (API-Sports)** | Commercial API TOS | YES (Under paid API subscription plan) | Redistribution of raw API output strictly prohibited. Internal caching permitted. | Optional (Recommended in audit logs) |
| **Football-Data.org** | API TOS (Free & Paid Tiers) | YES (Under paid tier plans) | Raw payload redistribution prohibited. | YES |
| **StatsBomb Open Data** | StatsBomb Open Data License | **NO** (Strictly Non-Commercial / Evaluation Use) | Public research redistribution permitted with explicit license notice. | **MANDATORY** ("Includes data from StatsBomb Open Data") |
| **OpenFootball (`clubs`)** | Public Domain (CC0 1.0) | YES | Unrestricted (Public Domain). | Optional |

---

## 2. COST ANALYSIS & OPERATIONAL BUDGETING

*Note: Pricing must be verified at acquisition time.*

| Provider Category | Source | Estimated Monthly Cost | Notes |
| :--- | :--- | :--- | :--- |
| Historical Match Statistics | Football-Data.co.uk | **$0.00** | Free bulk CSV downloads |
| Live Fixtures & Lineups | API-Football | **$0 – $39 / mo** | Free tier (100 req/day); Pro plan ($39/mo) provides 150,000 req/mo |
| Backup Fixtures | Football-Data.org | **$0 – €15 / mo** | Free tier for development; €15/mo for backup fallback queries |
| Research / Calibration Baseline | StatsBomb Open Data | **$0.00** | Free open-source repository |
| Entity & Reference Data | OpenFootball | **$0.00** | Free open-source repository |
| **TOTAL ESTIMATED BUDGET** | — | **$0.00 – $54.00 / mo** | Pay-as-you-grow serverless operational cost |

---

## 3. UNRESOLVED LEGAL QUESTIONS & COMPLIANCE RULES

1. **Scraping Prohibition**: Web scraping commercial sportsbook or news portals without an explicit commercial license agreement is strictly forbidden.
2. **Third-Party Odds Usage**: Betting odds supplied in historical CSVs (Football-Data.co.uk) are restricted to post-hoc model evaluation or market mapping benchmark displays. Odds MUST NOT be fed into forecasting models as predictive features.
3. **Data Caching & Retention**: Raw API response payloads cached in `raw_source_payloads` must adhere to API-Sports data retention policies (internal operational caching for prediction auditability).
