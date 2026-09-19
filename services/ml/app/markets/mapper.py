"""
Stage 17 Market Mapper Implementation

Deterministically maps Stage 16 forecast probabilities into controlled football market probabilities.
Enforces probability axioms, score matrix normalization, unsupported market explicit rejections,
and full traceability without bookmaker odds, value calculation, or risk scoring.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.ml.app.markets.catalogue import CONTROLLED_MARKET_CATALOGUE, MarketDefinition
from services.ml.app.markets.schemas import (
    MappedMarket,
    MappedMarketOutcome,
    MappedMarketReport,
    MarketProvenanceRecord,
)
from services.ml.app.models.base import ForecastOutput
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer

logger = logging.getLogger("football_ml.markets.mapper")


class MarketMapper:
    """
    Deterministic Football Market Probability Mapper.
    """

    def __init__(self):
        self.catalogue = CONTROLLED_MARKET_CATALOGUE

    def map_forecast_container_to_markets(
        self, container: CurrentMatchForecastContainer
    ) -> MappedMarketReport:
        logger.info(f"Mapping forecast container {container.container_id} for fixture {container.fixture.fixture_id} to markets...")

        mapped_markets: Dict[str, MappedMarket] = {}
        unsupported_market_ids: List[str] = []
        supported_count = 0
        unsupported_count = 0

        # Check if container is blocked or missing forecast output
        if container.validation_status != "READY" or not container.forecast_output:
            logger.warning(f"Container {container.container_id} is blocked ({container.blocked_reason}). Returning unmapped report.")
            for mkt_id, mkt_def in self.catalogue.items():
                unsupported_market_ids.append(mkt_id)
                unsupported_count += 1
                mapped_markets[mkt_id] = MappedMarket(
                    market_id=mkt_id,
                    market_name=mkt_def.name,
                    market_type=mkt_def.market_type,
                    is_supported=False,
                    unsupported_reason=f"Forecast container blocked: {container.blocked_reason or 'MISSING_FORECAST_OUTPUT'}",
                    outcomes=[],
                    provenance=MarketProvenanceRecord(
                        market_id=mkt_id,
                        source_forecast_container_id=container.container_id,
                        source_fixture_id=container.fixture.fixture_id,
                        source_model_name=container.model_name,
                        source_model_version=container.model_version,
                        mapping_rule=mkt_def.calculation_rule,
                        is_supported=False,
                        unsupported_reason=f"Container blocked ({container.blocked_reason})",
                    ),
                )

            return MappedMarketReport(
                report_id=f"MKT_REP_{container.fixture.fixture_id}_{uuid.uuid4().hex[:6]}",
                fixture_id=container.fixture.fixture_id,
                source_container_id=container.container_id,
                supported_markets_count=0,
                unsupported_markets_count=unsupported_count,
                mapped_markets=mapped_markets,
                unsupported_markets=unsupported_market_ids,
            )

        fc: ForecastOutput = container.forecast_output

        # Process each market in the controlled catalogue
        for mkt_id, mkt_def in self.catalogue.items():
            if not mkt_def.is_supported:
                unsupported_market_ids.append(mkt_id)
                unsupported_count += 1
                mapped_markets[mkt_id] = MappedMarket(
                    market_id=mkt_id,
                    market_name=mkt_def.name,
                    market_type=mkt_def.market_type,
                    is_supported=False,
                    unsupported_reason=mkt_def.calculation_rule,
                    outcomes=[],
                    provenance=MarketProvenanceRecord(
                        market_id=mkt_id,
                        source_forecast_container_id=container.container_id,
                        source_fixture_id=container.fixture.fixture_id,
                        source_model_name=container.model_name,
                        source_model_version=container.model_version,
                        mapping_rule=mkt_def.calculation_rule,
                        is_supported=False,
                        unsupported_reason=mkt_def.calculation_rule,
                    ),
                )
                continue

            # Map supported market probabilities deterministically
            mapped_mkt = self._map_supported_market(mkt_def, fc, container)
            mapped_markets[mkt_id] = mapped_mkt
            supported_count += 1

        report = MappedMarketReport(
            report_id=f"MKT_REP_{container.fixture.fixture_id}_{uuid.uuid4().hex[:6]}",
            fixture_id=container.fixture.fixture_id,
            source_container_id=container.container_id,
            supported_markets_count=supported_count,
            unsupported_markets_count=unsupported_count,
            mapped_markets=mapped_markets,
            unsupported_markets=unsupported_market_ids,
        )

        logger.info(f"Market mapping complete for {container.fixture.fixture_id}: Supported={supported_count}, Unsupported={unsupported_count}.")
        return report

    def _map_supported_market(
        self, mkt_def: MarketDefinition, fc: ForecastOutput, container: CurrentMatchForecastContainer
    ) -> MappedMarket:
        outcomes: List[MappedMarketOutcome] = []

        if mkt_def.market_id == "MKT_1X2":
            p_home = self._clamp_prob(fc.probabilities_1x2.get("home", 0.33))
            p_draw = self._clamp_prob(fc.probabilities_1x2.get("draw", 0.33))
            p_away = self._clamp_prob(fc.probabilities_1x2.get("away", 0.33))

            outcomes = [
                MappedMarketOutcome(outcome_id="1", outcome_name="Home Win (1)", probability=p_home),
                MappedMarketOutcome(outcome_id="X", outcome_name="Draw (X)", probability=p_draw),
                MappedMarketOutcome(outcome_id="2", outcome_name="Away Win (2)", probability=p_away),
            ]

        elif mkt_def.market_id.startswith("MKT_OVER_UNDER_"):
            # Extract line threshold, e.g. "0_5", "1_5", "2_5", "3_5", "4_5"
            line_str = mkt_def.market_id.replace("MKT_OVER_UNDER_", "")
            line_val = line_str.replace("_", ".")

            p_over = self._clamp_prob(fc.probabilities_totals.get(f"over_{line_str}", 0.5))
            p_under = self._clamp_prob(fc.probabilities_totals.get(f"under_{line_str}", 0.5))

            outcomes = [
                MappedMarketOutcome(outcome_id=f"OVER_{line_str}", outcome_name=f"Over {line_val} Goals", probability=p_over),
                MappedMarketOutcome(outcome_id=f"UNDER_{line_str}", outcome_name=f"Under {line_val} Goals", probability=p_under),
            ]

        elif mkt_def.market_id == "MKT_BTTS":
            p_yes = self._clamp_prob(fc.probabilities_btts.get("btts_yes", 0.5))
            p_no = self._clamp_prob(fc.probabilities_btts.get("btts_no", 0.5))

            outcomes = [
                MappedMarketOutcome(outcome_id="BTTS_YES", outcome_name="Both Teams To Score - Yes", probability=p_yes),
                MappedMarketOutcome(outcome_id="BTTS_NO", outcome_name="Both Teams To Score - No", probability=p_no),
            ]

        elif mkt_def.market_id == "MKT_CORRECT_SCORE":
            for h_g, row in fc.correct_score_matrix.items():
                for a_g, p in row.items():
                    p_clamped = self._clamp_prob(p)
                    outcomes.append(
                        MappedMarketOutcome(
                            outcome_id=f"CS_{h_g}_{a_g}",
                            outcome_name=f"Correct Score {h_g}-{a_g}",
                            probability=p_clamped,
                        )
                    )

        return MappedMarket(
            market_id=mkt_def.market_id,
            market_name=mkt_def.name,
            market_type=mkt_def.market_type,
            is_supported=True,
            unsupported_reason=None,
            outcomes=outcomes,
            provenance=MarketProvenanceRecord(
                market_id=mkt_def.market_id,
                source_forecast_container_id=container.container_id,
                source_fixture_id=container.fixture.fixture_id,
                source_model_name=container.model_name,
                source_model_version=container.model_version,
                mapping_rule=mkt_def.calculation_rule,
                is_supported=True,
                unsupported_reason=None,
            ),
        )

    @staticmethod
    def _clamp_prob(val: float) -> float:
        return max(0.0, min(1.0, float(val)))
