"""
Stage 8 Ingestion Adapter

Loads Stage 7 validated historical match and Elo records alongside OpenFootball reference data.
"""

from typing import Any, Dict, List

from services.ml.app.data.adapters.openfootball_reference import OpenFootballReferenceAdapter
from services.ml.app.data.stage7.pipeline import (
    Stage7CleaningPipelineEngine,
)


class Stage8IngestionAdapter:
    """
    Adapter to stream and provide clean records from Stage 7 and reference entities from OpenFootball.
    """

    def __init__(self):
        self.stage7_engine = Stage7CleaningPipelineEngine()
        self.openfootball_adapter = OpenFootballReferenceAdapter()

    def load_stage7_records(self) -> Dict[str, Any]:
        """
        Executes Stage 7 pipeline and returns accepted match and Elo records.
        """
        summary = self.stage7_engine.process_full_candidate_dataset()
        return {
            "summary": summary,
            "accepted_matches": self.stage7_engine.accepted_matches,
            "quarantined_matches": self.stage7_engine.quarantined_matches,
            "accepted_elo": self.stage7_engine.accepted_elo_records,
            "quarantined_elo": self.stage7_engine.quarantined_elo_records,
        }

    def load_openfootball_reference_clubs(self) -> List[Dict[str, Any]]:
        """
        Loads reference clubs and aliases from OpenFootball repository.
        """
        return self.openfootball_adapter.load_reference_clubs()
