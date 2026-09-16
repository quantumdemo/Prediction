-- PostgreSQL Production Football Database Schema
-- Stage 4: Database Schema & Data Contracts

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Source Registry
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    base_url VARCHAR(512),
    license_notes TEXT,
    reliability_notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Countries
CREATE TABLE IF NOT EXISTS countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(3) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Competitions
CREATE TABLE IF NOT EXISTS competitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID REFERENCES countries(id) ON DELETE RESTRICT,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(64) NOT NULL,
    governing_body VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Seasons
CREATE TABLE IF NOT EXISTS seasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    label VARCHAR(32) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_competition_season UNIQUE (competition_id, label)
);

-- 5. Venues / Stadiums
CREATE TABLE IF NOT EXISTS venues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID REFERENCES countries(id) ON DELETE SET NULL,
    canonical_name VARCHAR(255) NOT NULL,
    city VARCHAR(128),
    capacity INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Clubs
CREATE TABLE IF NOT EXISTS clubs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
    canonical_name VARCHAR(255) NOT NULL UNIQUE,
    short_name VARCHAR(128),
    city VARCHAR(128),
    venue_id UUID REFERENCES venues(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Club Aliases
CREATE TABLE IF NOT EXISTS club_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    alias_name VARCHAR(255) NOT NULL UNIQUE,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. Club External Identifiers
CREATE TABLE IF NOT EXISTS club_external_ids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    external_id VARCHAR(255) NOT NULL,
    source_club_name VARCHAR(255),
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_source_external_club UNIQUE (source_id, external_id)
);

-- 9. Club Season Memberships
CREATE TABLE IF NOT EXISTS club_season_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_club_season UNIQUE (club_id, season_id)
);

-- 10. Players
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID REFERENCES countries(id) ON DELETE SET NULL,
    canonical_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    position VARCHAR(64),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. Player Club Memberships
CREATE TABLE IF NOT EXISTS player_club_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    shirt_number INTEGER,
    start_date DATE,
    end_date DATE,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 12. Matches
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE RESTRICT,
    season_id UUID NOT NULL REFERENCES seasons(id) ON DELETE RESTRICT,
    home_club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE RESTRICT,
    away_club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE RESTRICT,
    venue_id UUID REFERENCES venues(id) ON DELETE SET NULL,
    scheduled_kickoff_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_kickoff_utc TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    home_score INTEGER,
    away_score INTEGER,
    validation_state VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED',
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_different_clubs CHECK (home_club_id <> away_club_id)
);

-- 13. Match External Identifiers
CREATE TABLE IF NOT EXISTS match_external_ids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    external_match_id VARCHAR(255) NOT NULL,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_source_external_match UNIQUE (source_id, external_match_id)
);

-- 14. Match Statistics
CREATE TABLE IF NOT EXISTS match_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    club_id UUID REFERENCES clubs(id) ON DELETE CASCADE,
    stat_type VARCHAR(64) NOT NULL,
    stat_value NUMERIC NOT NULL,
    period VARCHAR(32) NOT NULL DEFAULT 'FULL_TIME',
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    validation_state VARCHAR(32) NOT NULL DEFAULT 'VERIFIED',
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 15. Match Events
CREATE TABLE IF NOT EXISTS match_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE SET NULL,
    event_category VARCHAR(64) NOT NULL,
    minute INTEGER NOT NULL,
    extra_minute INTEGER,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    validation_state VARCHAR(32) NOT NULL DEFAULT 'VERIFIED',
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 16. Match Lineups
CREATE TABLE IF NOT EXISTS match_lineups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    club_id UUID NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL DEFAULT 'STARTING',
    position VARCHAR(64),
    shirt_number INTEGER,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_match_player_role UNIQUE (match_id, player_id, role)
);

-- 17. Raw Source Payloads
CREATE TABLE IF NOT EXISTS raw_source_payloads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    entity_type VARCHAR(64) NOT NULL,
    external_identifier VARCHAR(255) NOT NULL,
    raw_payload_json TEXT NOT NULL,
    retrieved_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ingestion_run_id UUID
);

-- 18. Provenance Records
CREATE TABLE IF NOT EXISTS provenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(64) NOT NULL,
    entity_id UUID NOT NULL,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    source_url VARCHAR(512),
    retrieved_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    validation_state VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED',
    notes TEXT
);

-- 19. Dataset Versions
CREATE TABLE IF NOT EXISTS dataset_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_label VARCHAR(64) NOT NULL UNIQUE,
    cutoff_timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 20. Ingestion Runs
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    status VARCHAR(32) NOT NULL DEFAULT 'STARTED',
    records_ingested INTEGER NOT NULL DEFAULT 0,
    error_log TEXT,
    started_at_utc TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at_utc TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clubs_canonical_name ON clubs(canonical_name);
CREATE INDEX IF NOT EXISTS idx_club_aliases_name ON club_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_club_ext_id ON club_external_ids(source_id, external_id);
CREATE INDEX IF NOT EXISTS idx_matches_comp_season ON matches(competition_id, season_id);
CREATE INDEX IF NOT EXISTS idx_matches_kickoff ON matches(scheduled_kickoff_utc);
CREATE INDEX IF NOT EXISTS idx_matches_home_away ON matches(home_club_id, away_club_id);
CREATE INDEX IF NOT EXISTS idx_match_ext_id ON match_external_ids(source_id, external_match_id);
CREATE INDEX IF NOT EXISTS idx_match_stats_match ON match_statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_provenance_entity ON provenance_records(entity_type, entity_id);
