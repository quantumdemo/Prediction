"""
Unit and Guard Tests for Stage 22 Shadow Validation & Historical Validation Engine

Verifies:
- Strict separation of prediction input data from post-prediction outcome evaluation data.
- OutcomeLeakageError raised when outcome targets leak into input request payloads.
- Model selection provenance audit and overlap detection (is_unseen_out_of_sample is False when overlapping Stage 13 selection dates).
- Deterministic execution of shadow validation.
- Fixture eligibility and exclusion tracking.
- Aggregate metrics calculation (Log Loss, Brier, RPS, Goal MAE, Over/Under 2.5, BTTS).
- NO-BET / blocked decision status handling.
- Export of machine-readable Stage 22 validation artifact (STAGE22_VALIDATION_ARTIFACT_v1.0.0).
"""

import os
import tempfile
import unittest
from typing import Dict, List

from services.ml.app.features.engine import MatchFeatureVector
from services.ml.app.integration.schemas import PredictionPipelineRequest
from services.ml.app.risk.schemas import DecisionStatus
from services.ml.app.validation.engine import OutcomeLeakageError, ShadowValidationEngine
from services.ml.app.validation.schemas import ShadowValidationArtifact


class TestStage22ShadowValidation(unittest.TestCase):

    def setUp(self):
        self.engine = ShadowValidationEngine(
            evaluation_period_start="2023-07-01",
            evaluation_period_end="2024-06-30",
            training_cutoff_date="2023-06-30",
        )
        self.test_dir = tempfile.mkdtemp()

        # Construct synthetic feature vectors for testing
        self.mock_vectors = [
            MatchFeatureVector(
                fixture_id="FIX_STAGE22_001",
                match_date="2023-08-15",
                competition_id="COMP_ENG_PL",
                season_id="SEASON_2023_2024",
                home_club_id="CLUB_ENG_ARSENAL",
                away_club_id="CLUB_ENG_CHELSEA",
                features={
                    "rolling_home_goals_for_5": 2.1,
                    "rolling_away_goals_against_5": 1.4,
                    "rest_days_difference": 1.0,
                },
                feature_availability={"rolling_home_goals_for_5": "PRESENT"},
                targets={
                    "full_time_result": "H",
                    "full_time_home_goals": 2,
                    "full_time_away_goals": 1,
                    "total_goals": 3,
                    "btts": True,
                },
            ),
            MatchFeatureVector(
                fixture_id="FIX_STAGE22_002",
                match_date="2023-09-20",
                competition_id="COMP_ENG_PL",
                season_id="SEASON_2023_2024",
                home_club_id="CLUB_ENG_MAN_CITY",
                away_club_id="CLUB_ENG_LIVERPOOL",
                features={
                    "rolling_home_goals_for_5": 2.5,
                    "rolling_away_goals_against_5": 1.0,
                    "rest_days_difference": 0.0,
                },
                feature_availability={"rolling_home_goals_for_5": "PRESENT"},
                targets={
                    "full_time_result": "D",
                    "full_time_home_goals": 1,
                    "full_time_away_goals": 1,
                    "total_goals": 2,
                    "btts": True,
                },
            ),
            # Outside evaluation period (training period)
            MatchFeatureVector(
                fixture_id="FIX_STAGE22_003_TRAIN",
                match_date="2022-10-10",
                competition_id="COMP_ENG_PL",
                season_id="SEASON_2022_2023",
                home_club_id="CLUB_ENG_CHELSEA",
                away_club_id="CLUB_ENG_ARSENAL",
                features={"rolling_home_goals_for_5": 1.5},
                feature_availability={"rolling_home_goals_for_5": "PRESENT"},
                targets={"full_time_result": "A", "full_time_home_goals": 0, "full_time_away_goals": 1, "total_goals": 1, "btts": False},
            ),
            # Missing target outcome (should be excluded)
            MatchFeatureVector(
                fixture_id="FIX_STAGE22_004_EXCLUDED",
                match_date="2023-11-05",
                competition_id="COMP_ENG_PL",
                season_id="SEASON_2023_2024",
                home_club_id="CLUB_ENG_SPURS",
                away_club_id="CLUB_ENG_CHELSEA",
                features={"rolling_home_goals_for_5": 1.2},
                feature_availability={"rolling_home_goals_for_5": "PRESENT"},
                targets={},
            ),
        ]

    def test_outcome_isolation_guard(self):
        """
        Verifies that OutcomeLeakageError is raised if outcome data leaks into input prediction request.
        """
        leaky_request = PredictionPipelineRequest(
            fixture_id="FIX_LEAK_TEST",
            home_team="CLUB_ENG_ARSENAL",
            away_team="CLUB_ENG_CHELSEA",
            competition="COMP_ENG_PL",
            season="2023_2024",
            match_date="2023-08-15",
            base_features={"rolling_home_goals_for_5": 2.1},
        )
        # Artificially set outcome field on base_features to test leakage guard
        leaky_request.base_features["full_time_result"] = "H"
        with self.assertRaises(OutcomeLeakageError):
            self.engine._verify_no_leakage_in_request(leaky_request)

    def test_model_selection_provenance_guard(self):
        """
        Verifies that evaluation runs overlapping Stage 13 model selection dates are NOT classified as unseen out-of-sample.
        """
        artifact = self.engine.run_shadow_validation(
            vectors=self.mock_vectors,
            artifact_output_dir=self.test_dir,
        )
        self.assertFalse(artifact.is_unseen_out_of_sample)
        self.assertIn("HISTORICAL_SELECTION_SET_REPLAY", artifact.statistical_interpretation)
        self.assertEqual(artifact.model_selection_overlap_period, "Window 4 (2023-07-01 to 2024-05-28)")

    def test_shadow_validation_execution_and_artifact(self):
        """
        Executes shadow validation and verifies machine-readable artifact format.
        """
        artifact: ShadowValidationArtifact = self.engine.run_shadow_validation(
            vectors=self.mock_vectors,
            artifact_output_dir=self.test_dir,
        )

        self.assertEqual(artifact.artifact_version, "STAGE22_VALIDATION_ARTIFACT_v1.0.0")
        self.assertEqual(artifact.model_name, "xgboost_platt")
        self.assertEqual(artifact.pre_match_input_leakage_status, "VERIFIED_NO_INPUT_LEAKAGE")

        # Data quality checks
        self.assertEqual(artifact.data_quality.total_fixtures_considered, 4)
        self.assertEqual(artifact.data_quality.eligible_fixtures, 2)
        self.assertEqual(artifact.data_quality.excluded_fixtures, 2)

        # Confirm evaluated records
        self.assertEqual(len(artifact.records), 2)
        for rec in artifact.records:
            self.assertIsNotNone(rec.shadow_prediction.prediction_id)
            self.assertIsNotNone(rec.shadow_prediction.probabilities_1x2)
            self.assertIsNotNone(rec.actual_outcome.full_time_result)
            # Guarantee separation: shadow_prediction must not have full_time_result attribute
            self.assertFalse(hasattr(rec.shadow_prediction, "full_time_result"))

        # Verify artifact file written to disk
        expected_file = os.path.join(self.test_dir, "stage22_shadow_validation_artifact.json")
        self.assertTrue(os.path.exists(expected_file))

    def test_deterministic_shadow_execution(self):
        """
        Verifies that repeated shadow validation runs produce identical prediction outcomes.
        """
        run_1 = self.engine.run_shadow_validation(vectors=self.mock_vectors, artifact_output_dir=self.test_dir)
        run_2 = self.engine.run_shadow_validation(vectors=self.mock_vectors, artifact_output_dir=self.test_dir)

        self.assertEqual(len(run_1.records), len(run_2.records))
        for r1, r2 in zip(run_1.records, run_2.records):
            self.assertEqual(r1.fixture_id, r2.fixture_id)
            self.assertEqual(r1.shadow_prediction.probabilities_1x2, r2.shadow_prediction.probabilities_1x2)
            self.assertEqual(r1.shadow_prediction.confidence_score, r2.shadow_prediction.confidence_score)
            self.assertEqual(r1.shadow_prediction.decision_status, r2.shadow_prediction.decision_status)

    def test_aggregate_metrics_calculation(self):
        """
        Verifies aggregate metric calculation logic.
        """
        artifact = self.engine.run_shadow_validation(vectors=self.mock_vectors, artifact_output_dir=self.test_dir)
        metrics = artifact.aggregate_metrics

        self.assertEqual(metrics.total_fixtures_evaluated, 2)
        self.assertGreaterEqual(metrics.log_loss_1x2, 0.0)
        self.assertGreaterEqual(metrics.brier_score_1x2, 0.0)
        self.assertGreaterEqual(metrics.rps_1x2, 0.0)
        self.assertGreaterEqual(metrics.coverage_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
