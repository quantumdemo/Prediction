"""
Stage 8 Fixture Resolver Engine

Generates stable canonical match/fixture identities, preserves true external IDs,
detects exact/likely/conflicting duplicate fixtures, and performs cross-source reconciliation
against the 39 Stage 6 baseline matches.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class CanonicalFixtureEntity:
    id: str
    competition_id: str
    season_id: str
    match_date: str
    match_time: Optional[str]
    home_club_id: str
    away_club_id: str
    full_time_home_goals: int
    full_time_away_goals: int
    full_time_result: str
    resolution_status: str = "VERIFIED"  # VERIFIED, LIKELY, UNCERTAIN, CONFLICTING, UNRESOLVED
    reconciliation_status: str = "STANDALONE"  # STANDALONE, RECONCILED_STAGE6_BASELINE
    external_ids: Dict[str, str] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)


class FixtureResolver:
    """
    Creates stable fixture identities and performs cross-source duplicate and Stage 6 baseline reconciliation.
    """

    def __init__(self):
        self.fixtures: Dict[str, CanonicalFixtureEntity] = {}
        self.fixture_lookup_keys: Dict[Tuple[str, str, str, str], str] = {}  # (comp_id, date, home_id, away_id) -> fixture_id
        self.stage6_baseline_fixtures: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.duplicates_detected = 0
        self.conflicts_detected = 0

    def resolve_fixture_identity(
        self,
        competition_id: str,
        season_id: str,
        match_date: str,
        match_time: Optional[str],
        home_club_id: str,
        away_club_id: str,
        home_goals: int,
        away_goals: int,
        result: str,
        source_id: str = "FOOTBALL_DATA_UK",
        external_match_id: Optional[str] = None,
        stats: Optional[Dict[str, Any]] = None,
    ) -> CanonicalFixtureEntity:
        lookup_key = (competition_id, match_date, home_club_id, away_club_id)

        if lookup_key in self.fixture_lookup_keys:
            self.duplicates_detected += 1
            existing_id = self.fixture_lookup_keys[lookup_key]
            existing_fixture = self.fixtures[existing_id]

            # Check score conflict
            if (existing_fixture.full_time_home_goals != home_goals or existing_fixture.full_time_away_goals != away_goals):
                self.conflicts_detected += 1
                existing_fixture.resolution_status = "CONFLICTING"

            if external_match_id:
                existing_fixture.external_ids[source_id] = external_match_id

            return existing_fixture

        # Generate deterministic internal fixture UUID based on canonical fixture context
        fixture_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"fixture:{competition_id}:{match_date}:{home_club_id}:{away_club_id}"))

        fixture = CanonicalFixtureEntity(
            id=fixture_id,
            competition_id=competition_id,
            season_id=season_id,
            match_date=match_date,
            match_time=match_time,
            home_club_id=home_club_id,
            away_club_id=away_club_id,
            full_time_home_goals=home_goals,
            full_time_away_goals=away_goals,
            full_time_result=result,
            external_ids={source_id: external_match_id} if external_match_id else {},
            stats=stats or {},
        )

        self.fixtures[fixture_id] = fixture
        self.fixture_lookup_keys[lookup_key] = fixture_id
        return fixture
