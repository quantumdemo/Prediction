"""
Stage 7 Data Cleaning, Normalization, Validation, and Quarantine Pipeline Engine

Executes deterministic cleaning, date/season/club-string normalization, cross-field validation,
quarantine classification, duplicate detection, and Stage 7 quality metric collection over candidate datasets.
"""

import logging
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from services.ml.app.data.stage7.ingestion import (
    SourceProvenance,
    stream_raw_elo_ratings,
    stream_raw_matches,
)
from services.ml.app.data.stage7.mappings import (
    MATCHES_COLUMN_MAPPINGS,
)

logger = logging.getLogger("football_ml.data.stage7.pipeline")

# Cutoff date for verified historical ClubElo ratings
CLUB_ELO_VERIFIED_CUTOFF_DATE = "2025-06-01"

# Stage 6 Baseline Validation Fixtures Reference (39 records)
STAGE6_BASELINE_FIXTURES_COUNT = 39


@dataclass
class ValidationIssue:
    rule: str
    severity: str  # "ERROR" or "WARNING"
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None


@dataclass
class CleanMatchRecord:
    record_status: str  # ACCEPTED, ACCEPTED_WITH_WARNINGS, QUARANTINED
    provenance: SourceProvenance
    canonical_data: Dict[str, Any] = field(default_factory=dict)
    normalized_names: Dict[str, str] = field(default_factory=dict)
    field_states: Dict[str, str] = field(default_factory=dict)
    validation_issues: List[ValidationIssue] = field(default_factory=list)


@dataclass
class CleanEloRecord:
    record_status: str  # ACCEPTED, QUARANTINED
    provenance: SourceProvenance
    snapshot_date: str = ""
    raw_club_name: str = ""
    normalized_club_key: str = ""
    country_code: Optional[str] = None
    elo_rating: Optional[float] = None
    classification: str = ""  # VERIFIED_HISTORICAL_ELO or PROVISIONAL_ESTIMATE
    validation_issues: List[ValidationIssue] = field(default_factory=list)


def normalize_team_string(raw_name: str) -> str:
    """
    Normalizes team name string for deterministic lookup keys without fuzzy merging.
    - Trims leading/trailing whitespace
    - Collapses inner whitespace
    - Unicode normalization (decomposed/recomposed handling via python string)
    - Lowercases for lookup keys
    """
    if not raw_name:
        return ""
    # Strip whitespace and collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", raw_name.strip())
    return cleaned.lower()


def parse_canonical_date(date_str: str) -> Tuple[Optional[str], Optional[ValidationIssue]]:
    """
    Validates and converts date into canonical ISO YYYY-MM-DD.
    """
    if not date_str:
        return None, ValidationIssue("DATE_MISSING", "ERROR", "Date string is empty", "MatchDate")
    date_str = date_str.strip()
    # Check standard ISO YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.year < 1900 or dt > datetime(2026, 12, 31):
                return date_str, ValidationIssue("DATE_OUT_OF_BOUNDS", "ERROR", f"Date '{date_str}' is out of acceptable bounds", "MatchDate", date_str)
            return date_str, None
        except ValueError:
            return None, ValidationIssue("DATE_INVALID_CALENDAR", "ERROR", f"Date '{date_str}' is malformed calendar date", "MatchDate", date_str)

    # Check DD/MM/YYYY
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d"), None
        except ValueError:
            return None, ValidationIssue("DATE_INVALID_CALENDAR", "ERROR", f"Date '{date_str}' is malformed calendar date", "MatchDate", date_str)

    return None, ValidationIssue("DATE_FORMAT_UNRECOGNIZED", "ERROR", f"Unrecognized date format '{date_str}'", "MatchDate", date_str)


def parse_canonical_time(time_str: str) -> Tuple[Optional[str], Optional[ValidationIssue]]:
    """
    Validates HH:MM:SS or HH:MM match time without converting unknown timezone or inventing times.
    """
    if not time_str or time_str.strip() in ("", "NULL", "None", "nan"):
        return None, None
    time_str = time_str.strip()
    if re.match(r"^\d{2}:\d{2}:\d{2}$", time_str):
        return time_str, None
    if re.match(r"^\d{2}:\d{2}$", time_str):
        return f"{time_str}:00", None
    return None, ValidationIssue("TIME_FORMAT_UNRECOGNIZED", "WARNING", f"Unrecognized time format '{time_str}'", "MatchTime", time_str)


