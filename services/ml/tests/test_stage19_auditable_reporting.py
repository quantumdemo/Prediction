"""
Stage 19 Auditable Prediction Reporting & History Test Suite

Verifies:
- Complete eligible prediction report generation
- NO-BET and insufficient evidence prediction report generation
- Blocked forecast report generation
- Prediction chain provenance preservation
- Forecaster model name, version, and calibration method preservation
- Mapped market probability preservation
- Confidence metric and risk assessment preservation
- Deterministic SHA256 audit hash generation
- Prediction history repository persistence and multi-criteria retrieval
- Prediction report immutability (overwriting throws ValueError)
- Strict separation of probability vs confidence score
- Absolute absence of fabricated values, bookmaker odds, expected value edge, or Kelly stake sizing
"""

import unittest
from services.ml.app.markets.mapper import MarketMapper
from services.ml.app.models.base import ForecastOutput
from services.ml.app.pipeline.schemas import CurrentFeatureProvenance, CurrentMatchForecastContainer
from services.ml.app.reporting.generator import AuditableReportGenerator
from services.ml.app.reporting.repository import PredictionHistoryRepository
from services.ml.app.reporting.schemas import PredictionHistoryFilter
from services.ml.app.research.schemas import FixtureVerification, ResearchState
from services.ml.app.risk.engine import RiskEngine
from services.ml.app.risk.schemas import DecisionStatus


