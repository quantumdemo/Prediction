# Data Contracts Specification (Stage 4)

## Architecture Overview

Data contracts establish formal type definitions and interfaces shared synchronously across:
- Next.js Web & API Gateway (`apps/web`)
- Shared TypeScript Contracts Package (`packages/contracts`)
- Python ML & Data Service (`services/ml`)
- Shared Python Contracts Library (`packages/contracts/python/football_contracts`)
- PostgreSQL Relational Database Schema (`infrastructure/database`)

## Controlled Vocabulary Enums

### 1. ValidationState
Representing the data confidence level of every ingested record:
- `VERIFIED`: Verified by multiple independent primary sources.
- `LIKELY`: Sourced from a reputable secondary provider.
- `UNCERTAIN`: Unconfirmed or single-source report.
- `CONFLICTING`: Contradictory reports exist across sources.
- `UNAVAILABLE`: Data is absent (represented as explicit `NULL`).
- `REJECTED`: Verified as inaccurate and discarded.
- `PENDING_EVIDENCE`: Awaiting current match research verification.

### 2. MatchStatus
- `SCHEDULED`
- `LIVE`
- `COMPLETED`
- `POSTPONED`
- `CANCELLED`
- `ABANDONED`
- `SUSPENDED`
- `UNKNOWN`

### 3. PredictionStatus
First-class output statuses:
- `VALID_PREDICTION`: High-confidence forecast generated.
- `NO_BET`: Explicit abstention output due to risk or missing data.
- `INSUFFICIENT_EVIDENCE`: Abstention due to incomplete research/lineup data.
- `UNSUPPORTED_FIXTURE`: Unverified fixture entity.
- `NOT_IMPLEMENTED`: System boundary response for future stages.

## Contract Alignment

Each database table maps directly to TypeScript interfaces in `packages/contracts/src/entities.ts` and Pydantic models in `packages/contracts/python/football_contracts/__init__.py`.

### Example Mapping: Club
- **TypeScript**: `export interface Club { id: string; countryId: string; canonicalName: string; shortName?: string; ... }`
- **Python**: `class Club(BaseModel): id: str; country_id: str; canonical_name: str; short_name: Optional[str] = None; ...`
- **PostgreSQL**: `CREATE TABLE clubs (id UUID PRIMARY KEY, country_id UUID NOT NULL, canonical_name VARCHAR UNIQUE, ...)`
