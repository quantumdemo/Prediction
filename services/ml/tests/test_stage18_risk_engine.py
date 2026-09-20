"""
Stage 18 Risk, Confidence & NO-BET Engine Test Suite

Verifies:
- Valid market with sufficient evidence (ELIGIBLE)
- Low probability/confidence handling (LOW_CONFIDENCE / NO-BET)
- High-risk conditions (HIGH_RISK / NO-BET)
- Insufficient evidence handling (INSUFFICIENT_EVIDENCE / NO-BET)
- Conflicting evidence flagging (RISK_UNRESOLVED_EVIDENCE_CONFLICT)
- Incomplete features risk flagging (RISK_MISSING_KEY_FEATURE)
- Invalid market probability handling
- Unsupported market blocking (BLOCKED / RISK_UNSUPPORTED_MARKET)
- Blocked forecast container handling (BLOCKED / RISK_BLOCKED_FORECAST_CONTAINER)
- Deterministic confidence score calculation and bounds [0, 1]
- Deterministic risk flag attachment
- Provenance preservation in provenance_summary
- Absolute absence of fabricated values, bookmaker odds, expected value edge, or Kelly sizing
"""

import unittest
from services.ml.app.markets.mapper import MarketMapper
from services.ml.app.models.base import ForecastOutput
from services.ml.app.pipeline.schemas import CurrentFeatureProvenance, CurrentMatchForecastContainer
from services.ml.app.research.schemas import FixtureVerification, ResearchState
from services.ml.app.risk.engine import RiskEngine
from services.ml.app.risk.schemas import ConfidenceLevel, DecisionStatus, RiskFlag


