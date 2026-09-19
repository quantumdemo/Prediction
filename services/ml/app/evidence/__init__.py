"""
Stage 15 Evidence Validation & Provenance Package

Provides deterministic validation, freshness checking, deduplication, conflict flagging,
and provenance retention for current-match web research evidence items.
"""

from services.ml.app.evidence.schemas import (
    EvidenceValidationReport,
    ValidatedEvidenceItem,
    ValidationOutcome,
    ValidationReason,
)
from services.ml.app.evidence.validator import EvidenceValidationEngine

__all__ = [
    "EvidenceValidationEngine",
    "ValidatedEvidenceItem",
    "EvidenceValidationReport",
    "ValidationOutcome",
    "ValidationReason",
]
