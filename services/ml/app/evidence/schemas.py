"""
Stage 15 Evidence Validation Schemas & Data Contracts

Defines validation outcomes (ACCEPTED, DOWNGRADED, REJECTED, FLAGGED_CONFLICT),
validation reason codes, validated evidence item models, and complete auditable validation reports.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.ml.app.research.schemas import FactCategory, ResearchItem, ResearchState


class ValidationOutcome(str, Enum):
    ACCEPTED = "ACCEPTED"
    DOWNGRADED = "DOWNGRADED"
    REJECTED = "REJECTED"
    FLAGGED_CONFLICT = "FLAGGED_CONFLICT"


class ValidationReason(str, Enum):
    VALID_PRIMARY_SOURCE = "VALID_PRIMARY_SOURCE"
    VALID_SECONDARY_SOURCE = "VALID_SECONDARY_SOURCE"
    STALE_TIMESTAMP = "STALE_TIMESTAMP"
    MISSING_TIMESTAMP = "MISSING_TIMESTAMP"
    INVALID_URL = "INVALID_URL"
    UNALLOWLISTED_SOURCE = "UNALLOWLISTED_SOURCE"
    EMPTY_CLAIM = "EMPTY_CLAIM"
    UNFOUND_FIXTURE_ASSOCIATION = "UNFOUND_FIXTURE_ASSOCIATION"
    WRONG_ENTITY_ASSOCIATION = "WRONG_ENTITY_ASSOCIATION"
    DUPLICATE_EVIDENCE = "DUPLICATE_EVIDENCE"
    CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"
    UNSUPPORTED_CATEGORY = "UNSUPPORTED_CATEGORY"


class ValidatedEvidenceItem(BaseModel):
    validation_id: str
    fact_id: str
    fixture_id: str
    category: FactCategory
    claim: str
    source_name: str
    source_url: str
    retrieval_timestamp_utc: str
    publication_timestamp_utc: Optional[str] = None
    original_research_state: ResearchState
    adjusted_research_state: ResearchState
    validation_outcome: ValidationOutcome
    validation_reasons: List[ValidationReason] = Field(default_factory=list)
    canonical_entities_mentioned: List[str] = Field(default_factory=list)
    contradiction_details: Optional[str] = None
    validation_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EvidenceValidationReport(BaseModel):
    report_id: str
    fixture_id: str
    total_evaluated: int = 0
    accepted_count: int = 0
    downgraded_count: int = 0
    rejected_count: int = 0
    conflicting_count: int = 0
    validated_items: List[ValidatedEvidenceItem] = Field(default_factory=list)
    rejected_items: List[ValidatedEvidenceItem] = Field(default_factory=list)
    audit_trail_hash: str = ""
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validation_engine_version: str = "STAGE15_EVIDENCE_VALIDATION_v1.0.0"