class TestStage18RiskEngine(unittest.TestCase):
    def setUp(self):
        self.risk_engine = RiskEngine()
        self.mapper = MarketMapper()

        self.fixture = FixtureVerification(
            fixture_id="FIX_STAGE18_TEST_001",
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
            fixture_id="FIX_STAGE18_TEST_001",
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
            container_id="FC_CONT_STAGE18_001",
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

    def test_valid_market_sufficient_evidence_eligible(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)

        self.assertGreater(report.eligible_markets_count, 0)
        dec_1x2 = report.market_decisions["MKT_1X2"]

        self.assertEqual(dec_1x2.decision_status, DecisionStatus.ELIGIBLE)
        self.assertEqual(dec_1x2.confidence_level, ConfidenceLevel.HIGH)
        self.assertGreaterEqual(dec_1x2.confidence_score, 0.70)
        self.assertEqual(dec_1x2.top_outcome_id, "1")

    def test_low_probability_low_confidence_nobet(self):
        # Create low top probability forecast (1X2 probabilities near 0.33)
        low_fc_output = ForecastOutput(
            fixture_id="FIX_LOW_001",
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
            container_id="FC_CONT_LOW_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={"FEAT_REST_DAYS_HOME": None},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="none",
            forecast_output=low_fc_output,
            validation_status="READY",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(low_container)
        risk_report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, low_container)

        dec_1x2 = risk_report.market_decisions["MKT_1X2"]
        self.assertEqual(dec_1x2.decision_status, DecisionStatus.LOW_CONFIDENCE)
        self.assertIn(RiskFlag.RISK_LOW_TOP_PROBABILITY, dec_1x2.risk_flags)

    def test_high_risk_conditions(self):
        # Forecast output with low top probability margin (0.37)
        low_fc = ForecastOutput(
            fixture_id="FIX_RISK_002",
            match_date="2025-03-20",
            model_name="EmpiricalBaselineModel",
            model_version="1.0.0",
            expected_home_goals=1.0,
            expected_away_goals=1.0,
            probabilities_1x2={"home": 0.37, "draw": 0.33, "away": 0.30},
            probabilities_totals={"over_2_5": 0.50, "under_2_5": 0.50},
            probabilities_btts={"btts_yes": 0.50, "btts_no": 0.50},
            correct_score_matrix={0: {0: 0.10}},
        )

        risk_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_RISK_002",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={"FEAT_REST_DAYS_HOME": None, "FEAT_FORM3_HOME": None},
            feature_provenance=[],
            model_name="EmpiricalBaselineModel",
            model_version="1.0.0",
            calibration_method="none",
            forecast_output=low_fc,
            validation_status="READY",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(risk_container)
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, risk_container)

        dec_1x2 = report.market_decisions["MKT_1X2"]
        self.assertIn(dec_1x2.decision_status, [DecisionStatus.HIGH_RISK, DecisionStatus.LOW_CONFIDENCE])

    def test_insufficient_evidence_nobet(self):
        # Container with 15 missing features
        missing_feats = {f"FEAT_{i}": None for i in range(15)}
        missing_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_MISSING_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector=missing_feats,
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=self.forecast_output,
            validation_status="READY",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(missing_container)
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, missing_container)

        dec_1x2 = report.market_decisions["MKT_1X2"]
        self.assertEqual(dec_1x2.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)

    def test_conflicting_evidence_flagging(self):
        conflicting_provenance = [
            CurrentFeatureProvenance(
                feature_id="FEAT_REST_DAYS_HOME",
                updated_value=7.0,
                original_historical_value=3.0,
                source_fact_id="FACT_001",
                source_name="BBC Sport",
                source_url="https://www.bbc.com/sport/rest",
                evidence_state=ResearchState.CONFLICTING,
                update_timestamp_utc="2025-03-18T10:00:00Z",
                transformation_rule="Extracted rest days",
            )
        ]

        conflict_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_CONFLICT_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={"FEAT_REST_DAYS_HOME": 7.0},
            feature_provenance=conflicting_provenance,
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=self.forecast_output,
            validation_status="READY",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(conflict_container)
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, conflict_container)

        dec_1x2 = report.market_decisions["MKT_1X2"]
        self.assertEqual(dec_1x2.decision_status, DecisionStatus.INSUFFICIENT_EVIDENCE)
        self.assertIn(RiskFlag.RISK_UNRESOLVED_EVIDENCE_CONFLICT, dec_1x2.risk_flags)

    def test_incomplete_features_risk(self):
        incomplete_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_INC_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={"FEAT_REST_DAYS_HOME": None},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=self.forecast_output,
            validation_status="READY",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(incomplete_container)
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, incomplete_container)

        dec_1x2 = report.market_decisions["MKT_1X2"]
        self.assertIn(RiskFlag.RISK_MISSING_KEY_FEATURE, dec_1x2.risk_flags)

    def test_unsupported_market_blocked(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)

        dec_handicap = report.market_decisions["MKT_ASIAN_HANDICAP"]
        self.assertEqual(dec_handicap.decision_status, DecisionStatus.BLOCKED)
        self.assertIn(RiskFlag.RISK_UNSUPPORTED_MARKET, dec_handicap.risk_flags)

    def test_blocked_forecast_container_nobet(self):
        blocked_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_BLOCKED_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            validation_status="BLOCKED_NO_FORECAST",
            blocked_reason="UNVERIFIED_FIXTURE",
        )

        mkt_report = self.mapper.map_forecast_container_to_markets(blocked_container)
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(mkt_report, blocked_container)

        self.assertEqual(report.eligible_markets_count, 0)
        for dec in report.market_decisions.values():
            self.assertEqual(dec.decision_status, DecisionStatus.BLOCKED)
            self.assertIn(RiskFlag.RISK_BLOCKED_FORECAST_CONTAINER, dec.risk_flags)

    def test_deterministic_confidence_calculation(self):
        r1 = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)
        r2 = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)

        d1 = r1.market_decisions["MKT_1X2"]
        d2 = r2.market_decisions["MKT_1X2"]

        self.assertEqual(d1.confidence_score, d2.confidence_score)
        self.assertEqual(d1.confidence_level, d2.confidence_level)
        self.assertEqual(d1.decision_status, d2.decision_status)
        self.assertGreaterEqual(d1.confidence_score, 0.0)
        self.assertLessEqual(d1.confidence_score, 1.0)

    def test_provenance_preservation(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)
        dec_1x2 = report.market_decisions["MKT_1X2"]

        self.assertEqual(dec_1x2.provenance_summary["source_container_id"], "FC_CONT_STAGE18_001")
        self.assertEqual(dec_1x2.provenance_summary["source_fixture_id"], "FIX_STAGE18_TEST_001")
        self.assertEqual(dec_1x2.provenance_summary["model_name"], "XGBoostForecaster")
        self.assertEqual(dec_1x2.provenance_summary["calibration_method"], "platt_sigmoid")

    def test_no_fabricated_values(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)
        dec_handicap = report.market_decisions["MKT_ASIAN_HANDICAP"]

        # Unsupported market has no top probability or top outcome manufactured
        self.assertIsNone(dec_handicap.top_outcome_id)
        self.assertIsNone(dec_handicap.top_probability)

    def test_no_bookmaker_odds_usage(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)
        report_dict = report.model_dump()

        self.assertNotIn("bookmaker_odds", report_dict)
        self.assertNotIn("odds", report_dict)

    def test_no_edge_value_calculation(self):
        report = self.risk_engine.evaluate_fixture_risk_and_confidence(self.market_report, self.ready_container)
        report_dict = report.model_dump()

        self.assertNotIn("expected_value", report_dict)
        self.assertNotIn("edge", report_dict)
        self.assertNotIn("kelly_stake", report_dict)
        self.assertNotIn("bankroll", report_dict)


if __name__ == "__main__":
    unittest.main()