def derive_canonical_season(match_date_str: str) -> Optional[str]:
    """
    Derives deterministic season label (e.g. 2024/25) from canonical match date YYYY-MM-DD.
    Assumes European football calendar split around July 1.
    """
    if not match_date_str or len(match_date_str) < 4:
        return None
    year = int(match_date_str[:4])
    month = int(match_date_str[5:7])
    if month >= 7:
        start_year = year
        end_year = (year + 1) % 100
    else:
        start_year = year - 1
        end_year = year % 100
    return f"{start_year}/{end_year:02d}"


def parse_int_field(val: Any) -> Tuple[Optional[int], str]:
    """
    Parses int value and returns (value, field_state: PRESENT, MISSING, INVALID).
    """
    if val is None or str(val).strip() in ("", "NULL", "None", "nan", "NaN"):
        return None, "MISSING"
    try:
        f_val = float(val)
        if math.isnan(f_val):
            return None, "MISSING"
        i_val = int(f_val)
        if f_val != i_val:
            return None, "INVALID"
        return i_val, "PRESENT"
    except (ValueError, TypeError):
        return None, "INVALID"


def parse_float_field(val: Any) -> Tuple[Optional[float], str]:
    """
    Parses float value and returns (value, field_state: PRESENT, MISSING, INVALID).
    """
    if val is None or str(val).strip() in ("", "NULL", "None", "nan", "NaN"):
        return None, "MISSING"
    try:
        f_val = float(val)
        if math.isnan(f_val) or math.isinf(f_val):
            return None, "MISSING"
        return f_val, "PRESENT"
    except (ValueError, TypeError):
        return None, "INVALID"


