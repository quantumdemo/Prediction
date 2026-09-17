"""
Stage 8 Competition, Season, and Club-Season Membership Resolver Engine

Maps source division codes (e.g. E0, SP1, I1) to canonical competitions,
derives stable season identities, and tracks club-season participation relationships.
"""

import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class CanonicalCompetitionEntity:
    id: str
    code: str
    name: str
    country_code: str
    competition_type: str = "LEAGUE"


@dataclass
class CanonicalSeasonEntity:
    id: str
    competition_id: str
    label: str  # e.g. 2024/25
    is_current: bool = False


DIVISION_TO_COMPETITION_MAP = {
    "E0": ("EPL", "English Premier League", "ENG"),
    "E1": ("EFL_CHAMP", "EFL Championship", "ENG"),
    "E2": ("EFL_LEAGUE1", "EFL League One", "ENG"),
    "E3": ("EFL_LEAGUE2", "EFL League Two", "ENG"),
    "SP1": ("LALIGA", "La Liga Primera Division", "ESP"),
    "SP2": ("LALIGA2", "La Liga Segunda Division", "ESP"),
    "I1": ("SERIEA", "Serie A", "ITA"),
    "I2": ("SERIEB", "Serie B", "ITA"),
    "D1": ("BUNDESLIGA", "Bundesliga", "GER"),
    "D2": ("BUNDESLIGA2", "2. Bundesliga", "GER"),
    "F1": ("LIGUE1", "Ligue 1", "FRA"),
    "F2": ("LIGUE2", "Ligue 2", "FRA"),
    "N1": ("EREDIVISIE", "Eredivisie", "NED"),
    "B1": ("PRO_LEAGUE", "Belgian Pro League", "BEL"),
    "P1": ("PRIMEIRA_LIGA", "Primeira Liga", "POR"),
    "T1": ("SUPER_LIG", "Super Lig", "TUR"),
    "G1": ("SUPER_LEAGUE_GR", "Super League Greece", "GRE"),
    "SC0": ("SCOT_PREM", "Scottish Premiership", "SCO"),
}


class CompetitionSeasonResolver:
    """
    Resolves source division codes and match seasons into canonical entities and memberships.
    """

    def __init__(self):
        self.competitions: Dict[str, CanonicalCompetitionEntity] = {}
        self.seasons: Dict[Tuple[str, str], CanonicalSeasonEntity] = {}  # (comp_id, season_label) -> CanonicalSeason
        self.club_season_memberships: Set[Tuple[str, str, str]] = set()  # (club_id, comp_id, season_id)

    def resolve_competition(self, source_division_code: str) -> Optional[CanonicalCompetitionEntity]:
        if source_division_code not in DIVISION_TO_COMPETITION_MAP:
            # Fallback for general country divisions
            comp_code = source_division_code.upper()
            country_code = source_division_code[:3].upper() if len(source_division_code) >= 3 else "UN"
            comp_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"comp:{comp_code}"))
            comp = CanonicalCompetitionEntity(
                id=comp_id, code=comp_code, name=f"Division {comp_code}", country_code=country_code
            )
            self.competitions[comp_code] = comp
            return comp

        comp_code, comp_name, country_code = DIVISION_TO_COMPETITION_MAP[source_division_code]
        comp_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"comp:{comp_code}"))

        if comp_code not in self.competitions:
            comp = CanonicalCompetitionEntity(
                id=comp_id, code=comp_code, name=comp_name, country_code=country_code
            )
            self.competitions[comp_code] = comp
            return comp

        return self.competitions[comp_code]

    def resolve_season(self, competition_id: str, season_label: str) -> CanonicalSeasonEntity:
        key = (competition_id, season_label)
        if key in self.seasons:
            return self.seasons[key]

        season_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"season:{competition_id}:{season_label}"))
        season = CanonicalSeasonEntity(
            id=season_id,
            competition_id=competition_id,
            label=season_label,
            is_current=(season_label == "2024/25"),
        )
        self.seasons[key] = season
        return season

    def register_club_season_membership(self, club_id: str, competition_id: str, season_id: str):
        self.club_season_memberships.add((club_id, competition_id, season_id))
