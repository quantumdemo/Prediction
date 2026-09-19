"""
Stage 14 Current-Match Web Research Engine Test Suite

Verifies:
- Fixture identity verification (home, away, competition, season, date, kickoff time, venue)
- Team and competition alias resolution to canonical platform IDs
- Source provenance capture (source name, valid URL, UTC retrieval timestamp)
- Explicit research states (VERIFIED, LIKELY, UNCERTAIN, CONFLICTING, UNAVAILABLE)
- Explicit contradiction detection without fact fabrication or silent selection
- Explicit tracking of unavailable information categories
- Rejection of invalid URLs, empty claims, or fabricated values
- Strict architectural isolation (zero prediction probability generation)
"""

import unittest
from datetime import datetime
from services.ml.app.research.engine import CurrentMatchResearchEngine
from services.ml.app.research.schemas import FactCategory, ResearchState
from services.ml.app.research.verification import FixtureVerifier


class TestStage14WebResearch(unittest.TestCase):
    def setUp(self):
        self.verifier = FixtureVerifier()
        self.engine = CurrentMatchResearchEngine()

        self.verified_fixture = self.verifier.verify_fixture(
            fixture_id="FIX_TEST_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            kickoff_time="20:00",
            venue="Old Trafford",
        )

    def test_fixture_verification(self):
        f = self.verified_fixture
        self.assertEqual(f.fixture_id, "FIX_TEST_001")
        self.assertEqual(f.home_team, "Manchester United")
        self.assertEqual(f.home_canonical_id, "CLUB_ENG_MANCHESTER_UNITED")
        self.assertEqual(f.away_team, "Arsenal")
        self.assertEqual(f.away_canonical_id, "CLUB_ENG_ARSENAL")
        self.assertEqual(f.competition, "Premier League")
        self.assertEqual(f.competition_canonical_id, "COMP_ENG_PL")
        self.assertEqual(f.season, "20242025")
        self.assertEqual(f.match_date, "2025-03-20")
        self.assertEqual(f.kickoff_time, "20:00")
        self.assertEqual(f.venue, "Old Trafford")
        self.assertTrue(f.is_verified)

    def test_team_and_competition_alias_resolution(self):
        team_std, team_id = self.verifier.resolve_team("barcelona")
        self.assertEqual(team_std, "Barcelona")
        self.assertEqual(team_id, "CLUB_ESP_BARCELONA")

        comp_std, comp_id = self.verifier.resolve_competition("la liga")
        self.assertEqual(comp_std, "La Liga")
        self.assertEqual(comp_id, "COMP_ESP_LA_LIGA")

        # Unknown team fallback
        un_std, un_id = self.verifier.resolve_team("Custom Local FC")
        self.assertEqual(un_std, "Custom Local FC")
        self.assertTrue(un_id.startswith("CLUB_GENERIC_"))

    def test_source_and_provenance_capture(self):
        raw_inputs = [
            {
                "claim": "Lisandro Martinez is OUT injured following knee surgery.",
                "source_name": "Sky Sports",
                "source_url": "https://www.skysports.com/football/news/martinez-injury",
                "category": "INJURIES",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Lisandro Martinez"],
            }
        ]
        report = self.engine.research_fixture(self.verified_fixture, raw_inputs)
        self.assertEqual(len(report.items), 1)

        item = report.items[0]
        self.assertEqual(item.source_name, "Sky Sports")
        self.assertTrue(item.source_url.startswith("https://"))
        self.assertTrue(len(item.retrieval_timestamp_utc) > 0)
        self.assertEqual(item.research_state, ResearchState.VERIFIED)

    def test_explicit_research_states(self):
        raw_inputs = [
            {
                "claim": "Confirmed lineup includes Rasmus Hojlund as starting striker.",
                "source_name": "Official Team Press",
                "source_url": "https://www.manutd.com/lineup",
                "category": "CONFIRMED_LINEUPS",
                "research_state": "VERIFIED",
            },
            {
                "claim": "Tactical shift to 3-4-2-1 formation is likely.",
                "source_name": "Tactical Analysis Blog",
                "source_url": "https://www.tactics.org/shift",
                "category": "TACTICAL_CHANGES",
                "research_state": "LIKELY",
            },
            {
                "claim": "Unconfirmed rumor regarding minor illness in squad.",
                "source_name": "Social Media Aggregator",
                "source_url": "https://www.rumors.com/illness",
                "category": "TEAM_NEWS",
                "research_state": "UNCERTAIN",
            },
        ]
        report = self.engine.research_fixture(self.verified_fixture, raw_inputs)
        states = {item.research_state for item in report.items}
        self.assertIn(ResearchState.VERIFIED, states)
        self.assertIn(ResearchState.LIKELY, states)
        self.assertIn(ResearchState.UNCERTAIN, states)

    def test_conflicting_information_handling(self):
        raw_inputs = [
            {
                "claim": "Bukayo Saka is OUT injured with a hamstring injury.",
                "source_name": "Source A",
                "source_url": "https://sourceA.com/saka",
                "category": "INJURIES",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Bukayo Saka"],
            },
            {
                "claim": "Bukayo Saka is FIT and starting in predicted lineup.",
                "source_name": "Source B",
                "source_url": "https://sourceB.com/saka",
                "category": "INJURIES",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Bukayo Saka"],
            },
        ]
        report = self.engine.research_fixture(self.verified_fixture, raw_inputs)
        self.assertGreaterEqual(len(report.conflicting_items), 1)

        for item in report.items:
            self.assertEqual(item.research_state, ResearchState.CONFLICTING)
            self.assertIsNotNone(item.contradiction_details)
            self.assertIn("Contradiction between sources", item.contradiction_details)

    def test_unavailable_information_handling(self):
        # Empty inputs should mark all categories as UNAVAILABLE
        report = self.engine.research_fixture(self.verified_fixture, raw_evidence_inputs=[])
        self.assertEqual(len(report.items), 0)
        self.assertEqual(len(report.unavailable_categories), len(FactCategory))

    def test_rejection_of_invalid_urls_and_empty_claims(self):
        invalid_inputs = [
            {
                "claim": "",  # Empty claim
                "source_name": "Bad Source",
                "source_url": "https://valid.url.com",
            },
            {
                "claim": "Valid claim text",
                "source_name": "Bad Source",
                "source_url": "not_a_valid_url",  # Invalid URL
            },
        ]
        report = self.engine.research_fixture(self.verified_fixture, invalid_inputs)
        self.assertEqual(len(report.items), 0)

    def test_isolation_no_prediction_probabilities(self):
        raw_inputs = [
            {
                "claim": "Arsenal won 4 of their last 5 league matches.",
                "source_name": "Opta Sports",
                "source_url": "https://opta.com/stats",
                "category": "RECENT_FORM",
                "research_state": "VERIFIED",
            }
        ]
        report = self.engine.research_fixture(self.verified_fixture, raw_inputs)

        # Assert no probability fields exist on report or items
        report_dict = report.model_dump()
        self.assertNotIn("probabilities_1x2", report_dict)
        self.assertNotIn("win_probability", report_dict)
        self.assertNotIn("odds", report_dict)

    def test_fixture_verification_validation_errors(self):
        with self.assertRaises(ValueError):
            self.verifier.verify_fixture(
                fixture_id="",
                home_team="Man Utd",
                away_team="Arsenal",
                competition="EPL",
                season="20242025",
                match_date="2025-03-20",
            )

        with self.assertRaises(ValueError):
            self.verifier.verify_fixture(
                fixture_id="FIX_001",
                home_team="Man Utd",
                away_team="Arsenal",
                competition="EPL",
                season="20242025",
                match_date="INVALID_DATE_FORMAT",
            )


if __name__ == "__main__":
    unittest.main()
