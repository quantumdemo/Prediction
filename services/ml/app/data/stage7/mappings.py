"""
Stage 7 Field Mapping and Schema Normalization Specification

Defines explicit mappings from raw source field names to project canonical field names,
field classifications, and validation rules.
"""


# Field classifications
CLASS_GROUP_A_CLEAN_FEATURE = "GROUP_A_CLEAN_FEATURE"
CLASS_REQUIRES_RECALCULATION = "REQUIRES_RECALCULATION"
CLASS_REJECTED_ODDS = "REJECTED_ODDS"
CLASS_REJECTED_UNVERIFIED = "REJECTED_UNVERIFIED"
CLASS_REJECTED_LEAKAGE = "REJECTED_LEAKAGE"
CLASS_ELO_VERIFIED = "VERIFIED_HISTORICAL_ELO"
CLASS_ELO_PROVISIONAL = "PROVISIONAL_ESTIMATE"

MATCHES_COLUMN_MAPPINGS = {
    "Division": {
        "canonical_field": "source_division_code",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_EMPTY_STRING",
        "missing_policy": "QUARANTINE",
    },
    "MatchDate": {
        "canonical_field": "match_date",
        "type": "date",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "VALID_CALENDAR_DATE_YYYY_MM_DD",
        "missing_policy": "QUARANTINE",
    },
    "MatchTime": {
        "canonical_field": "match_time_cet_minus1",
        "type": "time",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "VALID_TIME_HH_MM_SS_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeTeam": {
        "canonical_field": "raw_home_team_name",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_EMPTY_STRING",
        "missing_policy": "QUARANTINE",
    },
    "AwayTeam": {
        "canonical_field": "raw_away_team_name",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_EMPTY_STRING",
        "missing_policy": "QUARANTINE",
    },
    "FTHome": {
        "canonical_field": "full_time_home_goals",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER",
        "missing_policy": "QUARANTINE",
    },
    "FTAway": {
        "canonical_field": "full_time_away_goals",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER",
        "missing_policy": "QUARANTINE",
    },
    "FTResult": {
        "canonical_field": "full_time_result",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "MATCHES_ENUM_H_D_A",
        "missing_policy": "QUARANTINE",
    },
    "HTHome": {
        "canonical_field": "half_time_home_goals",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HTAway": {
        "canonical_field": "half_time_away_goals",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HTResult": {
        "canonical_field": "half_time_result",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "MATCHES_ENUM_H_D_A_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeShots": {
        "canonical_field": "home_shots",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayShots": {
        "canonical_field": "away_shots",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeTarget": {
        "canonical_field": "home_shots_on_target",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_LEQ_SHOTS",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayTarget": {
        "canonical_field": "away_shots_on_target",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_LEQ_SHOTS",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeFouls": {
        "canonical_field": "home_fouls",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayFouls": {
        "canonical_field": "away_fouls",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeCorners": {
        "canonical_field": "home_corners",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayCorners": {
        "canonical_field": "away_corners",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeYellow": {
        "canonical_field": "home_yellow_cards",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayYellow": {
        "canonical_field": "away_yellow_cards",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeRed": {
        "canonical_field": "home_red_cards",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayRed": {
        "canonical_field": "away_red_cards",
        "type": "int",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_NEGATIVE_INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    # Elo Fields
    "HomeElo": {
        "canonical_field": "home_elo",
        "type": "float",
        "classification": "HISTORICAL_ELO_REFERENCE",
        "validation_rule": "POSITIVE_FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayElo": {
        "canonical_field": "away_elo",
        "type": "float",
        "classification": "HISTORICAL_ELO_REFERENCE",
        "validation_rule": "POSITIVE_FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    # Pre-calculated features requiring recalculation in Stage 9
    "Form3Home": {
        "canonical_field": "source_form3_home",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_BETWEEN_0_AND_9_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "Form5Home": {
        "canonical_field": "source_form5_home",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_BETWEEN_0_AND_15_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "Form3Away": {
        "canonical_field": "source_form3_away",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_BETWEEN_0_AND_9_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "Form5Away": {
        "canonical_field": "source_form5_away",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_BETWEEN_0_AND_15_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "Form3_Diff": {
        "canonical_field": "source_form3_diff",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "Form5_Diff": {
        "canonical_field": "source_form5_diff",
        "type": "int",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "HomeRating": {
        "canonical_field": "source_home_rating",
        "type": "float",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "AwayRating": {
        "canonical_field": "source_away_rating",
        "type": "float",
        "classification": CLASS_REQUIRES_RECALCULATION,
        "validation_rule": "FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "ClusterLabel": {
        "canonical_field": "source_cluster_label",
        "type": "int",
        "classification": CLASS_REJECTED_LEAKAGE,
        "validation_rule": "INTEGER_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "ClusterProb": {
        "canonical_field": "source_cluster_prob",
        "type": "float",
        "classification": CLASS_REJECTED_LEAKAGE,
        "validation_rule": "PROBABILITY_0_TO_1_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "ExpectedGoalsHome": {
        "canonical_field": "source_expected_goals_home",
        "type": "float",
        "classification": CLASS_REJECTED_UNVERIFIED,
        "validation_rule": "NON_NEGATIVE_FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "ExpectedGoalsAway": {
        "canonical_field": "source_expected_goals_away",
        "type": "float",
        "classification": CLASS_REJECTED_UNVERIFIED,
        "validation_rule": "NON_NEGATIVE_FLOAT_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    # Odds Fields -> REJECTED_ODDS
    "OddHome": {"canonical_field": "source_odd_home", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "OddDraw": {"canonical_field": "source_odd_draw", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "OddAway": {"canonical_field": "source_odd_away", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "MaxHome": {"canonical_field": "source_max_home", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "MaxDraw": {"canonical_field": "source_max_draw", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "MaxAway": {"canonical_field": "source_max_away", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "Over25": {"canonical_field": "source_over25", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "Under25": {"canonical_field": "source_under25", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "MaxOver25": {"canonical_field": "source_max_over25", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "MaxUnder25": {"canonical_field": "source_max_under25", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "HandiSize": {"canonical_field": "source_handi_size", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "HandiHome": {"canonical_field": "source_handi_home", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
    "HandiAway": {"canonical_field": "source_handi_away", "type": "float", "classification": CLASS_REJECTED_ODDS, "validation_rule": "FLOAT_OR_NULL", "missing_policy": "PRESERVE_NULL"},
}

ELO_COLUMN_MAPPINGS = {
    "date": {
        "canonical_field": "snapshot_date",
        "type": "date",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "VALID_CALENDAR_DATE_YYYY_MM_DD",
        "missing_policy": "QUARANTINE",
    },
    "club": {
        "canonical_field": "raw_club_name",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "NON_EMPTY_STRING",
        "missing_policy": "QUARANTINE",
    },
    "country": {
        "canonical_field": "country_code",
        "type": "str",
        "classification": CLASS_GROUP_A_CLEAN_FEATURE,
        "validation_rule": "THREE_LETTER_COUNTRY_CODE_OR_NULL",
        "missing_policy": "PRESERVE_NULL",
    },
    "elo": {
        "canonical_field": "elo_rating",
        "type": "float",
        "classification": "ELO_CLASSIFICATION_DEPENDENT",
        "validation_rule": "POSITIVE_FLOAT",
        "missing_policy": "QUARANTINE",
    },
}
