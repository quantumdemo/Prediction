import { ValidationState, EvidenceTier } from './enums.js';

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
