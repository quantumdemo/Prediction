# Data Acquisition Risk Register (Stage 5)

## Risk Register Table

| Risk ID | Category | Risk Description | Severity | Likelihood | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RISK-ACQ-001** | Data Quality | Historical statistics (shots/corners) unavailable for lower-tier leagues. | HIGH | HIGH | Restrict model feature scope for lower tiers or issue `NO BET` when stats are missing. |
| **RISK-ACQ-002** | Entity Resolution | Inconsistent club name spellings across providers (e.g., 'Man Utd' vs 'Manchester United FC'). | CRITICAL | HIGH | Map external provider club IDs to canonical club UUIDs using `club_aliases` and `club_external_ids`. |
| **RISK-ACQ-003** | API Rate Limits | Burst request limits hit during live fixture polling. | MEDIUM | MEDIUM | Implement HTTP retry with exponential backoff and local cache layer in `raw_source_payloads`. |
| **RISK-ACQ-004** | Data Revision | Historical score or stat retroactively updated by data provider. | LOW | LOW | Preserve immutable `raw_source_payloads` and track revision timestamps in `provenance_records`. |
| **RISK-ACQ-005** | Service Discontinuation | API provider changes endpoints or discontinues free tiers. | MEDIUM | LOW | Maintain secondary backup sources (Football-Data.org) and decoupled acquisition adapters. |
| **RISK-ACQ-006** | Lineup Instability | Confirmed lineup unavailable close to kickoff time. | HIGH | MEDIUM | Issue `NO BET / INSUFFICIENT EVIDENCE` if lineup uncertainty score exceeds risk threshold. |
| **RISK-ACQ-007** | Pricing Changes | API subscription fees increase unexpectedly. | LOW | LOW | Monitor API usage metrics and enforce request budget limits. |
