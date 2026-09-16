import { ValidationState, MatchStatus, EvidenceTier, IngestionStatus } from './enums.js';

export interface SourceRef {
  id: string;
  code: string;
  name: string;
  sourceType: string;
  baseUrl?: string;
  licenseNotes?: string;
  reliabilityNotes?: string;
  isActive: boolean;
}

export interface Country {
  id: string;
  code: string;
  name: string;
  region?: string;
  isActive: boolean;
}

export interface Competition {
  id: string;
  countryId?: string;
  code: string;
  name: string;
  competitionType: string;
  governingBody?: string;
  isActive: boolean;
}

export interface Season {
  id: string;
  competitionId: string;
  label: string;
  startDate?: string;
  endDate?: string;
  isCurrent: boolean;
}

export interface Venue {
  id: string;
  countryId?: string;
  canonicalName: string;
  city?: string;
  capacity?: number;
  isActive: boolean;
}

export interface Club {
  id: string;
  countryId: string;
  canonicalName: string;
  shortName?: string;
  city?: string;
  venueId?: string;
  isActive: boolean;
}

export interface ClubAlias {
  id: string;
  clubId: string;
  aliasName: string;
  sourceId?: string;
}

export interface ClubExternalId {
  id: string;
  clubId: string;
  sourceId: string;
  externalId: string;
  sourceClubName?: string;
}

export interface ClubSeasonMembership {
  id: string;
  clubId: string;
  competitionId: string;
  seasonId: string;
}

export interface Player {
  id: string;
  countryId?: string;
  canonicalName: string;
  dateOfBirth?: string;
  position?: string;
  isActive: boolean;
}

export interface PlayerClubMembership {
  id: string;
  playerId: string;
  clubId: string;
  seasonId: string;
  shirtNumber?: number;
  startDate?: string;
  endDate?: string;
}

export interface MatchEntity {
  id: string;
  competitionId: string;
  seasonId: string;
  homeClubId: string;
  awayClubId: string;
  venueId?: string;
  scheduledKickoffUtc: string;
  actualKickoffUtc?: string;
  status: MatchStatus;
  homeScore?: number;
  awayScore?: number;
  validationState: ValidationState;
}

export interface MatchExternalId {
  id: string;
  matchId: string;
  sourceId: string;
  externalMatchId: string;
}

export interface MatchStatistic {
  id: string;
  matchId: string;
  clubId?: string;
  statType: string;
  statValue: number;
  period: string;
  sourceId?: string;
  validationState: ValidationState;
}

export interface MatchEvent {
  id: string;
  matchId: string;
  clubId: string;
  playerId?: string;
  eventCategory: string;
  minute: number;
  extraMinute?: number;
  sourceId?: string;
  validationState: ValidationState;
}

export interface MatchLineup {
  id: string;
  matchId: string;
  clubId: string;
  playerId: string;
  role: string;
  position?: string;
  shirtNumber?: number;
  sourceId?: string;
}

export interface RawSourcePayload {
  id: string;
  sourceId: string;
  entityType: string;
  externalIdentifier: string;
  rawPayloadJson: string;
  retrievedAtUtc: string;
  ingestionRunId?: string;
}

export interface ProvenanceRecord {
  id: string;
  entityType: string;
  entityId: string;
  sourceId: string;
  sourceUrl?: string;
  retrievedAtUtc: string;
  validationState: ValidationState;
  notes?: string;
}

export interface DatasetVersion {
  id: string;
  versionLabel: string;
  cutoffTimestampUtc: string;
  recordCount: number;
  notes?: string;
}

export interface IngestionRun {
  id: string;
  sourceId: string;
  status: IngestionStatus;
  recordsIngested: number;
  errorLog?: string;
  startedAtUtc: string;
  completedAtUtc?: string;
}

// References for UI and API lightweight rendering
export interface CompetitionRef {
  id: string;
  code: string;
  name: string;
  country: string;
}

export interface TeamRef {
  id: string;
  canonicalName: string;
  country: string;
}

export interface FixtureIdentification {
  fixtureId: string;
  season: string;
  competition: CompetitionRef;
  homeTeam: TeamRef;
  awayTeam: TeamRef;
  scheduledKickoffUtc: string;
  validationState: ValidationState;
}

export interface EvidenceItem {
  id: string;
  tier: EvidenceTier;
  sourceUrl: string;
  title: string;
  extractedAtUtc: string;
  snippet?: string;
  reliabilityScore: number;
}
