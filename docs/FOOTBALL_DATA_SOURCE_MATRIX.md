# Football Data Source Capability Matrix (Stage 5)

## 22-Field Comparison Matrix

| Field # | Attribute | Football-Data.co.uk | API-Football (API-Sports) | Football-Data.org | StatsBomb Open Data | OpenFootball (`clubs`) | Official League Feeds |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Source Name** | Football-Data.co.uk | API-Football / RapidAPI | Football-Data.org | StatsBomb Open Data | OpenFootball Clubs Repo | Official League Sites (EPL/UEFA) |
| **2** | **Source Type** | Open Bulk CSV Data | Commercial REST API | REST API | Open JSON Event Repo | Open Text Reference Files | Official Web Portals |
| **3** | **Provider** | Football-Data.co.uk | API-Sports | Football-Data.org | StatsBomb Services Ltd | OpenFootball Community | Premier League / UEFA |
| **4** | **Official / 3rd Party** | Third-Party Aggregator | Third-Party Aggregator | Third-Party Aggregator | Specialized Analytics Provider | Open Reference Project | Official First-Party |
| **5** | **Historical Results** | YES (FT/HT scores) | YES (FT/HT/ET/Penalties) | YES (FT/HT scores) | YES (Selected matches) | NO | YES |
| **6** | **Historical Statistics** | YES (Shots, SOT, Fouls) | YES (Detailed team stats) | PARTIAL (Basic stats) | YES (High-density events) | NO | YES |
| **7** | **xG / xGA** | NO | YES (Recent seasons 2021+) | NO | YES (Shot-level freeze frames) | NO | PARTIAL |
| **8** | **Shots / Shots on Target**| YES (Top 5 European) | YES | PARTIAL | YES (Exact coordinates) | NO | YES |
| **9** | **Possession %** | NO | YES | PARTIAL | YES | NO | YES |
| **10** | **Corners & Cards** | YES | YES | PARTIAL | YES | NO | YES |
| **11** | **Fouls & Offsides** | YES | YES | PARTIAL | YES | NO | YES |
| **12** | **Lineups & Player Stats** | NO | YES (Starting XI, bench) | PARTIAL (Squad list) | YES (Full match lineups) | NO | YES (Official confirmed) |
| **13** | **Injuries & News** | NO | YES (Daily injury reports) | NO | NO | NO | YES (Press releases) |
| **14** | **Competition Coverage** | 22 Major European Leagues | 1000+ Leagues Globally | Top European Leagues | Selected World Cups/Euros | 50+ Global Leagues | Specific Single League |
| **15** | **Historical Depth** | 25+ Seasons (1993–2026) | 10–15 Seasons | 10+ Seasons | Tournament-specific | Static Reference Data | Current + Recent Seasons |
| **16** | **Update Frequency** | Weekly Batch CSV | Real-time / 1-min poll | Real-time / 1-min poll | Periodic GitHub commits | Static / Occasional PRs | Live / Kickoff real-time |
| **17** | **Access Method** | Direct HTTP CSV Download | RESTful JSON API | RESTful JSON API | Git Clone / Python SDK | Git Clone / Text Parse | Restricted Web Scraping / API |
| **18** | **Rate Limits** | Unlimited (Static files) | 10–30 req/sec (Paid) | 10–100 req/min | Unlimited (Local files) | Unlimited (Local files) | Strict Scraping Limits |
| **19** | **Cost Structure** | 100% Free | Free Tier / $19–$39/mo | Free Tier / €15–€49/mo | 100% Free (Non-comm) | 100% Free (Public Domain) | Commercial License Required |
| **20** | **Licensing / Terms** | Open research / Citation | Commercial subscription | Commercial/Non-comm | Non-Commercial Only | Public Domain (CC0) | Strictly Restricted |
| **21** | **Recommended Role** | **PRIMARY HISTORICAL** | **PRIMARY LIVE / FIXTURE** | **SECONDARY BACKUP** | **RESEARCH / xG BASELINE** | **ENTITY / ALIAS REF** | **OFFICIAL VERIFICATION** |
| **22** | **Verification Status** | `VERIFIED` | `VERIFIED` | `VERIFIED` | `VERIFIED` | `VERIFIED` | `VERIFIED` |
