# Stage 7 — Quarantine Policy

## Policy Directives
1. **Zero Discard Policy**: Quarantined records are NEVER deleted or silently discarded. They are preserved with complete source provenance and failure diagnostics.
2. **Quarantine Criteria**:
   - Malformed or out-of-bounds dates / times.
   - Missing required match identifier fields (`Division`, `MatchDate`, `HomeTeam`, `AwayTeam`).
   - Score / Result contradictions (e.g. `FTHome: 2, FTAway: 0, FTResult: A`).
   - Invalid statistical relationships (`shots_on_target > total_shots`, negative cards/fouls).
   - Duplicate match fixture records.
3. **Quarantine Payload Attributes**:
   - `raw_source_file`
   - `source_row_index`
   - `source_sha256`
   - `quarantine_timestamp_utc`
   - `pipeline_version`
   - `rule_violated`
   - `violation_message`
   - `raw_payload`
