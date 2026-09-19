"""
Stage 14 Web Research Data Contracts & Pydantic Schemas

Defines explicit research states, fact categories, fixture verification schemas,
research items with full provenance, and complete research report structures.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ResearchState(str, Enum):
    VERIFIED = "VERIFIED"
    LIKELY = "LIKELY"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"
    UNAVAILABLE = "UNAVAILABLE"


class FactCategory(str, Enum):
    RECENT_FORM = "RECENT_FORM"
    LEAGUE_POSITION = "LEAGUE_POSITION"
    INJURIES = "INJURIES"
    SUSPENSIONS = "SUSPENSIONS"
    EXPECTED_LINEUPS = "EXPECTED_LINEUPS"
    CONFIRMED_LINEUPS = "CONFIRMED_LINEUPS"
    TACTICAL_CHANGES = "TACTICAL_CHANGES"
    MANAGER_CHANGES = "MANAGER_CHANGES"
    REST_CONGESTION = "REST_CONGESTION"
    TRAVEL_CONTEXT = "TRAVEL_CONTEXT"
    HEAD_TO_HEAD = "HEAD_TO_HEAD"
    TEAM_NEWS = "TEAM_NEWS"


class FixtureVerification(BaseModel):
    fixture_id: str
    home_team: str
    away_team: str
    home_canonical_id: str
    away_canonical_id: str
    competition: str
    competition_canonical_id: str
    season: str
    match_date: str
    kickoff_time: Optional[str] = None
    venue: Optional[str] = None
    fixture_status: str = "SCHEDULED"
    is_verified: bool = True
    verification_method: str = "CANONICAL_DATABASE_MATCH"
    verified_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResearchItem(BaseModel):
    fact_id: str
    category: FactCategory
    claim: str
    source_name: str
    source_url: str
    retrieval_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    publication_timestamp_utc: Optional[str] = None
    research_state: ResearchState
    canonical_entities_mentioned: List[str] = Field(default_factory=list)
    contradiction_details: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("claim")
    def validate_claim_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Research item claim cannot be empty.")
        return v.strip()


class ResearchReport(BaseModel):
    report_id: str
    fixture: FixtureVerification
    items: List[ResearchItem] = Field(default_factory=list)
    summary_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    conflicting_items: List[ResearchItem] = Field(default_factory=list)
    unavailable_categories: List[FactCategory] = Field(default_factory=list)
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    research_engine_version: str = "STAGE14_WEB_RESEARCH_v1.0.0"
