# Stage 8 — Entity Mapping Rules

## Multi-Level Resolution Hierarchy

| Resolution Level | Method Name | Rules & Context Required |
| :--- | :--- | :--- |
| **LEVEL 1** | Exact External / Source ID Match | Exact source identifier or established external ID. |
| **LEVEL 2** | Verified Alias Match | Verified alias match from OpenFootball or established reference database. |
| **LEVEL 3** | Controlled Normalized Match | Normalized string + country/division context produces unambiguous deterministic match. |
| **LEVEL 4** | Historical Context Match | Historical name + competition + season + country context supports identity. |
| **LEVEL 5** | Unresolved Review Queue | Ambiguous or conflicting team names sent to explicit review queue (`UNRESOLVED`). |
