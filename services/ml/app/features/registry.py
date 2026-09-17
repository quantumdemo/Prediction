"""
Stage 9 Feature Registry

Formal definitions and metadata for all prediction-time safe numerical features.
Enforces zero future-data leakage and explicit missingness states.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class FeatureDefinition:
    feature_id: str
    name: str
    family: str
    description: str
    calculation_formula: str
    window_type: str  # ROLLING_3, ROLLING_5, ROLLING_10, ALL_TIME, RECENT_MATCH
    minimum_history_required: int
    missing_data_rule: str  # INSUFFICIENT_HISTORY, MISSING, PRESERVE_NULL
    availability_cutoff: str  # STRICTLY_BEFORE_MATCH_KICKOFF
    leakage_status: str = "SAFE_PRE_MATCH"


STAGE9_FEATURE_REGISTRY: Dict[str, FeatureDefinition] = {
    # Recalculated Form Features
    "FEAT_FORM3_HOME": FeatureDefinition(
        feature_id="FEAT_FORM3_HOME",
        name="home_recalculated_form3",
        family="FORM",
        description="Points obtained by home team in previous 3 completed matches (Win=3, Draw=1, Loss=0)",
        calculation_formula="sum(points(last_3_matches))",
        window_type="ROLLING_3",
        minimum_history_required=3,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_FORM5_HOME": FeatureDefinition(
        feature_id="FEAT_FORM5_HOME",
        name="home_recalculated_form5",
        family="FORM",
        description="Points obtained by home team in previous 5 completed matches",
        calculation_formula="sum(points(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_FORM3_AWAY": FeatureDefinition(
        feature_id="FEAT_FORM3_AWAY",
        name="away_recalculated_form3",
        family="FORM",
        description="Points obtained by away team in previous 3 completed matches",
        calculation_formula="sum(points(last_3_matches))",
        window_type="ROLLING_3",
        minimum_history_required=3,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_FORM5_AWAY": FeatureDefinition(
        feature_id="FEAT_FORM5_AWAY",
        name="away_recalculated_form5",
        family="FORM",
        description="Points obtained by away team in previous 5 completed matches",
        calculation_formula="sum(points(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_FORM3_DIFF": FeatureDefinition(
        feature_id="FEAT_FORM3_DIFF",
        name="form3_difference",
        family="FORM",
        description="Home Form3 minus Away Form3",
        calculation_formula="home_form3 - away_form3",
        window_type="ROLLING_3",
        minimum_history_required=3,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_FORM5_DIFF": FeatureDefinition(
        feature_id="FEAT_FORM5_DIFF",
        name="form5_difference",
        family="FORM",
        description="Home Form5 minus Away Form5",
        calculation_formula="home_form5 - away_form5",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    # Goals Features
    "FEAT_GOALS_SCORED_AVG5_HOME": FeatureDefinition(
        feature_id="FEAT_GOALS_SCORED_AVG5_HOME",
        name="home_goals_scored_avg5",
        family="GOALS",
        description="Average goals scored by home team in previous 5 completed matches",
        calculation_formula="mean(goals_scored(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_GOALS_CONCEDED_AVG5_HOME": FeatureDefinition(
        feature_id="FEAT_GOALS_CONCEDED_AVG5_HOME",
        name="home_goals_conceded_avg5",
        family="GOALS",
        description="Average goals conceded by home team in previous 5 completed matches",
        calculation_formula="mean(goals_conceded(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_GOALS_SCORED_AVG5_AWAY": FeatureDefinition(
        feature_id="FEAT_GOALS_SCORED_AVG5_AWAY",
        name="away_goals_scored_avg5",
        family="GOALS",
        description="Average goals scored by away team in previous 5 completed matches",
        calculation_formula="mean(goals_scored(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_GOALS_CONCEDED_AVG5_AWAY": FeatureDefinition(
        feature_id="FEAT_GOALS_CONCEDED_AVG5_AWAY",
        name="away_goals_conceded_avg5",
        family="GOALS",
        description="Average goals conceded by away team in previous 5 completed matches",
        calculation_formula="mean(goals_conceded(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    # Shots & Target Features
    "FEAT_SHOTS_AVG5_HOME": FeatureDefinition(
        feature_id="FEAT_SHOTS_AVG5_HOME",
        name="home_shots_avg5",
        family="SHOTS",
        description="Average shots by home team in previous 5 completed matches",
        calculation_formula="mean(shots(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="MISSING",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_SHOTS_TARGET_AVG5_HOME": FeatureDefinition(
        feature_id="FEAT_SHOTS_TARGET_AVG5_HOME",
        name="home_shots_on_target_avg5",
        family="SHOTS",
        description="Average shots on target by home team in previous 5 completed matches",
        calculation_formula="mean(shots_on_target(last_5_matches))",
        window_type="ROLLING_5",
        minimum_history_required=5,
        missing_data_rule="MISSING",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    # Rest Days & Congestion Features
    "FEAT_REST_DAYS_HOME": FeatureDefinition(
        feature_id="FEAT_REST_DAYS_HOME",
        name="home_rest_days",
        family="REST_CONGESTION",
        description="Days since home team's previous completed match",
        calculation_formula="date(match_T) - date(match_T_minus_1)",
        window_type="RECENT_MATCH",
        minimum_history_required=1,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_REST_DAYS_AWAY": FeatureDefinition(
        feature_id="FEAT_REST_DAYS_AWAY",
        name="away_rest_days",
        family="REST_CONGESTION",
        description="Days since away team's previous completed match",
        calculation_formula="date(match_T) - date(match_T_minus_1)",
        window_type="RECENT_MATCH",
        minimum_history_required=1,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    # Head-to-Head
    "FEAT_H2H_HOME_WINS": FeatureDefinition(
        feature_id="FEAT_H2H_HOME_WINS",
        name="h2h_home_wins",
        family="HEAD_TO_HEAD",
        description="Number of wins by home team in previous H2H meetings before match T",
        calculation_formula="count(h2h_home_wins)",
        window_type="ALL_TIME",
        minimum_history_required=1,
        missing_data_rule="INSUFFICIENT_HISTORY",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    # Pre-match Elo
    "FEAT_ELO_PRE_MATCH_HOME": FeatureDefinition(
        feature_id="FEAT_ELO_PRE_MATCH_HOME",
        name="home_pre_match_elo",
        family="ELO",
        description="Most recent Elo rating snapshot strictly prior to match kickoff",
        calculation_formula="elo_snapshot(date < match_date)",
        window_type="RECENT_MATCH",
        minimum_history_required=1,
        missing_data_rule="MISSING",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_ELO_PRE_MATCH_AWAY": FeatureDefinition(
        feature_id="FEAT_ELO_PRE_MATCH_AWAY",
        name="away_pre_match_elo",
        family="ELO",
        description="Most recent Elo rating snapshot strictly prior to match kickoff",
        calculation_formula="elo_snapshot(date < match_date)",
        window_type="RECENT_MATCH",
        minimum_history_required=1,
        missing_data_rule="MISSING",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
    "FEAT_ELO_PRE_MATCH_DIFF": FeatureDefinition(
        feature_id="FEAT_ELO_PRE_MATCH_DIFF",
        name="pre_match_elo_difference",
        family="ELO",
        description="Home pre-match Elo minus Away pre-match Elo",
        calculation_formula="home_elo - away_elo",
        window_type="RECENT_MATCH",
        minimum_history_required=1,
        missing_data_rule="MISSING",
        availability_cutoff="STRICTLY_BEFORE_MATCH_KICKOFF",
    ),
}
