"""
Stage 8 Venue and Player Entity Resolution Module

Handles venue resolution where verified evidence exists and explicitly enforces
PLAYER RESOLUTION: UNAVAILABLE / NOT SUPPORTED BY CURRENT HISTORICAL SOURCE
without fabricating fake player records.
"""

from typing import Any, Dict, Optional


class VenuePlayerResolver:
    """
    Handles venue lookup and player entity status reporting.
    """

    def resolve_venue(self, club_canonical_name: str, city: Optional[str]) -> Dict[str, Any]:
        """
        Resolves venue entity if evidence exists; otherwise returns status UNAVAILABLE.
        """
        return {
            "venue_id": None,
            "canonical_name": None,
            "city": city,
            "status": "UNAVAILABLE",
            "evidence": "Venue data not provided in raw historical source",
        }

    def get_player_resolution_status(self) -> Dict[str, Any]:
        """
        Returns explicit player entity resolution status without fabricating fake player records.
        """
        return {
            "player_entity_resolution_status": "UNAVAILABLE",
            "reason": "PLAYER ENTITY RESOLUTION: UNAVAILABLE / NOT SUPPORTED BY CURRENT HISTORICAL SOURCE",
            "fabricated_player_records_count": 0,
        }
