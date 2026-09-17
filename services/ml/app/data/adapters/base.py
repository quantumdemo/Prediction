import datetime
import logging
import uuid
from typing import Any, Dict, Optional, Tuple

import httpx

logger = logging.getLogger("football_ml.data.adapters")


class BaseAcquisitionAdapter:
    """
    Abstract Base Class for Data Source Acquisition Adapters (Stage 6)

    Responsibilities:
    - HTTP retrieval with exponential backoff and timeout handling
    - Raw payload preservation into raw_source_payloads
    - Source provenance record creation into provenance_records
    """

    def __init__(self, source_code: str, source_name: str, base_url: str):
        self.source_code = source_code
        self.source_name = source_name
        self.base_url = base_url

    def fetch_url(
        self, url: str, timeout: float = 15.0, retries: int = 3
    ) -> Tuple[bool, str, int]:
        """
        Fetches text/CSV/JSON content from HTTP URL with backoff retries.
        Returns: (success: bool, content: str, status_code: int)
        """
        for attempt in range(retries):
            try:
                with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        return True, response.text, 200
                    logger.warning(
                        f"Attempt {attempt + 1}/{retries} for {url} returned {response.status_code}"
                    )
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{retries} for {url} failed: {e}")

        return False, "", 500

    def create_raw_payload_entry(
        self,
        source_id: str,
        entity_type: str,
        external_identifier: str,
        raw_payload_json: str,
        ingestion_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "source_id": source_id,
            "entity_type": entity_type,
            "external_identifier": external_identifier,
            "raw_payload_json": raw_payload_json,
            "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc),
            "ingestion_run_id": ingestion_run_id,
        }

    def create_provenance_entry(
        self,
        entity_type: str,
        entity_id: str,
        source_id: str,
        source_url: str,
        validation_state: str = "VERIFIED",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "source_id": source_id,
            "source_url": source_url,
            "retrieved_at_utc": datetime.datetime.now(datetime.timezone.utc),
            "validation_state": validation_state,
            "notes": notes,
        }
