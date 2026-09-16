# OpenFootball Source Research & Design Notes

## Overview

- **Source Name**: OpenFootball Clubs Repository (`openfootball/clubs`)
- **Repository URL**: `https://github.com/openfootball/clubs/tree/master`
- **License / Usage**: Public Domain (CC0 1.0 Universal)
- **Retrieval Date**: September 2026
- **Primary Role in Platform**: Reference dataset informing canonical club entity structures, club aliases, stadium/venue reference modeling, country relationships, and entity resolution schema design.

## Directory & File Structure

The OpenFootball clubs repository uses a structured plain-text data hierarchy organized by country and league tier:

```
openfootball/clubs/
├── 1-england/
│   ├── clubs.txt        # Club codes, canonical names, cities, stadium references
│   └── stadiums.txt     # Venue names, cities, capacity
├── 1-spain/
│   └── clubs.txt
├── 1-germany/
│   └── clubs.txt
└── ...
```

### Typical Record Format
```txt
eng.1 | Arsenal FC        | Arsenal      | London    | Emirates Stadium
eng.1 | Chelsea FC        | Chelsea      | London    | Stamford Bridge
```

## Intended System Role

OpenFootball data informs the design of the following core database entities in Stage 4:
1. **Canonical Club Reference (`clubs`)**: Informs short name, canonical name, city, and country association schema.
2. **Club Aliases (`club_aliases`)**: Informs alternate spelling and variant name resolution structures.
3. **Venues / Stadiums (`venues`)**: Informs venue entity design (name, city, capacity, country).
4. **External Identifiers (`club_external_ids`)**: Informs mapping of source-specific codes (e.g. `eng.1 / arsenal`) to canonical UUIDs.

## Critical Limitations & Non-Goals

1. **Not a Historical Match Dataset**: OpenFootball `clubs` contains zero match results, goals, shots, possession, corners, cards, or xG.
2. **No Model-Ready Data**: It cannot be used to train forecasting models or derive team strength parameters.
3. **No Player Statistics**: It contains no player rosters, transfer histories, or player performance metrics.
4. **No Direct Ingestion**: OpenFootball data is used strictly for schema and reference modeling. Broad production data ingestion belongs to later stages.
