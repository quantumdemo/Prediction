# Entity Mapping & Normalization Rules (Stage 6)

## Overview

Stage 6 implements deterministic entity normalization required to map raw provider team names (e.g. Football-Data.co.uk team `Arsenal` or `Man United`) to canonical database entities (`clubs`, `club_aliases`, `club_external_ids`).

## Resolution Steps

1. **Exact Match**: Check `clubs.canonical_name == team_name`.
2. **Alias Resolution**: Check `club_aliases.alias_name == team_name`.
3. **External ID Resolution**: Check `club_external_ids.source_club_name == team_name` for `source_id`.
4. **New Entity Creation**: If no match exists, create a new canonical `clubs` record, insert a corresponding `club_aliases` entry, and generate a `club_external_ids` record.

*Note: Advanced probabilistic or fuzzy string entity resolution is reserved for Stage 8.*
