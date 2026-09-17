"""
Source Acquisition Adapters Package (Stage 6)
"""

from services.ml.app.data.adapters.base import BaseAcquisitionAdapter
from services.ml.app.data.adapters.football_data_uk import FootballDataUKAdapter
from services.ml.app.data.adapters.openfootball_reference import OpenFootballReferenceAdapter

__all__ = [
    "BaseAcquisitionAdapter",
    "FootballDataUKAdapter",
    "OpenFootballReferenceAdapter",
]
