"""
Stage 15 Evidence Validation Test Suite

Verifies:
- Valid evidence acceptance with primary source allowlists
- Invalid URL and missing protocol rejection
- Stale timestamp detection and state downgrading
- Missing retrieval timestamp rejection
- Duplicate evidence detection and rejection
- Conflicting evidence flagging and state adjustment
- Wrong entity/fixture association rejection
- Empty claim rejection
- Full provenance preservation (source, URL, retrieval timestamp, claim, reasons)
- Deterministic audit hash generation and reproducibility
- Rejection of fabricated or converted missing data
"""

import unittest
from datetime import datetime, timezone

from services.ml.app.evidence.schemas import ValidationOutcome, ValidationReason
from services.ml.app.evidence.validator import EvidenceValidationEngine
from services.ml.app.research.engine import CurrentMatchResearchEngine
from services.ml.app.research.schemas import FactCategory, ResearchItem, ResearchState
from services.ml.app.research.verification import FixtureVerifier


class TestStage15EvidenceValidation(unittest.TestCase):
    def setUp(self):
        self.verifier = FixtureVerifier()
        self.research_engine = CurrentMatchResearchEngine()
        self.validator = EvidenceValidationEngine()

        self.fixture = self.verifier.verify_fixture(
            fixture_id="FIX_STAGE15_001",
            home_team="Man Utd",
            away_team="Arsenal",
            competition="EPL",
            season="20242025",
            match_date="2025-03-20",
            kickoff_time="20:00",
            venue="Old Trafford",
        )

    def test_valid_evidence_acceptance(self):
        raw_inputs = [
            {
                "claim": "Lisandro Martinez is OUT injured with knee surgery.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/martinez",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "INJURIES",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Manchester United", "Lisandro Martinez"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.accepted_count, 1)
        self.assertEqual(val_report.rejected_count, 0)

        item = val_report.validated_items[0]
        self.assertEqual(item.validation_outcome, ValidationOutcome.ACCEPTED)
        self.assertIn(ValidationReason.VALID_PRIMARY_SOURCE, item.validation_reasons)

    def test_invalid_source_and_unallowlisted_domain(self):
        raw_inputs = [
            {
                "claim": "Unverified rumor from unofficial fan site.",
                "source_name": "Fan Forum",
                "source_url": "https://www.unverifiedfanblog.com/post/123",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "TEAM_NEWS",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Arsenal"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.downgraded_count, 1)
        item = val_report.validated_items[0]
        self.assertEqual(item.validation_outcome, ValidationOutcome.DOWNGRADED)
        self.assertIn(ValidationReason.UNALLOWLISTED_SOURCE, item.validation_reasons)
        self.assertEqual(item.adjusted_research_state, ResearchState.LIKELY)

    def test_invalid_url_rejection(self):
        item = ResearchItem(
            fact_id="FACT_INVALID_URL",
            category=FactCategory.TEAM_NEWS,
            claim="Valid claim text with invalid URL format.",
            source_name="Source",
            source_url="ftp://invalid-url-schema.com",
            retrieval_timestamp_utc="2025-03-18T10:00:00Z",
            research_state=ResearchState.VERIFIED,
        )
        val_item = self.validator.validate_item(item, self.fixture, seen_claims=set())

        self.assertEqual(val_item.validation_outcome, ValidationOutcome.REJECTED)
        self.assertIn(ValidationReason.INVALID_URL, val_item.validation_reasons)

    def test_stale_evidence_detection(self):
        raw_inputs = [
            {
                "claim": "Old injury update from 6 months ago.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/old-news",
                "retrieval_timestamp_utc": "2024-09-01T10:00:00Z",  # Stale relative to 2025-03-20
                "category": "INJURIES",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Arsenal"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.downgraded_count, 1)
        item = val_report.validated_items[0]
        self.assertEqual(item.validation_outcome, ValidationOutcome.DOWNGRADED)
        self.assertIn(ValidationReason.STALE_TIMESTAMP, item.validation_reasons)
        self.assertEqual(item.adjusted_research_state, ResearchState.UNCERTAIN)

    def test_missing_timestamp_rejection(self):
        item = ResearchItem(
            fact_id="FACT_NO_TS",
            category=FactCategory.TEAM_NEWS,
            claim="Claim without timestamp.",
            source_name="BBC Sport",
            source_url="https://www.bbc.com/sport/news",
            retrieval_timestamp_utc="",
            research_state=ResearchState.VERIFIED,
        )
        val_item = self.validator.validate_item(item, self.fixture, seen_claims=set())
        self.assertEqual(val_item.validation_outcome, ValidationOutcome.REJECTED)
        self.assertIn(ValidationReason.MISSING_TIMESTAMP, val_item.validation_reasons)

    def test_duplicate_evidence_rejection(self):
        raw_inputs = [
            {
                "claim": "Lisandro Martinez is OUT injured with knee surgery.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/football/martinez1",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "INJURIES",
                "canonical_entities_mentioned": ["Manchester United"],
            },
            {
                "claim": "Lisandro Martinez is OUT injured with knee surgery.",  # Exact duplicate
                "source_name": "Sky Sports",
                "source_url": "https://www.skysports.com/football/martinez2",
                "retrieval_timestamp_utc": "2025-03-18T11:00:00Z",
                "category": "INJURIES",
                "canonical_entities_mentioned": ["Manchester United"],
            },
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.accepted_count, 1)
        self.assertEqual(val_report.rejected_count, 1)
        self.assertIn(ValidationReason.DUPLICATE_EVIDENCE, val_report.rejected_items[0].validation_reasons)

    def test_conflicting_evidence_flagging(self):
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
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.conflicting_count, 2)
        for item in val_report.validated_items:
            self.assertEqual(item.validation_outcome, ValidationOutcome.FLAGGED_CONFLICT)
            self.assertEqual(item.adjusted_research_state, ResearchState.CONFLICTING)

    def test_wrong_fixture_or_entity_association(self):
        raw_inputs = [
            {
                "claim": "Kylian Mbappe scored 2 goals for Real Madrid in La Liga.",
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/mbappe",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "TEAM_NEWS",
                "canonical_entities_mentioned": ["Kylian Mbappe", "Real Madrid"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.rejected_count, 1)
        self.assertIn(ValidationReason.WRONG_ENTITY_ASSOCIATION, val_report.rejected_items[0].validation_reasons)

    def test_unsupported_or_empty_claim(self):
        raw_inputs = [
            {
                "claim": "   ",  # Whitespace only
                "source_name": "BBC Sport",
                "source_url": "https://www.bbc.com/sport/empty",
                "retrieval_timestamp_utc": "2025-03-18T10:00:00Z",
                "category": "TEAM_NEWS",
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        self.assertEqual(val_report.total_evaluated, 0)  # Filtered out by research engine parser

    def test_preservation_of_full_provenance(self):
        raw_inputs = [
            {
                "claim": "Arsenal squad arrived at Manchester airport.",
                "source_name": "The Guardian",
                "source_url": "https://www.theguardian.com/sport/arsenal-travel",
                "retrieval_timestamp_utc": "2025-03-19T14:00:00Z",
                "publication_timestamp_utc": "2025-03-19T13:30:00Z",
                "category": "TRAVEL_CONTEXT",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Arsenal"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)
        val_report = self.validator.validate_research_report(report)

        item = val_report.validated_items[0]
        self.assertEqual(item.source_name, "The Guardian")
        self.assertEqual(item.source_url, "https://www.theguardian.com/sport/arsenal-travel")
        self.assertEqual(item.retrieval_timestamp_utc, "2025-03-19T14:00:00Z")
        self.assertEqual(item.publication_timestamp_utc, "2025-03-19T13:30:00Z")
        self.assertEqual(item.claim, "Arsenal squad arrived at Manchester airport.")

    def test_deterministic_and_auditable_validation(self):
        raw_inputs = [
            {
                "claim": "Confirmed lineup includes Declan Rice in midfield.",
                "source_name": "Opta Sports",
                "source_url": "https://www.opta.com/arsenal/lineup",
                "retrieval_timestamp_utc": "2025-03-19T18:00:00Z",
                "category": "CONFIRMED_LINEUPS",
                "research_state": "VERIFIED",
                "canonical_entities_mentioned": ["Arsenal", "Declan Rice"],
            }
        ]
        report = self.research_engine.research_fixture(self.fixture, raw_inputs)

        val_report1 = self.validator.validate_research_report(report)
        val_report2 = self.validator.validate_research_report(report)

        self.assertEqual(val_report1.audit_trail_hash, val_report2.audit_trail_hash)
        self.assertTrue(len(val_report1.audit_trail_hash) == 64)

    def test_rejection_of_fabricated_data(self):
        item = ResearchItem(
            fact_id="FACT_UNCERTAIN",
            category=FactCategory.TACTICAL_CHANGES,
            claim="Unconfirmed tactical speculation.",
            source_name="Unverified Blog",
            source_url="https://www.unverified.com/blog",
            retrieval_timestamp_utc="2025-03-18T10:00:00Z",
            research_state=ResearchState.UNCERTAIN,
        )
        val_item = self.validator.validate_item(item, self.fixture, seen_claims=set())

        # Assert validator never upgrades UNCERTAIN to VERIFIED
        self.assertNotEqual(val_item.adjusted_research_state, ResearchState.VERIFIED)


if __name__ == "__main__":
    unittest.main()
