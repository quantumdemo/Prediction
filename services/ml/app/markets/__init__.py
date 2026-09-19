"""
Stage 17 Market Catalogue & Mapping Package

Provides controlled market definitions (1X2, Totals 0.5-4.5, BTTS, Correct Score),
deterministic forecast probability mapping, probability bounds checking,
unsupported market handling, and full provenance traceability.
"""

from services.ml.app.markets.catalogue import CONTROLLED_MARKET_CATALOGUE, MarketDefinition
from services.ml.app.markets.mapper import MarketMapper
from services.ml.app.markets.schemas import (
    MappedMarket,
    MappedMarketOutcome,
    MappedMarketReport,
    MarketProvenanceRecord,
)

__all__ = [
    "MarketMapper",
    "MarketDefinition",
    "CONTROLLED_MARKET_CATALOGUE",
    "MappedMarketOutcome",
    "MappedMarket",
    "MarketProvenanceRecord",
    "MappedMarketReport",
]
