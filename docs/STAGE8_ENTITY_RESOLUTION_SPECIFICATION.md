# Stage 8 — Entity Resolution Specification

## Executive Overview
This document specifies the exact entity identity resolution rules and hierarchy applied during **Stage 8 — Football Entity & Fixture Identification**.

The pipeline transforms Stage 7 validated historical records into controlled canonical entities across countries, competitions, seasons, clubs, club-season memberships, venues, and fixtures.

## Core Rules & Identity Prohibitions
1. **Club Name is Not Identity**: Club names vary by spelling, abbreviation, and historical context. Stable internal UUIDs are assigned to each unique entity.
2. **No Popularity/Prestige Bias**: Entity identity decisions rely strictly on deterministic evidence, country/division context, and source references. Popularity, reputation, or league status are never used as evidence.
3. **No Uncontrolled Fuzzy Resolution**: Fuzzy string matching is restricted to candidate generation and review queue placement. It is never used automatically for final identity decisions without contextual confirmation.
4. **Team Type Separation**: Senior men's clubs, women's clubs, reserve/B teams, and youth teams are explicitly separated and never merged into parent clubs.
5. **No Player Fabrication**: Player entity resolution is explicitly marked as `UNAVAILABLE` because current historical datasets do not provide line-up feeds. Fake player records are strictly prohibited.
