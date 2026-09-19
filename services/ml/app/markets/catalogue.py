"""
Stage 17 Controlled Market Catalogue Definitions

Defines canonical market IDs, market types, required model outputs,
calculation rules, and support statuses for supported vs unsupported football markets.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MarketDefinition:
    market_id: str
    name: str
    market_type: str  # MULTI_CLASS, BINARY, MATRIX, HANDICAP, STATISTICAL
    required_model_output: str
    calculation_rule: str
    is_supported: bool
    description: str


CONTROLLED_MARKET_CATALOGUE: Dict[str, MarketDefinition] = {
    # 1. 1X2 Match Result
    "MKT_1X2": MarketDefinition(
        market_id="MKT_1X2",
        name="Full Time Result (1X2)",
        market_type="MULTI_CLASS",
        required_model_output="probabilities_1x2",
        calculation_rule="Direct mapping from calibrated probabilities_1x2 (Home, Draw, Away)",
        is_supported=True,
        description="Standard 3-way full time match result market (Home Win, Draw, Away Win)",
    ),

    # 2. Over / Under 0.5 Goals
    "MKT_OVER_UNDER_0_5": MarketDefinition(
        market_id="MKT_OVER_UNDER_0_5",
        name="Over/Under 0.5 Goals",
        market_type="BINARY",
        required_model_output="probabilities_totals",
        calculation_rule="Direct mapping from probabilities_totals (over_0_5, under_0_5)",
        is_supported=True,
        description="Binary total goals market for over/under 0.5 goals",
    ),

    # 3. Over / Under 1.5 Goals
    "MKT_OVER_UNDER_1_5": MarketDefinition(
        market_id="MKT_OVER_UNDER_1_5",
        name="Over/Under 1.5 Goals",
        market_type="BINARY",
        required_model_output="probabilities_totals",
        calculation_rule="Direct mapping from probabilities_totals (over_1_5, under_1_5)",
        is_supported=True,
        description="Binary total goals market for over/under 1.5 goals",
    ),

    # 4. Over / Under 2.5 Goals
    "MKT_OVER_UNDER_2_5": MarketDefinition(
        market_id="MKT_OVER_UNDER_2_5",
        name="Over/Under 2.5 Goals",
        market_type="BINARY",
        required_model_output="probabilities_totals",
        calculation_rule="Direct mapping from probabilities_totals (over_2_5, under_2_5)",
        is_supported=True,
        description="Binary total goals market for over/under 2.5 goals",
    ),

    # 5. Over / Under 3.5 Goals
    "MKT_OVER_UNDER_3_5": MarketDefinition(
        market_id="MKT_OVER_UNDER_3_5",
        name="Over/Under 3.5 Goals",
        market_type="BINARY",
        required_model_output="probabilities_totals",
        calculation_rule="Direct mapping from probabilities_totals (over_3_5, under_3_5)",
        is_supported=True,
        description="Binary total goals market for over/under 3.5 goals",
    ),

    # 6. Over / Under 4.5 Goals
    "MKT_OVER_UNDER_4_5": MarketDefinition(
        market_id="MKT_OVER_UNDER_4_5",
        name="Over/Under 4.5 Goals",
        market_type="BINARY",
        required_model_output="probabilities_totals",
        calculation_rule="Direct mapping from probabilities_totals (over_4_5, under_4_5)",
        is_supported=True,
        description="Binary total goals market for over/under 4.5 goals",
    ),

    # 7. Both Teams To Score (BTTS)
    "MKT_BTTS": MarketDefinition(
        market_id="MKT_BTTS",
        name="Both Teams To Score (BTTS)",
        market_type="BINARY",
        required_model_output="probabilities_btts",
        calculation_rule="Direct mapping from probabilities_btts (btts_yes, btts_no)",
        is_supported=True,
        description="Binary market for both teams scoring at least one goal",
    ),

    # 8. Correct Score Grid
    "MKT_CORRECT_SCORE": MarketDefinition(
        market_id="MKT_CORRECT_SCORE",
        name="Correct Score Grid",
        market_type="MATRIX",
        required_model_output="correct_score_matrix",
        calculation_rule="Matrix extraction from model score matrix dict (home_goals x away_goals)",
        is_supported=True,
        description="Exact full-time correct score probability grid",
    ),

    # Unsupported Markets (Explicit Rejection Rules)
    "MKT_ASIAN_HANDICAP": MarketDefinition(
        market_id="MKT_ASIAN_HANDICAP",
        name="Asian Handicap",
        market_type="HANDICAP",
        required_model_output="handicap_distribution",
        calculation_rule="Requires Asian handicap goal line distribution model - Not supported in Stage 17",
        is_supported=False,
        description="Asian handicap goal margin market",
    ),
    "MKT_CORNER_TOTALS": MarketDefinition(
        market_id="MKT_CORNER_TOTALS",
        name="Total Match Corners",
        market_type="STATISTICAL",
        required_model_output="corner_distribution",
        calculation_rule="Requires corner Poisson/Poisson-Binomial model - Not supported in Stage 17",
        is_supported=False,
        description="Over/Under total corners awarded in match",
    ),
    "MKT_CARD_TOTALS": MarketDefinition(
        market_id="MKT_CARD_TOTALS",
        name="Total Match Cards",
        market_type="STATISTICAL",
        required_model_output="card_distribution",
        calculation_rule="Requires booking points model - Not supported in Stage 17",
        is_supported=False,
        description="Over/Under total yellow/red cards shown in match",
    ),
}
