# Stage 7 — Normalization Rules

## Directives
1. **Schema Normalization**: Map raw source fields into project canonical names without changing underlying meaning.
2. **Date & Time Normalization**:
   - Dates converted into canonical `YYYY-MM-DD` ISO 8601 representation.
   - Match times preserved in `HH:MM:SS` CET-1 representation without converting unknown timezones or inventing kickoff times.
3. **Season Normalization**:
   - Seasons derived deterministically from match dates (e.g. `2024-08-18` -> `2024/25`).
4. **Division Normalization**:
   - Division codes mapped to `source_division_code` (e.g. `E0`, `I1`, `SP1`) without premature entity resolution.
5. **Club String Normalization**:
   - Leading/trailing whitespace trimmed and inner spaces collapsed.
   - Comparison keys generated in lowercase for deterministic lookup keys.
   - Raw club names strictly preserved (`raw_home_team_name`, `raw_away_team_name`). No fuzzy club merging or canonical UUID assignments in Stage 7.
