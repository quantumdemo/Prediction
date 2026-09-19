"""
Stage 16 Current-Match Feature Update & Forecasting Pipeline Test Suite

Verifies:
- Verified fixture pipeline flow and READY status
- Valid current evidence numerical feature updates
- Missing evidence handling and preserved NULL states
- Stale evidence handling and state downgrading
- Conflicting evidence blocking (BLOCKED_NO_FORECAST)
- Unverified fixture rejection
- Prediction-time leakage detection (retrieval timestamp > prediction cutoff)
- Full feature provenance preservation (fact ID, URL, state, transformation rule)
- Deterministic feature vector generation
- Correct Stage 13 selected model interface usage (XGBoostForecaster / xgboost_platt)
- Rejection of fabricated or synthetic values
"""

import unittest
from datetime import datetime, timezone

from services.ml.app.evidence.schemas import EvidenceValidationReport
from services.ml.app.evidence.validator import EvidenceValidationEngine
from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY
from services.ml.app.models.xgboost_model import XGBoostForecaster
from services.ml.app.pipeline.forecaster import CurrentMatchForecastingPipeline
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer
from services.ml.app.research.engine import CurrentMatchResearchEngine
from services.ml.app.research.schemas import FixtureVerification
from services.ml.app.research.verification import FixtureVerifier


