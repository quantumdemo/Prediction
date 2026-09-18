"""
Stage 9 Feature Engineering Engine

Chronological, state-tracking feature calculation engine over canonical Stage 8 matches.
Guarantees zero future-data leakage by calculating pre-match features using ONLY matches < T.
Strictly isolates target variables from feature vectors.
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.data.stage8.pipeline import Stage8EntityResolutionPipelineEngine
from services.ml.app.features.registry import STAGE9_FEATURE_REGISTRY

logger = logging.getLogger("football_ml.features.engine")


@dataclass
class TeamMatchState:
    match_date_str: str
    match_date_obj: date
    is_home: bool
    opponent_club_id: str
    goals_scored: int
    goals_conceded: int
    points: int
    shots: Optional[int]
    shots_on_target: Optional[int]
    fouls: Optional[int]
    corners: Optional[int]
    yellow_cards: Optional[int]
    red_cards: Optional[int]
    clean_sheet: int
    failed_to_score: int
    btts: int
    elo_rating: Optional[float]


@dataclass
class MatchFeatureVector:
    fixture_id: str
    match_date: str
    competition_id: str
    season_id: str
    home_club_id: str
    away_club_id: str
    features: Dict[str, Optional[float]]
    feature_availability: Dict[str, str]  # PRESENT, MISSING_SOURCE_DATA, INSUFFICIENT_HISTORY, UNAVAILABLE, INVALID
    targets: Dict[str, Any]  # Isolated target variables for supervised learning
    feature_version: str = "STAGE9_FEATURE_DATASET_v1.0.0"


class Stage9FeatureEngine:
    """
    Production-oriented chronological feature calculation engine.
    """

    def __init__(self):
        self.stage8_engine = Stage8EntityResolutionPipelineEngine()
        self.team_history: Dict[str, List[TeamMatchState]] = {}  # club_id -> chronological past matches
        self.h2h_history: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}  # (club1, club2) -> past meetings

    def calculate_features_for_all_fixtures(self) -> List[MatchFeatureVector]:
        """
        Processes all Stage 8 canonical fixtures chronologically and generates pre-match features.
        Excludes target match outcome from its own features (Zero Future-Data Leakage).
        """
        logger.info("Starting Stage 9 Feature Calculation Engine...")

        summary = self.stage8_engine.process_full_entity_resolution()
        fixtures_dict = self.stage8_engine.fixture_resolver.fixtures

        # Sort fixtures strictly chronologically by match_date
        sorted_fixtures = sorted(fixtures_dict.values(), key=lambda f: f.match_date)

        feature_vectors: List[MatchFeatureVector] = []

        for f in sorted_fixtures:
            f_vector = self._generate_pre_match_features(f)
            feature_vectors.append(f_vector)

            # AFTER feature calculation, update chronological team states with match T outcome
            self._update_chronological_state(f)

        logger.info(f"Generated {len(feature_vectors)} pre-match feature vectors safely.")
        return feature_vectors

    def _generate_pre_match_features(self, fixture: Any) -> MatchFeatureVector:
        m_date = fixture.match_date
        h_id = fixture.home_club_id
        a_id = fixture.away_club_id
        stats = fixture.stats or {}

        # 1. Fetch pre-match chronological history (strictly < match T date)
        h_past = self.team_history.get(h_id, [])
        a_past = self.team_history.get(a_id, [])

        feats: Dict[str, Optional[float]] = {}
        avail: Dict[str, str] = {}

        curr_dt = datetime.strptime(m_date, "%Y-%m-%d").date()

        # Helper to set feature and availability
        def _set_feat(f_id: str, val: Optional[float], st: str):
            feats[f_id] = val
            avail[f_id] = st

        # --- 1. Form Features (6) ---
        if len(h_past) >= 3:
            _set_feat("FEAT_FORM3_HOME", float(sum(p.points for p in h_past[-3:])), "PRESENT")
        else:
            _set_feat("FEAT_FORM3_HOME", None, "INSUFFICIENT_HISTORY")

        if len(h_past) >= 5:
            _set_feat("FEAT_FORM5_HOME", float(sum(p.points for p in h_past[-5:])), "PRESENT")
        else:
            _set_feat("FEAT_FORM5_HOME", None, "INSUFFICIENT_HISTORY")

        if len(a_past) >= 3:
            _set_feat("FEAT_FORM3_AWAY", float(sum(p.points for p in a_past[-3:])), "PRESENT")
        else:
            _set_feat("FEAT_FORM3_AWAY", None, "INSUFFICIENT_HISTORY")

        if len(a_past) >= 5:
            _set_feat("FEAT_FORM5_AWAY", float(sum(p.points for p in a_past[-5:])), "PRESENT")
        else:
            _set_feat("FEAT_FORM5_AWAY", None, "INSUFFICIENT_HISTORY")

        if feats["FEAT_FORM3_HOME"] is not None and feats["FEAT_FORM3_AWAY"] is not None:
            _set_feat("FEAT_FORM3_DIFF", feats["FEAT_FORM3_HOME"] - feats["FEAT_FORM3_AWAY"], "PRESENT")
        else:
            _set_feat("FEAT_FORM3_DIFF", None, "INSUFFICIENT_HISTORY")

        if feats["FEAT_FORM5_HOME"] is not None and feats["FEAT_FORM5_AWAY"] is not None:
            _set_feat("FEAT_FORM5_DIFF", feats["FEAT_FORM5_HOME"] - feats["FEAT_FORM5_AWAY"], "PRESENT")
        else:
            _set_feat("FEAT_FORM5_DIFF", None, "INSUFFICIENT_HISTORY")

        # --- 2. Goals Features (6) ---
        if len(h_past) >= 5:
            _set_feat("FEAT_GOALS_SCORED_AVG5_HOME", float(sum(p.goals_scored for p in h_past[-5:]) / 5.0), "PRESENT")
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_HOME", float(sum(p.goals_conceded for p in h_past[-5:]) / 5.0), "PRESENT")
        else:
            _set_feat("FEAT_GOALS_SCORED_AVG5_HOME", None, "INSUFFICIENT_HISTORY")
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_HOME", None, "INSUFFICIENT_HISTORY")

        if len(a_past) >= 5:
            _set_feat("FEAT_GOALS_SCORED_AVG5_AWAY", float(sum(p.goals_scored for p in a_past[-5:]) / 5.0), "PRESENT")
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_AWAY", float(sum(p.goals_conceded for p in a_past[-5:]) / 5.0), "PRESENT")
        else:
            _set_feat("FEAT_GOALS_SCORED_AVG5_AWAY", None, "INSUFFICIENT_HISTORY")
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_AWAY", None, "INSUFFICIENT_HISTORY")

        if feats["FEAT_GOALS_SCORED_AVG5_HOME"] is not None and feats["FEAT_GOALS_SCORED_AVG5_AWAY"] is not None:
            _set_feat("FEAT_GOALS_SCORED_AVG5_DIFF", feats["FEAT_GOALS_SCORED_AVG5_HOME"] - feats["FEAT_GOALS_SCORED_AVG5_AWAY"], "PRESENT")
        else:
            _set_feat("FEAT_GOALS_SCORED_AVG5_DIFF", None, "INSUFFICIENT_HISTORY")

        if feats["FEAT_GOALS_CONCEDED_AVG5_HOME"] is not None and feats["FEAT_GOALS_CONCEDED_AVG5_AWAY"] is not None:
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_DIFF", feats["FEAT_GOALS_CONCEDED_AVG5_HOME"] - feats["FEAT_GOALS_CONCEDED_AVG5_AWAY"], "PRESENT")
        else:
            _set_feat("FEAT_GOALS_CONCEDED_AVG5_DIFF", None, "INSUFFICIENT_HISTORY")

        # --- 3. Rest Days & Fixture Congestion Features (13) ---
        if h_past:
            last_dt = h_past[-1].match_date_obj
            _set_feat("FEAT_REST_DAYS_HOME", float((curr_dt - last_dt).days), "PRESENT")
        else:
            _set_feat("FEAT_REST_DAYS_HOME", None, "INSUFFICIENT_HISTORY")

        if a_past:
            last_dt = a_past[-1].match_date_obj
            _set_feat("FEAT_REST_DAYS_AWAY", float((curr_dt - last_dt).days), "PRESENT")
        else:
            _set_feat("FEAT_REST_DAYS_AWAY", None, "INSUFFICIENT_HISTORY")

        if feats["FEAT_REST_DAYS_HOME"] is not None and feats["FEAT_REST_DAYS_AWAY"] is not None:
            _set_feat("FEAT_REST_DAYS_DIFF", feats["FEAT_REST_DAYS_HOME"] - feats["FEAT_REST_DAYS_AWAY"], "PRESENT")
        else:
            _set_feat("FEAT_REST_DAYS_DIFF", None, "INSUFFICIENT_HISTORY")

        # Fast congestion counters using reverse traversal
        def _get_congestion_counts(past: List[TeamMatchState]) -> Tuple[int, int, int]:
            c7, c14, c30 = 0, 0, 0
            for p in reversed(past):
                diff_days = (curr_dt - p.match_date_obj).days
                if diff_days <= 0:
                    continue
                if diff_days > 30:
                    break
                c30 += 1
                if diff_days <= 14:
                    c14 += 1
                if diff_days <= 7:
                    c7 += 1
            return c7, c14, c30

        h_7, h_14, h_30 = _get_congestion_counts(h_past)
        a_7, a_14, a_30 = _get_congestion_counts(a_past)

        _set_feat("FEAT_CONGESTION_7_HOME", float(h_7), "PRESENT")
        _set_feat("FEAT_CONGESTION_14_HOME", float(h_14), "PRESENT")
        _set_feat("FEAT_CONGESTION_30_HOME", float(h_30), "PRESENT")

        _set_feat("FEAT_CONGESTION_7_AWAY", float(a_7), "PRESENT")
        _set_feat("FEAT_CONGESTION_14_AWAY", float(a_14), "PRESENT")
        _set_feat("FEAT_CONGESTION_30_AWAY", float(a_30), "PRESENT")

        _set_feat("FEAT_CONGESTION_7_DIFF", float(h_7 - a_7), "PRESENT")
        _set_feat("FEAT_CONGESTION_14_DIFF", float(h_14 - a_14), "PRESENT")
        _set_feat("FEAT_CONGESTION_30_DIFF", float(h_30 - a_30), "PRESENT")

        # Fast reverse scanning helper for rolling statistics
        def _calc_rolling_source_stat_fast(team_past: List[TeamMatchState], stat_field: str, window: int = 5) -> Tuple[Optional[float], str]:
            if len(team_past) < window:
                return None, "INSUFFICIENT_HISTORY"
            vals = []
            for p in reversed(team_past):
                v = getattr(p, stat_field)
                if v is not None:
                    vals.append(v)
                    if len(vals) == window:
                        break
            if len(vals) < window:
                return None, "MISSING_SOURCE_DATA"
            avg_val = float(sum(vals) / float(window))
            return avg_val, "PRESENT"

        def _calc_diff(h_val: Optional[float], h_st: str, a_val: Optional[float], a_st: str) -> Tuple[Optional[float], str]:
            if h_st == "PRESENT" and a_st == "PRESENT" and h_val is not None and a_val is not None:
                return h_val - a_val, "PRESENT"
            if h_st == "INSUFFICIENT_HISTORY" or a_st == "INSUFFICIENT_HISTORY":
                return None, "INSUFFICIENT_HISTORY"
            return None, "MISSING_SOURCE_DATA"

        # --- 4. Shots Features (6) ---
        h_sh_val, h_sh_st = _calc_rolling_source_stat_fast(h_past, "shots", 5)
        a_sh_val, a_sh_st = _calc_rolling_source_stat_fast(a_past, "shots", 5)
        d_sh_val, d_sh_st = _calc_diff(h_sh_val, h_sh_st, a_sh_val, a_sh_st)
        _set_feat("FEAT_SHOTS_AVG5_HOME", h_sh_val, h_sh_st)
        _set_feat("FEAT_SHOTS_AVG5_AWAY", a_sh_val, a_sh_st)
        _set_feat("FEAT_SHOTS_AVG5_DIFF", d_sh_val, d_sh_st)

        h_st_val, h_st_st = _calc_rolling_source_stat_fast(h_past, "shots_on_target", 5)
        a_st_val, a_st_st = _calc_rolling_source_stat_fast(a_past, "shots_on_target", 5)
        d_st_val, d_st_st = _calc_diff(h_st_val, h_st_st, a_st_val, a_st_st)
        _set_feat("FEAT_SHOTS_TARGET_AVG5_HOME", h_st_val, h_st_st)
        _set_feat("FEAT_SHOTS_TARGET_AVG5_AWAY", a_st_val, a_st_st)
        _set_feat("FEAT_SHOTS_TARGET_AVG5_DIFF", d_st_val, d_st_st)

        # --- 5. Corners Features (3) ---
        h_co_val, h_co_st = _calc_rolling_source_stat_fast(h_past, "corners", 5)
        a_co_val, a_co_st = _calc_rolling_source_stat_fast(a_past, "corners", 5)
        d_co_val, d_co_st = _calc_diff(h_co_val, h_co_st, a_co_val, a_co_st)
        _set_feat("FEAT_CORNERS_AVG5_HOME", h_co_val, h_co_st)
        _set_feat("FEAT_CORNERS_AVG5_AWAY", a_co_val, a_co_st)
        _set_feat("FEAT_CORNERS_AVG5_DIFF", d_co_val, d_co_st)

        # --- 6. Fouls Features (3) ---
        h_fo_val, h_fo_st = _calc_rolling_source_stat_fast(h_past, "fouls", 5)
        a_fo_val, a_fo_st = _calc_rolling_source_stat_fast(a_past, "fouls", 5)
        d_fo_val, d_fo_st = _calc_diff(h_fo_val, h_fo_st, a_fo_val, a_fo_st)
        _set_feat("FEAT_FOULS_AVG5_HOME", h_fo_val, h_fo_st)
        _set_feat("FEAT_FOULS_AVG5_AWAY", a_fo_val, a_fo_st)
        _set_feat("FEAT_FOULS_AVG5_DIFF", d_fo_val, d_fo_st)

        # --- 7. Cards Features (6) ---
        h_yc_val, h_yc_st = _calc_rolling_source_stat_fast(h_past, "yellow_cards", 5)
        a_yc_val, a_yc_st = _calc_rolling_source_stat_fast(a_past, "yellow_cards", 5)
        d_yc_val, d_yc_st = _calc_diff(h_yc_val, h_yc_st, a_yc_val, a_yc_st)
        _set_feat("FEAT_YELLOW_CARDS_AVG5_HOME", h_yc_val, h_yc_st)
        _set_feat("FEAT_YELLOW_CARDS_AVG5_AWAY", a_yc_val, a_yc_st)
        _set_feat("FEAT_YELLOW_CARDS_AVG5_DIFF", d_yc_val, d_yc_st)

        h_rc_val, h_rc_st = _calc_rolling_source_stat_fast(h_past, "red_cards", 5)
        a_rc_val, a_rc_st = _calc_rolling_source_stat_fast(a_past, "red_cards", 5)
        d_rc_val, d_rc_st = _calc_diff(h_rc_val, h_rc_st, a_rc_val, a_rc_st)
        _set_feat("FEAT_RED_CARDS_AVG5_HOME", h_rc_val, h_rc_st)
        _set_feat("FEAT_RED_CARDS_AVG5_AWAY", a_rc_val, a_rc_st)
        _set_feat("FEAT_RED_CARDS_AVG5_DIFF", d_rc_val, d_rc_st)

        # --- 8. Clean-Sheet Features (3) ---
        if len(h_past) >= 5:
            h_cs_val = float(sum(p.clean_sheet for p in h_past[-5:]) / 5.0)
            h_cs_st = "PRESENT"
        else:
            h_cs_val, h_cs_st = None, "INSUFFICIENT_HISTORY"

        if len(a_past) >= 5:
            a_cs_val = float(sum(p.clean_sheet for p in a_past[-5:]) / 5.0)
            a_cs_st = "PRESENT"
        else:
            a_cs_val, a_cs_st = None, "INSUFFICIENT_HISTORY"

        d_cs_val, d_cs_st = _calc_diff(h_cs_val, h_cs_st, a_cs_val, a_cs_st)
        _set_feat("FEAT_CLEAN_SHEET_RATE5_HOME", h_cs_val, h_cs_st)
        _set_feat("FEAT_CLEAN_SHEET_RATE5_AWAY", a_cs_val, a_cs_st)
        _set_feat("FEAT_CLEAN_SHEET_RATE5_DIFF", d_cs_val, d_cs_st)

        # --- 9. Failed-To-Score Features (3) ---
        if len(h_past) >= 5:
            h_fts_val = float(sum(p.failed_to_score for p in h_past[-5:]) / 5.0)
            h_fts_st = "PRESENT"
        else:
            h_fts_val, h_fts_st = None, "INSUFFICIENT_HISTORY"

        if len(a_past) >= 5:
            a_fts_val = float(sum(p.failed_to_score for p in a_past[-5:]) / 5.0)
            a_fts_st = "PRESENT"
        else:
            a_fts_val, a_fts_st = None, "INSUFFICIENT_HISTORY"

        d_fts_val, d_fts_st = _calc_diff(h_fts_val, h_fts_st, a_fts_val, a_fts_st)
        _set_feat("FEAT_FAILED_TO_SCORE_RATE5_HOME", h_fts_val, h_fts_st)
        _set_feat("FEAT_FAILED_TO_SCORE_RATE5_AWAY", a_fts_val, a_fts_st)
        _set_feat("FEAT_FAILED_TO_SCORE_RATE5_DIFF", d_fts_val, d_fts_st)

        # --- 10. Historical BTTS Features (3) ---
        if len(h_past) >= 5:
            h_btts_val = float(sum(p.btts for p in h_past[-5:]) / 5.0)
            h_btts_st = "PRESENT"
        else:
            h_btts_val, h_btts_st = None, "INSUFFICIENT_HISTORY"

        if len(a_past) >= 5:
            a_btts_val = float(sum(p.btts for p in a_past[-5:]) / 5.0)
            a_btts_st = "PRESENT"
        else:
            a_btts_val, a_btts_st = None, "INSUFFICIENT_HISTORY"

        d_btts_val, d_btts_st = _calc_diff(h_btts_val, h_btts_st, a_btts_val, a_btts_st)
        _set_feat("FEAT_BTTS_RATE5_HOME", h_btts_val, h_btts_st)
        _set_feat("FEAT_BTTS_RATE5_AWAY", a_btts_val, a_btts_st)
        _set_feat("FEAT_BTTS_RATE5_DIFF", d_btts_val, d_btts_st)

        # --- 11. Head-to-Head (1) ---
        h2h_key = tuple(sorted([h_id, a_id]))
        past_h2h = self.h2h_history.get(h2h_key, [])
        h_wins = sum(1 for m in past_h2h if m["winner_club_id"] == h_id)
        _set_feat("FEAT_H2H_HOME_WINS", float(h_wins), "PRESENT" if past_h2h else "INSUFFICIENT_HISTORY")

        # --- 12. Pre-match Elo Features (3) ---
        h_elo = stats.get("home_elo")
        a_elo = stats.get("away_elo")

        # Fallback to last recorded team elo if available
        if h_elo is None and h_past:
            for p in reversed(h_past):
                if p.elo_rating is not None:
                    h_elo = p.elo_rating
                    break

        if a_elo is None and a_past:
            for p in reversed(a_past):
                if p.elo_rating is not None:
                    a_elo = p.elo_rating
                    break

        h_elo_val = float(h_elo) if h_elo is not None else None
        h_elo_st = "PRESENT" if h_elo_val is not None else "MISSING_SOURCE_DATA"

        a_elo_val = float(a_elo) if a_elo is not None else None
        a_elo_st = "PRESENT" if a_elo_val is not None else "MISSING_SOURCE_DATA"

        d_elo_val, d_elo_st = _calc_diff(h_elo_val, h_elo_st, a_elo_val, a_elo_st)

        _set_feat("FEAT_ELO_PRE_MATCH_HOME", h_elo_val, h_elo_st)
        _set_feat("FEAT_ELO_PRE_MATCH_AWAY", a_elo_val, a_elo_st)
        _set_feat("FEAT_ELO_PRE_MATCH_DIFF", d_elo_val, d_elo_st)

        # Ensure all registered features are populated
        for fid in STAGE9_FEATURE_REGISTRY:
            if fid not in feats:
                feats[fid] = None
                avail[fid] = "UNAVAILABLE"

        # --- Isolated Targets ---
        targets = {
            "full_time_home_goals": fixture.full_time_home_goals,
            "full_time_away_goals": fixture.full_time_away_goals,
            "full_time_result": fixture.full_time_result,
            "total_goals": fixture.full_time_home_goals + fixture.full_time_away_goals,
            "btts": bool(fixture.full_time_home_goals > 0 and fixture.full_time_away_goals > 0),
        }

        return MatchFeatureVector(
            fixture_id=fixture.id,
            match_date=m_date,
            competition_id=fixture.competition_id,
            season_id=fixture.season_id,
            home_club_id=h_id,
            away_club_id=a_id,
            features=feats,
            feature_availability=avail,
            targets=targets,
        )

    def _update_chronological_state(self, fixture: Any):
        m_date = fixture.match_date
        m_dt = datetime.strptime(m_date, "%Y-%m-%d").date()
        h_id = fixture.home_club_id
        a_id = fixture.away_club_id
        h_goals = fixture.full_time_home_goals
        a_goals = fixture.full_time_away_goals
        res = fixture.full_time_result
        stats = fixture.stats or {}

        h_pts = 3 if res == "H" else (1 if res == "D" else 0)
        a_pts = 3 if res == "A" else (1 if res == "D" else 0)

        h_cs = 1 if a_goals == 0 else 0
        a_cs = 1 if h_goals == 0 else 0

        h_fts = 1 if h_goals == 0 else 0
        a_fts = 1 if a_goals == 0 else 0

        match_btts = 1 if h_goals > 0 and a_goals > 0 else 0

        # Home team state update
        if h_id not in self.team_history:
            self.team_history[h_id] = []
        self.team_history[h_id].append(
            TeamMatchState(
                match_date_str=m_date,
                match_date_obj=m_dt,
                is_home=True,
                opponent_club_id=a_id,
                goals_scored=h_goals,
                goals_conceded=a_goals,
                points=h_pts,
                shots=stats.get("home_shots"),
                shots_on_target=stats.get("home_shots_on_target"),
                fouls=stats.get("home_fouls"),
                corners=stats.get("home_corners"),
                yellow_cards=stats.get("home_yellow_cards"),
                red_cards=stats.get("home_red_cards"),
                clean_sheet=h_cs,
                failed_to_score=h_fts,
                btts=match_btts,
                elo_rating=stats.get("home_elo"),
            )
        )

        # Away team state update
        if a_id not in self.team_history:
            self.team_history[a_id] = []
        self.team_history[a_id].append(
            TeamMatchState(
                match_date_str=m_date,
                match_date_obj=m_dt,
                is_home=False,
                opponent_club_id=h_id,
                goals_scored=a_goals,
                goals_conceded=h_goals,
                points=a_pts,
                shots=stats.get("away_shots"),
                shots_on_target=stats.get("away_shots_on_target"),
                fouls=stats.get("away_fouls"),
                corners=stats.get("away_corners"),
                yellow_cards=stats.get("away_yellow_cards"),
                red_cards=stats.get("away_red_cards"),
                clean_sheet=a_cs,
                failed_to_score=a_fts,
                btts=match_btts,
                elo_rating=stats.get("away_elo"),
            )
        )

        # H2H history update
        h2h_key = tuple(sorted([h_id, a_id]))
        if h2h_key not in self.h2h_history:
            self.h2h_history[h2h_key] = []
        winner = h_id if res == "H" else (a_id if res == "A" else None)
        self.h2h_history[h2h_key].append(
            {
                "match_date": m_date,
                "winner_club_id": winner,
                "home_goals": h_goals,
                "away_goals": a_goals,
            }
        )
