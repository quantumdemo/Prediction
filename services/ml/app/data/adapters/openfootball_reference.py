import logging
from typing import Any, Dict, List

from services.ml.app.data.adapters.base import BaseAcquisitionAdapter

logger = logging.getLogger("football_ml.data.adapters.openfootball")

OPENFOOTBALL_CLUB_REFERENCES = [
    {
        "canonical_name": "Arsenal FC",
        "short_name": "Arsenal",
        "country_code": "ENG",
        "city": "London",
        "aliases": ["Arsenal", "Gunners", "Arsenal London"],
    },
    {
        "canonical_name": "Chelsea FC",
        "short_name": "Chelsea",
        "country_code": "ENG",
        "city": "London",
        "aliases": ["Chelsea", "Blues"],
    },
    {
        "canonical_name": "Liverpool FC",
        "short_name": "Liverpool",
        "country_code": "ENG",
        "city": "Liverpool",
        "aliases": ["Liverpool", "Reds"],
    },
    {
        "canonical_name": "Manchester United FC",
        "short_name": "Man United",
        "country_code": "ENG",
        "city": "Manchester",
        "aliases": ["Man United", "Man Utd", "Manchester Utd"],
    },
    {
        "canonical_name": "Manchester City FC",
        "short_name": "Man City",
        "country_code": "ENG",
        "city": "Manchester",
        "aliases": ["Man City", "Manchester City"],
    },
    {
        "canonical_name": "Real Madrid CF",
        "short_name": "Real Madrid",
        "country_code": "ESP",
        "city": "Madrid",
        "aliases": ["Real Madrid", "R. Madrid"],
    },
    {
        "canonical_name": "FC Barcelona",
        "short_name": "Barcelona",
        "country_code": "ESP",
        "city": "Barcelona",
        "aliases": ["Barcelona", "Barca"],
    },
    {
        "canonical_name": "FC Bayern Munich",
        "short_name": "Bayern Munich",
        "country_code": "GER",
        "city": "Munich",
        "aliases": ["Bayern Munich", "Bayern", "FC Bayern"],
    },
    {
        "canonical_name": "Juventus FC",
        "short_name": "Juventus",
        "country_code": "ITA",
        "city": "Turin",
        "aliases": ["Juventus", "Juve"],
    },
    {
        "canonical_name": "Paris Saint-Germain FC",
        "short_name": "PSG",
        "country_code": "FRA",
        "city": "Paris",
        "aliases": ["PSG", "Paris SG", "Paris Saint-Germain"],
    },
]


class OpenFootballReferenceAdapter(BaseAcquisitionAdapter):
    def __init__(self):
        super().__init__(
            source_code="OPENFOOTBALL",
            source_name="OpenFootball Clubs Repository",
            base_url="https://raw.githubusercontent.com/openfootball/clubs/master",
        )

    def load_reference_clubs(self) -> List[Dict[str, Any]]:
        return OPENFOOTBALL_CLUB_REFERENCES
