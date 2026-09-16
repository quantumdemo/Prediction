# DATA ARCHITECTURE & CONCEPTUAL DATABASE SCHEMAS
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. CONCEPTUAL ENTITY RELATIONSHIP MODEL

```
[Country] ──1:N──► [Competition] ──1:N──► [Season]
                       │                     │
                       └─────────┐ ┌─────────┘
                                 ▼ ▼
                             [Match] ◄──1:N── [Match Statistics]
                              ▲   ▲
                      Home Club   Away Club
                              │   │
                          [Club] ──1:N──► [Player]
                            │                │
                      [Club Alias]    [Player Alias]

----------------------------------------------------------------------
SYSTEM AUDIT & MODEL PROVENANCE ENTITIES:

[Dataset Version] ──1:N──► [Feature Version] ──1:N──► [Model Version]
                                                            │
                                                            ▼
[Prediction Log] ◄──1:N── [Prediction Evidence]    [Calibration Model]
       │
       ▼
[Market Outcome]
```

---

### 2. CORE DATABASE ENTITIES & SCHEMA DEFINITIONS

#### 2.1 Entity Identifiers
- All core entities use 128-bit `UUIDv4` primary keys for global uniqueness.
- External provider IDs (e.g., API-Football ID, Football-Data ID) are stored in dedicated mapping tables (`external_entity_mappings`).

#### 2.2 Key Table Specifications

##### `countries`
- `id`: `UUID` (PK)
- `name`: `VARCHAR(100)` (UNIQUE)
- `iso_code`: `VARCHAR(3)` (UNIQUE)

##### `competitions`
- `id`: `UUID` (PK)
- `country_id`: `UUID` (FK -> `countries.id`)
- `name`: `VARCHAR(150)`
- `code`: `VARCHAR(50)`
- `format`: `VARCHAR(50)` (e.g., `DOMESTIC_LEAGUE`, `CUP`, `INTERNATIONAL`)

##### `clubs`
- `id`: `UUID` (PK)
- `country_id`: `UUID` (FK -> `countries.id`)
- `canonical_name`: `VARCHAR(150)`
- `short_name`: `VARCHAR(50)`

##### `club_aliases`
- `id`: `UUID` (PK)
- `club_id`: `UUID` (FK -> `clubs.id`)
- `alias_name`: `VARCHAR(150)` (INDEXed)
- `source_provider`: `VARCHAR(50)`

##### `matches`
- `id`: `UUID` (PK)
- `competition_id`: `UUID` (FK -> `competitions.id`)
- `season_year`: `INT`
- `kickoff_timestamp`: `TIMESTAMPTZ` (INDEXed)
- `home_club_id`: `UUID` (FK -> `clubs.id`)
- `away_club_id`: `UUID` (FK -> `clubs.id`)
- `home_score`: `INT NULL`
- `away_score`: `INT NULL`
- `match_status`: `VARCHAR(30)` (`SCHEDULED`, `FINISHED`, `POSTPONED`, `CANCELLED`)

##### `match_statistics`
- `id`: `UUID` (PK)
- `match_id`: `UUID` (FK -> `matches.id`)
- `home_shots`: `INT NULL`
- `away_shots`: `INT NULL`
- `home_shots_on_target`: `INT NULL`
- `away_shots_on_target`: `INT NULL`
- `home_corners`: `INT NULL`
- `away_corners`: `INT NULL`
- `home_xg`: `NUMERIC(4,2) NULL`
- `away_xg`: `NUMERIC(4,2) NULL`
- `provenance_url`: `TEXT`
- `ingested_at`: `TIMESTAMPTZ`

##### `predictions`
- `id`: `UUID` (PK)
- `match_id`: `UUID` (FK -> `matches.id`)
- `prediction_timestamp`: `TIMESTAMPTZ`
- `model_version_id`: `UUID` (FK -> `model_versions.id`)
- `feature_version_id`: `UUID` (FK -> `feature_versions.id`)
- `calibration_version_id`: `UUID` (FK -> `calibration_models.id`)
- `p_home_win`: `NUMERIC(5,4)`
- `p_draw`: `NUMERIC(5,4)`
- `p_away_win`: `NUMERIC(5,4)`
- `decision`: `VARCHAR(30)` (`PREDICTION`, `NO_BET`)
- `risk_score`: `NUMERIC(4,3)`
- `audit_snapshot`: `JSONB`