class TestStage19AuditableReporting(unittest.TestCase):
    def setUp(self):
        self.generator = AuditableReportGenerator()
        self.repository = PredictionHistoryRepository()
        self.mapper = MarketMapper()
        self.risk_engine = RiskEngine()

        self.fixture = FixtureVerification(
            fixture_id="FIX_STAGE19_TEST_001",
            home_team="Manchester United",
            away_team="Arsenal",
            home_canonical_id="CLUB_ENG_MANCHESTER_UNITED",
            away_canonical_id="CLUB_ENG_ARSENAL",
            competition="Premier League",
            competition_canonical_id="COMP_ENG_PL",
            season="20242025",
            match_date="2025-03-20",
        )

        self.forecast_output = ForecastOutput(
            fixture_id="FIX_STAGE19_TEST_001",
            match_date="2025-03-20",
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            expected_home_goals=1.6,
            expected_away_goals=1.2,
            probabilities_1x2={"home": 0.58, "draw": 0.22, "away": 0.20},
            probabilities_totals={
                "over_0_5": 0.92, "under_0_5": 0.08,
                "over_1_5": 0.75, "under_1_5": 0.25,
                "over_2_5": 0.55, "under_2_5": 0.45,
                "over_3_5": 0.32, "under_3_5": 0.68,
                "over_4_5": 0.15, "under_4_5": 0.85,
            },
            probabilities_btts={"btts_yes": 0.58, "btts_no": 0.42},
            correct_score_matrix={0: {0: 0.10}},
        )

        self.ready_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_STAGE19_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={"FEAT_REST_DAYS_HOME": 7.0},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=self.forecast_output,
            validation_status="READY",
        )

        self.market_report = self.mapper.map_forecast_container_to_markets(self.ready_container)
        self.risk_report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)

    def test_complete_eligible_prediction_report(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)

        self.assertEqual(report.fixture_id, "FIX_STAGE19_TEST_001")
        self.assertEqual(report.model_name, "XGBoostForecaster")
        self.assertEqual(report.calibration_method, "platt_sigmoid")
        self.assertEqual(report.final_decision_status, DecisionStatus.ELIGIBLE.value)
        self.assertTrue(len(report.audit_hash) == 64)

    def test_no_bet_prediction_report(self):
        low_fc = ForecastOutput(
            fixture_id="FIX_STAGE19_NOBET",
            match_date="2025-03-20",
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            expected_home_goals=1.0,
            expected_away_goals=1.0,
            probabilities_1x2={"home": 0.35, "draw": 0.34, "away": 0.31},
            probabilities_totals={"over_2_5": 0.50, "under_2_5": 0.50},
            probabilities_btts={"btts_yes": 0.50, "btts_no": 0.50},
            correct_score_matrix={0: {0: 0.10}},
        )
        low_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_NOBET",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="none",
            forecast_output=low_fc,
            validation_status="READY",
        )
        mkt_rep = self.mapper.map_forecast_container_to_markets(low_container)
        risk_rep = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_rep, low_container)

        report = self.generator.generate_report(low_container, mkt_rep, risk_rep)
        self.assertIn(report.final_decision_status, [DecisionStatus.LOW_CONFIDENCE.value, DecisionStatus.HIGH_RISK.value])

    def test_blocked_prediction_report(self):
        blocked_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_BLOCKED",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            validation_status="BLOCKED_NO_FORECAST",
            blocked_reason="UNVERIFIED_FIXTURE",
        )
        mkt_rep = self.mapper.map_forecast_container_to_markets(blocked_container)
        risk_rep = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_rep, blocked_container)

        report = self.generator.generate_report(blocked_container, mkt_rep, risk_rep)
        self.assertEqual(report.final_decision_status, DecisionStatus.BLOCKED.value)
        self.assertIn("UNVERIFIED_FIXTURE", report.blocked_reasons)

    def test_provenance_preservation(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        prov = report.provenance_chain

        self.assertEqual(prov.fixture_id, "FIX_STAGE19_TEST_001")
        self.assertEqual(prov.model_name, "XGBoostForecaster")
        self.assertEqual(prov.calibration_method, "platt_sigmoid")

    def test_model_version_preservation(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.assertEqual(report.model_name, "XGBoostForecaster")
        self.assertEqual(report.model_version, "1.0.0_platt")

    def test_market_probability_preservation(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.assertIn("MKT_1X2", report.market_probabilities)
        mkt_1x2 = report.market_probabilities["MKT_1X2"]
        self.assertTrue(mkt_1x2["is_supported"])

    def test_confidence_risk_preservation(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.assertIn("MKT_1X2", report.confidence_metrics)
        self.assertIn("MKT_1X2", report.risk_assessment)

    def test_audit_hash_determinism(self):
        r1 = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        r2 = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)

        self.assertEqual(r1.audit_hash, r2.audit_hash)
        self.assertEqual(len(r1.audit_hash), 64)

    def test_prediction_persistence_and_retrieval(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.repository.save_report(report)

        by_id = self.repository.get_by_report_id(report.report_id)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.report_id, report.report_id)

        by_pred = self.repository.get_by_prediction_id(report.prediction_id)
        self.assertIsNotNone(by_pred)
        self.assertEqual(by_pred.prediction_id, report.prediction_id)

    def test_prediction_history_filtering(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.repository.save_report(report)

        q = PredictionHistoryFilter(
            fixture_id="FIX_STAGE19_TEST_001",
            decision_status=DecisionStatus.ELIGIBLE.value,
        )
        res = self.repository.query_history(q)
        self.assertEqual(len(res), 1)

    def test_prediction_report_immutability(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        self.repository.save_report(report)

        # Attempting to save duplicate report ID must raise ValueError
        with self.assertRaises(ValueError):
            self.repository.save_report(report)

    def test_separation_of_probability_vs_confidence(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)

        prob_1x2_home = report.forecast_probabilities["probabilities_1x2"]["home"]
        conf_1x2_score = report.confidence_metrics["MKT_1X2"]["score"]

        # Probability (0.58) and Confidence Score (e.g. 0.81) are distinct concepts
        self.assertNotEqual(prob_1x2_home, conf_1x2_score)

    def test_no_fabricated_values(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        report_dict = report.model_dump()

        # Unused or missing fields must remain None, not manufactured
        self.assertIsNone(report.blocked_reasons)

    def test_no_bookmaker_odds_usage(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        report_dict = report.model_dump()

        self.assertNotIn("bookmaker_odds", report_dict)
        self.assertNotIn("odds", report_dict)

    def test_no_ev_edge_calculation(self):
        report = self.generator.generate_report(self.ready_container, self.market_report, self.risk_report)
        report_dict = report.model_dump()

        self.assertNotIn("expected_value", report_dict)
        self.assertNotIn("edge", report_dict)
        self.assertNotIn("kelly_stake", report_dict)


if __name__ == "__main__":
    unittest.main()
