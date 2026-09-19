"""
Stage 17 Market Catalogue Pydantic Schemas

Defines schemas for mapped market outcomes, market provenance records,
individual mapped markets, and complete fixture market mapping reports.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MappedMarketOutcome(BaseModel):
    outcome_id: str
    outcome_name: str
    probability: float = Field(ge=0.0, le=1.0)
    is_valid_probability: bool = True


class MarketProvenanceRecord(BaseModel):
    market_id: str
    source_forecast_container_id: str
    source_fixture_id: str
    source_model_name: str
    source_model_version: str
    mapping_rule: str
    is_supported: bool
    unsupported_reason: Optional[str] = None
    mapping_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MappedMarket(BaseModel):
    market_id: str
    market_name: str
    market_type: str
    is_supported: bool
    unsupported_reason: Optional[str] = None
    outcomes: List[MappedMarketOutcome] = Field(default_factory=list)
    provenance: MarketProvenanceRecord


class MappedMarketReport(BaseModel):
    report_id: str
    fixture_id: str
    source_container_id: str
    supported_markets_count: int = 0
    unsupported_markets_count: int = 0
    mapped_markets: Dict[str, MappedMarket] = Field(default_factory=dict)
    unsupported_markets: List[str] = Field(default_factory=list)
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mapping_engine_version: str = "STAGE17_MARKET_MAPPING_v1.0.0"