class Stage7CleaningPipelineEngine:
    """
    Stage 7 Comprehensive Cleaning Pipeline Engine.
    Executes raw processing, normalization, cross-validation, quarantine, duplicate detection,
    and quality statistics generation.
    """

    def __init__(self):
        self.accepted_matches: List[CleanMatchRecord] = []
        self.quarantined_matches: List[CleanMatchRecord] = []
        self.accepted_elo_records: List[CleanEloRecord] = []
        self.quarantined_elo_records: List[CleanEloRecord] = []

        self.duplicate_records_count = 0
        self.exact_duplicates_count = 0
        self.suspicious_duplicates_count = 0

        self.unique_teams_requiring_stage8_review: Set[str] = set()

        # Quality metrics tracking
        self.match_metrics = {
            "total_raw": 0,
            "parsed_valid": 0,
            "accepted_with_warnings": 0,
            "quarantined": 0,
            "duplicates": 0,
            "earliest_date": None,
            "latest_date": None,
            "field_counts": {},
        }
        self.elo_metrics = {
            "total_raw": 0,
            "verified_historical": 0,
            "provisional_estimates": 0,
            "quarantined": 0,
            "earliest_date": None,
            "latest_date": None,
        }

    def clean_single_match_row(
        self, row_idx: int, raw_row: Dict[str, str], prov: SourceProvenance
    ) -> CleanMatchRecord:
        issues: List[ValidationIssue] = []
        canonical_data: Dict[str, Any] = {}
        normalized_names: Dict[str, str] = {}
        field_states: Dict[str, str] = {}

        # 1. Division
        raw_div = raw_row.get("Division", "").strip()
        if not raw_div:
            issues.append(ValidationIssue("DIVISION_MISSING", "ERROR", "Division code is missing", "Division"))
            field_states["source_division_code"] = "MISSING"
        else:
            canonical_data["source_division_code"] = raw_div
            field_states["source_division_code"] = "PRESENT"

        # 2. Date & Season
        raw_date = raw_row.get("MatchDate", "")
        parsed_date, date_issue = parse_canonical_date(raw_date)
        if date_issue:
            issues.append(date_issue)
            field_states["match_date"] = "INVALID"
        else:
            canonical_data["match_date"] = parsed_date
            field_states["match_date"] = "PRESENT"
            canonical_data["derived_season"] = derive_canonical_season(parsed_date)

        # 3. Time
        raw_time = raw_row.get("MatchTime", "")
        parsed_time, time_issue = parse_canonical_time(raw_time)
        if time_issue:
            issues.append(time_issue)
            field_states["match_time_cet_minus1"] = "INVALID"
        else:
            canonical_data["match_time_cet_minus1"] = parsed_time
            field_states["match_time_cet_minus1"] = "PRESENT" if parsed_time else "NOT_AVAILABLE_FROM_SOURCE"

        # 4. Club Names
        raw_home = raw_row.get("HomeTeam", "").strip()
        raw_away = raw_row.get("AwayTeam", "").strip()
        if not raw_home:
            issues.append(ValidationIssue("HOME_TEAM_MISSING", "ERROR", "Home team name is missing", "HomeTeam"))
            field_states["raw_home_team_name"] = "MISSING"
        else:
            canonical_data["raw_home_team_name"] = raw_home
            norm_home = normalize_team_string(raw_home)
            normalized_names["home_team_comparison_key"] = norm_home
            field_states["raw_home_team_name"] = "PRESENT"
            self.unique_teams_requiring_stage8_review.add(raw_home)

        if not raw_away:
            issues.append(ValidationIssue("AWAY_TEAM_MISSING", "ERROR", "Away team name is missing", "AwayTeam"))
            field_states["raw_away_team_name"] = "MISSING"
        else:
            canonical_data["raw_away_team_name"] = raw_away
            norm_away = normalize_team_string(raw_away)
            normalized_names["away_team_comparison_key"] = norm_away
            field_states["raw_away_team_name"] = "PRESENT"
            self.unique_teams_requiring_stage8_review.add(raw_away)

        if raw_home and raw_away and normalized_names.get("home_team_comparison_key") == normalized_names.get("away_team_comparison_key"):
            issues.append(ValidationIssue("SAME_HOME_AWAY_CLUB", "ERROR", f"Home and away club names normalize to same string '{raw_home}'", "HomeTeam"))

        # 5. Full-time goals & result
        ft_home, ft_home_st = parse_int_field(raw_row.get("FTHome"))
        ft_away, ft_away_st = parse_int_field(raw_row.get("FTAway"))
        ft_res = raw_row.get("FTResult", "").strip().upper() if raw_row.get("FTResult") else None

        field_states["full_time_home_goals"] = ft_home_st
        field_states["full_time_away_goals"] = ft_away_st

        if ft_home_st == "INVALID" or ft_home is None or ft_home < 0:
            issues.append(ValidationIssue("FT_HOME_GOALS_INVALID", "ERROR", f"Invalid FT home goals '{raw_row.get('FTHome')}'", "FTHome"))
        else:
            canonical_data["full_time_home_goals"] = ft_home

        if ft_away_st == "INVALID" or ft_away is None or ft_away < 0:
            issues.append(ValidationIssue("FT_AWAY_GOALS_INVALID", "ERROR", f"Invalid FT away goals '{raw_row.get('FTAway')}'", "FTAway"))
        else:
            canonical_data["full_time_away_goals"] = ft_away

        if not ft_res or ft_res not in ("H", "D", "A"):
            issues.append(ValidationIssue("FT_RESULT_INVALID", "ERROR", f"Invalid FT result '{ft_res}'", "FTResult"))
            field_states["full_time_result"] = "INVALID"
        else:
            canonical_data["full_time_result"] = ft_res
            field_states["full_time_result"] = "PRESENT"

        # Result vs Score cross-validation
        if ft_home is not None and ft_away is not None and ft_res in ("H", "D", "A"):
            expected_res = "H" if ft_home > ft_away else ("A" if ft_home < ft_away else "D")
            if ft_res != expected_res:
                issues.append(ValidationIssue("FT_RESULT_SCORE_MISMATCH", "ERROR", f"FT result '{ft_res}' conflicts with score {ft_home}-{ft_away} (expected '{expected_res}')", "FTResult"))

        # 6. Half-time goals & result
        ht_home, ht_home_st = parse_int_field(raw_row.get("HTHome"))
        ht_away, ht_away_st = parse_int_field(raw_row.get("HTAway"))
        ht_res = raw_row.get("HTResult", "").strip().upper() if raw_row.get("HTResult") else None

        field_states["half_time_home_goals"] = ht_home_st
        field_states["half_time_away_goals"] = ht_away_st

        if ht_home is not None and ht_home >= 0:
            canonical_data["half_time_home_goals"] = ht_home
            if ft_home is not None and ht_home > ft_home:
                issues.append(ValidationIssue("HT_GOALS_EXCEED_FT", "ERROR", f"HT home goals ({ht_home}) exceed FT home goals ({ft_home})", "HTHome"))

        if ht_away is not None and ht_away >= 0:
            canonical_data["half_time_away_goals"] = ht_away
            if ft_away is not None and ht_away > ft_away:
                issues.append(ValidationIssue("HT_GOALS_EXCEED_FT", "ERROR", f"HT away goals ({ht_away}) exceed FT away goals ({ft_away})", "HTAway"))

        if ht_res and ht_res in ("H", "D", "A"):
            canonical_data["half_time_result"] = ht_res
            field_states["half_time_result"] = "PRESENT"
            if ht_home is not None and ht_away is not None:
                exp_ht_res = "H" if ht_home > ht_away else ("A" if ht_home < ht_away else "D")
                if ht_res != exp_ht_res:
                    issues.append(ValidationIssue("HT_RESULT_SCORE_MISMATCH", "WARNING", f"HT result '{ht_res}' conflicts with HT score {ht_home}-{ht_away}", "HTResult"))

        # 7. Statistics Parsing & Relationship Validation
        stat_fields = [
            ("HomeShots", "home_shots"),
            ("AwayShots", "away_shots"),
            ("HomeTarget", "home_shots_on_target"),
            ("AwayTarget", "away_shots_on_target"),
            ("HomeFouls", "home_fouls"),
            ("AwayFouls", "away_fouls"),
            ("HomeCorners", "home_corners"),
            ("AwayCorners", "away_corners"),
            ("HomeYellow", "home_yellow_cards"),
            ("AwayYellow", "away_yellow_cards"),
            ("HomeRed", "home_red_cards"),
            ("AwayRed", "away_red_cards"),
        ]

        for raw_k, can_k in stat_fields:
            v_val, v_st = parse_int_field(raw_row.get(raw_k))
            field_states[can_k] = v_st
            if v_st == "PRESENT" and v_val is not None:
                if v_val < 0:
                    issues.append(ValidationIssue(f"{can_k.upper()}_NEGATIVE", "ERROR", f"Negative statistic for {can_k}: {v_val}", raw_k))
                else:
                    canonical_data[can_k] = v_val

        # Shots on target vs Shots check
        hs = canonical_data.get("home_shots")
        hst = canonical_data.get("home_shots_on_target")
        if hs is not None and hst is not None and hst > hs:
            issues.append(ValidationIssue("HOME_SHOTS_ON_TARGET_EXCEEDS_SHOTS", "ERROR", f"Home shots on target ({hst}) > total shots ({hs})", "HomeTarget"))

        aws = canonical_data.get("away_shots")
        ast = canonical_data.get("away_shots_on_target")
        if aws is not None and ast is not None and ast > aws:
            issues.append(ValidationIssue("AWAY_SHOTS_ON_TARGET_EXCEEDS_SHOTS", "ERROR", f"Away shots on target ({ast}) > total shots ({aws})", "AwayTarget"))

        # 8. Elo & Pre-calculated & Odds Fields Classifications
        # Preserve Elo ratings
        h_elo, h_elo_st = parse_float_field(raw_row.get("HomeElo"))
        a_elo, a_elo_st = parse_float_field(raw_row.get("AwayElo"))
        field_states["home_elo"] = h_elo_st
        field_states["away_elo"] = a_elo_st
        if h_elo is not None: canonical_data["home_elo"] = h_elo
        if a_elo is not None: canonical_data["away_elo"] = a_elo

        # Form / Rating -> REQUIRES_RECALCULATION
        for fk in ["Form3Home", "Form5Home", "Form3Away", "Form5Away", "Form3_Diff", "Form5_Diff", "HomeRating", "AwayRating"]:
            v, st = parse_float_field(raw_row.get(fk))
            mapped_f = MATCHES_COLUMN_MAPPINGS[fk]["canonical_field"]
            field_states[mapped_f] = f"REQUIRES_RECALCULATION_{st}"
            if v is not None:
                canonical_data[mapped_f] = v

        # Cluster Labels -> REJECTED_LEAKAGE
        for fk in ["ClusterLabel", "ClusterProb"]:
            v, st = parse_float_field(raw_row.get(fk))
            mapped_f = MATCHES_COLUMN_MAPPINGS[fk]["canonical_field"]
            field_states[mapped_f] = f"REJECTED_LEAKAGE_{st}"

        # Synthetic xG -> REJECTED_UNVERIFIED
        for fk in ["ExpectedGoalsHome", "ExpectedGoalsAway"]:
            v, st = parse_float_field(raw_row.get(fk))
            mapped_f = MATCHES_COLUMN_MAPPINGS[fk]["canonical_field"]
            field_states[mapped_f] = f"REJECTED_UNVERIFIED_{st}"

        # Odds -> REJECTED_ODDS
        odds_keys = ["OddHome", "OddDraw", "OddAway", "MaxHome", "MaxDraw", "MaxAway", "Over25", "Under25", "MaxOver25", "MaxUnder25", "HandiSize", "HandiHome", "HandiAway"]
        for fk in odds_keys:
            v, st = parse_float_field(raw_row.get(fk))
            mapped_f = MATCHES_COLUMN_MAPPINGS[fk]["canonical_field"]
            field_states[mapped_f] = f"REJECTED_ODDS_{st}"

        # Determine overall status
        has_errors = any(i.severity == "ERROR" for i in issues)
        has_warnings = any(i.severity == "WARNING" for i in issues)

        if has_errors:
            status = "QUARANTINED"
        elif has_warnings:
            status = "ACCEPTED_WITH_WARNINGS"
        else:
            status = "ACCEPTED"

        return CleanMatchRecord(
            record_status=status,
            provenance=prov,
            canonical_data=canonical_data,
            normalized_names=normalized_names,
            field_states=field_states,
            validation_issues=issues,
        )

    def clean_single_elo_row(
        self, row_idx: int, raw_row: Dict[str, str], prov: SourceProvenance
    ) -> CleanEloRecord:
        issues: List[ValidationIssue] = []
        raw_date = raw_row.get("date", "").strip()
        raw_club = raw_row.get("club", "").strip()
        raw_country = raw_row.get("country", "").strip() if raw_row.get("country") else None
        raw_elo_str = raw_row.get("elo")

        parsed_date, date_issue = parse_canonical_date(raw_date)
        if date_issue:
            issues.append(date_issue)

        if not raw_club:
            issues.append(ValidationIssue("ELO_CLUB_MISSING", "ERROR", "Elo club name is missing", "club"))

        elo_val, elo_st = parse_float_field(raw_elo_str)
        if elo_st == "INVALID" or elo_val is None or elo_val <= 0:
            issues.append(ValidationIssue("ELO_VALUE_INVALID", "ERROR", f"Invalid Elo rating '{raw_elo_str}'", "elo"))

        # Classification based on cutoff date
        if parsed_date and parsed_date > CLUB_ELO_VERIFIED_CUTOFF_DATE:
            classification = "PROVISIONAL_ESTIMATE"
        else:
            classification = "VERIFIED_HISTORICAL_ELO"

        norm_key = normalize_team_string(raw_club)
        if raw_club:
            self.unique_teams_requiring_stage8_review.add(raw_club)

        status = "QUARANTINED" if any(i.severity == "ERROR" for i in issues) else "ACCEPTED"

        return CleanEloRecord(
            record_status=status,
            provenance=prov,
            snapshot_date=parsed_date or raw_date,
            raw_club_name=raw_club,
            normalized_club_key=norm_key,
            country_code=raw_country,
            elo_rating=elo_val,
            classification=classification,
            validation_issues=issues,
        )

    def process_full_candidate_dataset(self) -> Dict[str, Any]:
        """
        Processes entire raw dataset streaming from Matches.csv and EloRatings.csv.
        Handles chunked streaming, duplicate detection, and builds full quality metrics report.
        """
        logger.info("Starting Stage 7 cleaning pipeline over full candidate dataset...")

        seen_match_keys: Dict[Tuple[str, str, str, str], CleanMatchRecord] = {}

        # 1. Stream Matches
        for idx, raw_row, prov in stream_raw_matches():
            self.match_metrics["total_raw"] += 1
            rec = self.clean_single_match_row(idx, raw_row, prov)

            if rec.record_status == "QUARANTINED":
                self.quarantined_matches.append(rec)
                self.match_metrics["quarantined"] += 1
                continue

            # Duplicate detection key: division + match_date + norm_home + norm_away
            div = rec.canonical_data.get("source_division_code", "")
            m_date = rec.canonical_data.get("match_date", "")
            h_key = rec.normalized_names.get("home_team_comparison_key", "")
            a_key = rec.normalized_names.get("away_team_comparison_key", "")

            m_key = (div, m_date, h_key, a_key)

            if m_key in seen_match_keys:
                self.duplicate_records_count += 1
                self.match_metrics["duplicates"] += 1
                existing_rec = seen_match_keys[m_key]

                # Check if exact duplicate in stats or suspicious
                if existing_rec.canonical_data == rec.canonical_data:
                    self.exact_duplicates_count += 1
                else:
                    self.suspicious_duplicates_count += 1

                # Quarantine duplicate to avoid unverified overwrites
                rec.record_status = "QUARANTINED"
                rec.validation_issues.append(
                    ValidationIssue("DUPLICATE_FIXTURE", "ERROR", f"Duplicate match fixture key {m_key}", "MatchFixture")
                )
                self.quarantined_matches.append(rec)
                continue

            seen_match_keys[m_key] = rec
            self.accepted_matches.append(rec)

            if rec.record_status == "ACCEPTED_WITH_WARNINGS":
                self.match_metrics["accepted_with_warnings"] += 1
            else:
                self.match_metrics["parsed_valid"] += 1

            # Track temporal boundaries
            if m_date:
                if not self.match_metrics["earliest_date"] or m_date < self.match_metrics["earliest_date"]:
                    self.match_metrics["earliest_date"] = m_date
                if not self.match_metrics["latest_date"] or m_date > self.match_metrics["latest_date"]:
                    self.match_metrics["latest_date"] = m_date

        # 2. Stream Elo Ratings
        for idx, raw_row, prov in stream_raw_elo_ratings():
            self.elo_metrics["total_raw"] += 1
            rec = self.clean_single_elo_row(idx, raw_row, prov)

            if rec.record_status == "QUARANTINED":
                self.quarantined_elo_records.append(rec)
                self.elo_metrics["quarantined"] += 1
            else:
                self.accepted_elo_records.append(rec)
                if rec.classification == "VERIFIED_HISTORICAL_ELO":
                    self.elo_metrics["verified_historical"] += 1
                else:
                    self.elo_metrics["provisional_estimates"] += 1

                e_date = rec.snapshot_date
                if e_date:
                    if not self.elo_metrics["earliest_date"] or e_date < self.elo_metrics["earliest_date"]:
                        self.elo_metrics["earliest_date"] = e_date
                    if not self.elo_metrics["latest_date"] or e_date > self.elo_metrics["latest_date"]:
                        self.elo_metrics["latest_date"] = e_date

        summary = {
            "pipeline_version": "v1.0.0-stage7",
            "matches": {
                "total_raw": self.match_metrics["total_raw"],
                "accepted_valid": len(self.accepted_matches),
                "accepted_with_warnings": self.match_metrics["accepted_with_warnings"],
                "quarantined": len(self.quarantined_matches),
                "duplicate_count": self.duplicate_records_count,
                "exact_duplicates": self.exact_duplicates_count,
                "suspicious_duplicates": self.suspicious_duplicates_count,
                "earliest_date": self.match_metrics["earliest_date"],
                "latest_date": self.match_metrics["latest_date"],
            },
            "elo": {
                "total_raw": self.elo_metrics["total_raw"],
                "accepted": len(self.accepted_elo_records),
                "verified_historical": self.elo_metrics["verified_historical"],
                "provisional_estimates": self.elo_metrics["provisional_estimates"],
                "quarantined": len(self.quarantined_elo_records),
                "earliest_date": self.elo_metrics["earliest_date"],
                "latest_date": self.elo_metrics["latest_date"],
            },
            "teams_requiring_stage8_review_count": len(self.unique_teams_requiring_stage8_review),
        }

        logger.info(f"Stage 7 Pipeline complete. Summary: {summary}")
        return summary
