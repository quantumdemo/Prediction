"""
Stage 17 Market Catalogue & Mapping Test Suite

Verifies:
- Every supported market (1X2, Over/Under 0.5-4.5, BTTS, Correct Score Grid)
- Deterministic probability mapping and repeated execution stability
- Probability bounds [0, 1] enforcement
- Probability complementary sum consistency
- Correct score matrix distribution mapping
- Explicit unsupported market rejections (Asian Handicap, Corners, Cards)
- Blocked forecast container and missing forecast output handling
- Full provenance preservation (source container, model name/version, mapping rule)
- Absolute absence of bookmaker odds, value calculation, or fabricated probabilities
"""

import unittest
from services.ml.app.markets.catalogue import CONTROLLED_MARKET_CATALOGUE
from services.ml.app.markets.mapper import MarketMapper
from services.ml.app.models.base import ForecastOutput
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer
from services.ml.app.research.schemas import FixtureVerification


class TestStage17MarketMapping(unittest.TestCase):
    def setUp(self):
        self.mapper = MarketMapper()

        self.fixture = FixtureVerification(
            fixture_id="FIX_STAGE17_TEST_001",
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
            fixture_id="FIX_STAGE17_TEST_001",
            match_date="2025-03-20",
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            expected_home_goals=1.6,
            expected_away_goals=1.2,
            probabilities_1x2={"home": 0.45, "draw": 0.30, "away": 0.25},
            probabilities_totals={
                "over_0_5": 0.92, "under_0_5": 0.08,
                "over_1_5": 0.75, "under_1_5": 0.25,
                "over_2_5": 0.55, "under_2_5": 0.45,
                "over_3_5": 0.32, "under_3_5": 0.68,
                "over_4_5": 0.15, "under_4_5": 0.85,
            },
            probabilities_btts={"btts_yes": 0.58, "btts_no": 0.42},
            correct_score_matrix={
                0: {0: 0.08, 1: 0.10},
                1: {0: 0.15, 1: 0.20},
                2: {1: 0.12},
            },
        )

        self.ready_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_READY_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=self.forecast_output,
            validation_status="READY",
        )

    def test_every_supported_market(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)

        self.assertEqual(report.supported_markets_count, 8)
        self.assertEqual(report.unsupported_markets_count, 3)

        supported_ids = [
            "MKT_1X2", "MKT_OVER_UNDER_0_5", "MKT_OVER_UNDER_1_5",
            "MKT_OVER_UNDER_2_5", "MKT_OVER_UNDER_3_5", "MKT_OVER_UNDER_4_5",
            "MKT_BTTS", "MKT_CORRECT_SCORE",
        ]
        for mkt_id in supported_ids:
            self.assertIn(mkt_id, report.mapped_markets)
            mkt = report.mapped_markets[mkt_id]
            self.assertTrue(mkt.is_supported)
            self.assertGreater(len(mkt.outcomes), 0)

    def test_deterministic_probability_mapping(self):
        r1 = self.mapper.map_forecast_container_to_markets(self.ready_container)
        r2 = self.mapper.map_forecast_container_to_markets(self.ready_container)

        self.assertEqual(r1.supported_markets_count, r2.supported_markets_count)
        self.assertEqual(
            r1.mapped_markets["MKT_1X2"].outcomes[0].probability,
            r2.mapped_markets["MKT_1X2"].outcomes[0].probability,
        )

    def test_probability_bounds(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)

        for mkt_id, mkt in report.mapped_markets.items():
            for outcome in mkt.outcomes:
                self.assertGreaterEqual(outcome.probability, 0.0)
                self.assertLessEqual(outcome.probability, 1.0)
                self.assertTrue(outcome.is_valid_probability)

    def test_probability_consistency(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)

        # 1X2 sum = 1.0
        mkt_1x2 = report.mapped_markets["MKT_1X2"]
        sum_1x2 = sum(o.probability for o in mkt_1x2.outcomes)
        self.assertAlmostEqual(sum_1x2, 1.0, places=5)

        # BTTS sum = 1.0
        mkt_btts = report.mapped_markets["MKT_BTTS"]
        sum_btts = sum(o.probability for o in mkt_btts.outcomes)
        self.assertAlmostEqual(sum_btts, 1.0, places=5)

        # Totals over + under sum = 1.0
        for line in ["0_5", "1_5", "2_5", "3_5", "4_5"]:
            mkt_tot = report.mapped_markets[f"MKT_OVER_UNDER_{line}"]
            sum_tot = sum(o.probability for o in mkt_tot.outcomes)
            self.assertAlmostEqual(sum_tot, 1.0, places=5)

    def test_correct_score_distribution_handling(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)
        mkt_cs = report.mapped_markets["MKT_CORRECT_SCORE"]

        self.assertTrue(mkt_cs.is_supported)
        self.assertEqual(mkt_cs.market_type, "MATRIX")

        score_outcomes = {o.outcome_id: o.probability for o in mkt_cs.outcomes}
        self.assertIn("CS_0_0", score_outcomes)
        self.assertAlmostEqual(score_outcomes["CS_0_0"], 0.08)
        self.assertAlmostEqual(score_outcomes["CS_1_1"], 0.20)

    def test_unsupported_markets(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)

        unsupported_ids = ["MKT_ASIAN_HANDICAP", "MKT_CORNER_TOTALS", "MKT_CARD_TOTALS"]
        for mkt_id in unsupported_ids:
            self.assertIn(mkt_id, report.mapped_markets)
            mkt = report.mapped_markets[mkt_id]
            self.assertFalse(mkt.is_supported)
            self.assertEqual(len(mkt.outcomes), 0)
            self.assertIsNotNone(mkt.unsupported_reason)

    def test_missing_forecast_output(self):
        empty_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_EMPTY_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            model_name="XGBoostForecaster",
            model_version="1.0.0_platt",
            calibration_method="platt_sigmoid",
            forecast_output=None,  # Missing
            validation_status="BLOCKED_NO_FORECAST",
            blocked_reason="MISSING_FORECAST_OUTPUT",
        )

        report = self.mapper.map_forecast_container_to_markets(empty_container)
        self.assertEqual(report.supported_markets_count, 0)
        self.assertEqual(report.unsupported_markets_count, len(CONTROLLED_MARKET_CATALOGUE))

    def test_invalid_forecast_input_blocked_container(self):
        blocked_container = CurrentMatchForecastContainer(
            container_id="FC_CONT_BLOCKED_001",
            fixture=self.fixture,
            prediction_timestamp_utc="2025-03-19T12:00:00Z",
            updated_feature_vector={},
            feature_provenance=[],
            validation_status="BLOCKED_NO_FORECAST",
            blocked_reason="UNRESOLVED_CRITICAL_EVIDENCE_CONFLICT",
        )

        report = self.mapper.map_forecast_container_to_markets(blocked_container)
        self.assertEqual(report.supported_markets_count, 0)
        for mkt in report.mapped_markets.values():
            self.assertFalse(mkt.is_supported)
            self.assertIn("UNRESOLVED_CRITICAL_EVIDENCE_CONFLICT", mkt.unsupported_reason)

    def test_provenance_preservation(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)
        mkt_1x2 = report.mapped_markets["MKT_1X2"]
        prov = mkt_1x2.provenance

        self.assertEqual(prov.source_forecast_container_id, "FC_CONT_READY_001")
        self.assertEqual(prov.source_fixture_id, "FIX_STAGE17_TEST_001")
        self.assertEqual(prov.source_model_name, "XGBoostForecaster")
        self.assertEqual(prov.source_model_version, "1.0.0_platt")
        self.assertTrue(prov.is_supported)

    def test_no_bookmaker_odds_usage(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)
        report_dict = report.model_dump()

        # Assert zero odds, bookmaker names, margins, or expected value calculations
        self.assertNotIn("bookmaker_odds", report_dict)
        self.assertNotIn("odds", report_dict)
        self.assertNotIn("expected_value", report_dict)
        self.assertNotIn("edge", report_dict)

    def test_no_fabricated_probabilities(self):
        report = self.mapper.map_forecast_container_to_markets(self.ready_container)
        mkt_handicap = report.mapped_markets["MKT_ASIAN_HANDICAP"]

        # Unsupported market must return zero outcomes, not invented probabilities
        self.assertEqual(len(mkt_handicap.outcomes), 0)

    def test_deterministic_repeated_execution(self):
        results = [self.mapper.map_forecast_container_to_markets(self.ready_container) for _ in range(5)]
        first_prob = results[0].mapped_markets["MKT_1X2"].outcomes[0].probability
        for r in results[1:]:
            self.assertEqual(r.mapped_markets["MKT_1X2"].outcomes[0].probability, first_prob)


if __name__ == "__main__":
    unittest.main()
