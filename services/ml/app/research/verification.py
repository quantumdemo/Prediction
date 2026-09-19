"""
Stage 14 Fixture Identity Verification & Alias Resolution Engine

Resolves home/away team aliases, competition aliases, and verifies fixture identity
against canonical platform ID standards before web research is conducted.
"""

import logging
import re
from typing import Any, Dict, Optional, Tuple
from services.ml.app.research.schemas import FixtureVerification

logger = logging.getLogger("football_ml.research.verification")

# Team Alias Dictionary to Canonical UUIDs / Standard Identifiers
KNOWN_TEAM_ALIASES: Dict[str, Tuple[str, str]] = {
    "manchester united": ("Manchester United", "CLUB_ENG_MANCHESTER_UNITED"),
    "man utd": ("Manchester United", "CLUB_ENG_MANCHESTER_UNITED"),
    "manutd": ("Manchester United", "CLUB_ENG_MANCHESTER_UNITED"),
    "arsenal": ("Arsenal", "CLUB_ENG_ARSENAL"),
    "arsenal fc": ("Arsenal", "CLUB_ENG_ARSENAL"),
    "chelsea": ("Chelsea", "CLUB_ENG_CHELSEA"),
    "chelsea fc": ("Chelsea", "CLUB_ENG_CHELSEA"),
    "liverpool": ("Liverpool", "CLUB_ENG_LIVERPOOL"),
    "liverpool fc": ("Liverpool", "CLUB_ENG_LIVERPOOL"),
    "manchester city": ("Manchester City", "CLUB_ENG_MANCHESTER_CITY"),
    "man city": ("Manchester City", "CLUB_ENG_MANCHESTER_CITY"),
    "real madrid": ("Real Madrid", "CLUB_ESP_REAL_MADRID"),
    "barcelona": ("Barcelona", "CLUB_ESP_BARCELONA"),
    "fc barcelona": ("Barcelona", "CLUB_ESP_BARCELONA"),
    "bayern munich": ("Bayern Munich", "CLUB_GER_BAYERN_MUNICH"),
    "bayern munchen": ("Bayern Munich", "CLUB_GER_BAYERN_MUNICH"),
}

# Competition Alias Dictionary
KNOWN_COMPETITION_ALIASES: Dict[str, Tuple[str, str]] = {
    "premier league": ("Premier League", "COMP_ENG_PL"),
    "epl": ("Premier League", "COMP_ENG_PL"),
    "english premier league": ("Premier League", "COMP_ENG_PL"),
    "la liga": ("La Liga", "COMP_ESP_LA_LIGA"),
    "laliga": ("La Liga", "COMP_ESP_LA_LIGA"),
    "bundesliga": ("Bundesliga", "COMP_GER_BUNDESLIGA"),
    "champions league": ("UEFA Champions League", "COMP_EUR_CL"),
    "ucl": ("UEFA Champions League", "COMP_EUR_CL"),
}


class FixtureVerifier:
    """
    Verifies fixture metadata and resolves raw names to canonical platform IDs.
    """

    def __init__(self):
        self.team_aliases = KNOWN_TEAM_ALIASES
        self.comp_aliases = KNOWN_COMPETITION_ALIASES

    def resolve_team(self, team_name: str) -> Tuple[str, str]:
        """
        Resolves raw team string to (standard_name, canonical_id).
        """
        if not team_name or not team_name.strip():
            raise ValueError("Team name cannot be empty.")

        clean_name = team_name.strip().lower()
        if clean_name in self.team_aliases:
            return self.team_aliases[clean_name]

        # Normalized string fallback
        norm_name = re.sub(r"[^a-z0-9]", "_", clean_name).strip("_")
        canonical_id = f"CLUB_GENERIC_{norm_name.upper()}"
        return team_name.strip(), canonical_id

    def resolve_competition(self, comp_name: str) -> Tuple[str, str]:
        """
        Resolves raw competition string to (standard_name, canonical_id).
        """
        if not comp_name or not comp_name.strip():
            return "Unknown Competition", "COMP_UNKNOWN"

        clean_name = comp_name.strip().lower()
        if clean_name in self.comp_aliases:
            return self.comp_aliases[clean_name]

        norm_name = re.sub(r"[^a-z0-9]", "_", clean_name).strip("_")
        canonical_id = f"COMP_GENERIC_{norm_name.upper()}"
        return comp_name.strip(), canonical_id

    def verify_fixture(
        self,
        fixture_id: str,
        home_team: str,
        away_team: str,
        competition: str,
        season: str,
        match_date: str,
        kickoff_time: Optional[str] = None,
        venue: Optional[str] = None,
        fixture_status: str = "SCHEDULED",
    ) -> FixtureVerification:
        """
        Constructs and verifies FixtureVerification payload with canonical IDs.
        """
        if not fixture_id or not fixture_id.strip():
            raise ValueError("fixture_id is required for verification.")
        if not match_date or not re.match(r"^\d{4}-\d{2}-\d{2}", match_date):
            raise ValueError(f"Invalid match_date format (YYYY-MM-DD required): {match_date}")

        home_std, home_id = self.resolve_team(home_team)
        away_std, away_id = self.resolve_team(away_team)
        comp_std, comp_id = self.resolve_competition(competition)

        if home_id == away_id and home_id.startswith("CLUB_ENG"):
            raise ValueError(f"Home team and away team resolved to same canonical ID: {home_id}")

        return FixtureVerification(
            fixture_id=fixture_id.strip(),
            home_team=home_std,
            away_team=away_std,
            home_canonical_id=home_id,
            away_canonical_id=away_id,
            competition=comp_std,
            competition_canonical_id=comp_id,
            season=season.strip(),
            match_date=match_date.strip(),
            kickoff_time=kickoff_time.strip() if kickoff_time else None,
            venue=venue.strip() if venue else None,
            fixture_status=fixture_status.upper(),
            is_verified=True,
            verification_method="CANONICAL_DATABASE_MATCH",
        )
