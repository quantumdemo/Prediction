import { PredictionStatus, MarketType } from './enums.js';
import { FixtureIdentification, EvidenceItem } from './entities.js';

export interface ModelMetadata {
  modelId: string;
  modelName: string;
  version: string;
  modelType: string; // e.g. 'Poisson', 'XGBoost'
  trainedAtUtc: string;
  calibrationMethod?: string;
}

export interface DatasetMetadata {
  datasetId: string;
  cutoffTimestampUtc: string;
  recordCount: number;
}

export interface PredictionRequest {
  fixtureId: string;
  correlationId: string;
  requestedMarkets?: MarketType[];
  forceFreshResearch?: boolean;
}

export interface ProbabilityDistribution {
  homeWinProb?: number;
  drawProb?: number;
  awayWinProb?: number;
  overProb?: number;
  underProb?: number;
  bttsYesProb?: number;
  bttsNoProb?: number;
}

export interface PredictionResponse {
  predictionId: string;
  fixture: FixtureIdentification;
  status: PredictionStatus;
  noBetReason?: string;
  probabilities?: ProbabilityDistribution;
  recommendedMarket?: MarketType;
  confidenceScore?: number;
  evidence: EvidenceItem[];
  modelMetadata?: ModelMetadata;
  datasetMetadata?: DatasetMetadata;
  generatedAtUtc: string;
  correlationId: string;
}
