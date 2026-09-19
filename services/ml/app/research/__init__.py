"""
Stage 14 Current-Match Web Research Engine Package

Provides structured pre-match research collection, fixture verification, entity alias resolution,
provenance tracking, explicit research state classification, and contradiction handling
for current football matches without probability generation or synthetic data fabrication.
"""

from services.ml.app.research.engine import CurrentMatchResearchEngine
from services.ml.app.research.schemas import (
    FactCategory,
    FixtureVerification,
    ResearchItem,
    ResearchReport,
    ResearchState,
)
from services.ml.app.research.verification import FixtureVerifier

__all__ = [
    "CurrentMatchResearchEngine",
    "FixtureVerifier",
    "ResearchState",
    "FactCategory",
    "FixtureVerification",
    "ResearchItem",
    "ResearchReport",
]