class TestStage16CurrentForecasting(unittest.TestCase):
    def setUp(self):
        self.verifier = FixtureVerifier()
        self.research_engine = CurrentMatchResearchEngine()
        self.validation_engine = EvidenceValidationEngine()
        self.pipeline = CurrentMatchForecastingPipeline()

        self.fixture = self.verifier.verify_fixture(
            fixture_id="FIX_STAGE16_TEST_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            kickoff_time="20:00",
            venue="Old Trafford",
        )

        base_feats = {fname: 0.0 for fname in STAGE9_FEATURE_REGISTRY.keys()}
        base_feats["FEAT_REST_DAYS_HOME"] = None
        self.base_vec = MatchFeatureVector(
            fixture_id="FIX_STAGE16_TEST_001",
            match_date="2025-03-20",
            competition_id="COMP_ENG_PL",
            season_id="SEASON_20242025",
            home_club_id="CLUB_ENG_MANCHESTER_UNITED",
            away_club_id="CLUB_ENG_ARSENAL",
            features=base_feats,
            feature_availability={k: "PRESENT" if v is not None else "INSUFFICIENT_HISTORY" for k, v in base_feats.items()},
            targets={"full_time_result": "H", "full_time_home_goals": 2, "full_time_away_goals": 1, "total_goals": 3, "btts": True},
        )

    def test_verified_fixture_flow(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated to 7 days.",
                "source_name": "Premier League Official",
                "source_url": "https://www.premierleague.com/news/rest",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )

        self.assertEqual(container.validation_status, "READY")
        self.assertIsNone(container.blocked_reason)
        self.assertIsNotNone(container.forecast_output)
        self.assertEqual(container.model_name, "XGBoostForecaster")
        self.assertEqual(container.calibration_method, "platt_sigmoid")

    def test_valid_current_evidence_feature_update(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated to 8 days.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/rest",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )

        self.assertEqual(container.updated_feature_vector["FEAT_REST_DAYS_HOME"], 8.0)
        self.assertEqual(len(container.feature_provenance), 1)
        prov = container.feature_provenance[0]
        self.assertEqual(prov.feature_id, "FEAT_REST_DAYS_HOME")
        self.assertEqual(prov.updated_value, 8.0)

    def test_missing_evidence_handling(self):
        # Empty evidence report should leave features as base without failing
        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=None,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )
        self.assertEqual(container.validation_status, "READY")
        self.assertIsNone(container.updated_feature_vector.get("FEAT_REST_DAYS_HOME"))

    def test_stale_evidence_handling(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated to 5 days.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/stale",
                "retrieval_timestamp_utc": "2024-01-01T10:00:00Z",  # Stale relative to 2025-03-20
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )
        self.assertEqual(container.validation_status, "READY")
        # Stale evidence should be downgraded
        prov = container.feature_provenance[0]
        self.assertEqual(prov.evidence_state.value, "UNCERTAIN")

    def test_conflicting_evidence_blocking(self):
        raw_inputs = [
            {
                "claim": "Bukayo Saka is OUT injured with a hamstring tear.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/saka1",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "INJURIES",
                "canonical_entities_mentioned": ["Arsenal", "Bukayo Saka"],
            },
            {
                "claim": "Bukayo Saka trained fully and is FIT and available to play.",
                "source_name": "Sky Sports",
                "source_url": "https://www.skysports.com/saka2",
                "retrieval_timestamp_utc": "2025-03-18T11:00:00Z",
                "category": "INJURIES",
                "canonical_entities_mentioned": ["Arsenal", "Bukayo Saka"],
            },
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )
        self.assertEqual(container.validation_status, "BLOCKED_NO_FORECAST")
        self.assertEqual(container.blocked_reason, "UNRESOLVED_CRITICAL_EVIDENCE_CONFLICT")

    def test_invalid_fixture_rejection(self):
        invalid_fixture = FixtureVerification(
            fixture_id="FIX_UNVERIFIED_001",
            home_team="Unknown Team A",
            away_team="Unknown Team B",
            home_canonical_id="CLUB_GENERIC_A",
            away_canonical_id="CLUB_GENERIC_B",
            competition="Unknown League",
            competition_canonical_id="COMP_UNKNOWN",
            season="20242025",
            match_date="2025-03-20",
            is_verified=False,  # Unverified
        )

        container = self.pipeline.generate_current_match_forecast(
            fixture=invalid_fixture,
            validation_report=None,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )
        self.assertEqual(container.validation_status, "BLOCKED_NO_FORECAST")
        self.assertEqual(container.blocked_reason, "UNVERIFIED_FIXTURE")

    def test_prediction_time_leakage_rejection(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated after match kickoff.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/postmatch",
                "retrieval_timestamp_utc": "2025-03-21T10:00:00Z",  # Retrieved AFTER 2025-03-19 cutoff
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",  # Prediction Cutoff
        )

        self.assertEqual(container.validation_status, "BLOCKED_NO_FORECAST")
        self.assertEqual(container.blocked_reason, "PREDICTION_TIME_LEAKAGE")

    def test_missing_feature_handling_preserves_null(self):
        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=None,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )
        self.assertIsNone(container.updated_feature_vector["FEAT_REST_DAYS_HOME"])

    def test_provenance_preservation(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated to 6 days.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/rest6",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=val_report,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )

        self.assertEqual(len(container.feature_provenance), 1)
        prov = container.feature_provenance[0]
        self.assertEqual(prov.source_name, "BBC Sport")
        self.assertEqual(prov.source_url, "https://www.bbc.com/sport/football/rest6")
        self.assertEqual(prov.update_timestamp_utc, "2025-03-18T10:00:00Z")

    def test_deterministic_feature_generation(self):
        raw_inputs = [
            {
                "claim": "Home team rest days updated to 6 days.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/rest6",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "REST_CONGESTION",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United"],
            }
        ]
        res_report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validation_engine.validate_research_report(res_report)

        c1 = self.pipeline.generate_current_match_forecast(self.fixture, val_report, self.base_vec, "2025-03-19T12:00:00Z")
        c2 = self.pipeline.generate_current_match_forecast(self.fixture, val_report, self.base_vec, "2025-03-19T12:00:00Z")

        self.assertEqual(c1.updated_feature_vector, c2.updated_feature_vector)
        self.assertEqual(c1.forecast_output.probabilities_1x2, c2.forecast_output.probabilities_1x2)

    def test_correct_stage13_model_interface_usage(self):
        self.assertEqual(self.pipeline.production_model.model_name, "XGBoostForecaster")
        self.assertEqual(self.pipeline.production_model.model_version, "1.0.0")

    def test_rejection_of_fabricated_values(self):
        container = self.pipeline.generate_current_match_forecast(
            fixture=self.fixture,
            validation_report=None,
            base_feature_vector=self.base_vec,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
        )

        # Confirm unverified missing feature stays None and is not filled with synthetic defaults
        self.assertIsNone(container.updated_feature_vector["FEAT_REST_DAYS_HOME"])


if __name__ == "__main__":
    unittest.main()
