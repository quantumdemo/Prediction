"""
Stage 9 Feature Engineering Engine

Chronological, state-tracking feature calculation engine over canonical Stage 8 matches.
Guarantees zero future-data leakage by calculating pre-match features using ONLY matches < T.
Strictly isolates target variables from feature vectors.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.data.stage8.pipeline import Stage8EntityResolutionPipelineEngine

logger = logging.getLogger("football_ml.features.engine")


@dataclass
class TeamMatchState:
    match_date: str
    is_home: bool
    opponent_club_id: str
    goals_scored: int
    goals_conceded: int
    points: int
    shots: Optional[int]
    shots_on_target: Optional[int]


@dataclass
class MatchFeatureVector:
    fixture_id: str
    match_date: str
    competition_id: str
    season_id: str
    home_club_id: str
    away_club_id: str
    features: Dict[str, Optional[float]]
    feature_availability: Dict[str, str]  # PRESENT, MISSING, INSUFFICIENT_HISTORY
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

        # 1. Fetch pre-match chronological history (strictly < match T date)
        h_past = self.team_history.get(h_id, [])
        a_past = self.team_history.get(a_id, [])

        feats: Dict[str, Optional[float]] = {}
        avail: Dict[str, str] = {}

        # --- Recalculated Form Features ---
        # Form3 & Form5 Home
        if len(h_past) >= 3:
            feats["FEAT_FORM3_HOME"] = float(sum(p.points for p in h_past[-3:]))
            avail["FEAT_FORM3_HOME"] = "PRESENT"
        else:
            feats["FEAT_FORM3_HOME"] = None
            avail["FEAT_FORM3_HOME"] = "INSUFFICIENT_HISTORY"

        if len(h_past) >= 5:
            feats["FEAT_FORM5_HOME"] = float(sum(p.points for p in h_past[-5:]))
            avail["FEAT_FORM5_HOME"] = "PRESENT"
        else:
            feats["FEAT_FORM5_HOME"] = None
            avail["FEAT_FORM5_HOME"] = "INSUFFICIENT_HISTORY"

        # Form3 & Form5 Away
        if len(a_past) >= 3:
            feats["FEAT_FORM3_AWAY"] = float(sum(p.points for p in a_past[-3:]))
            avail["FEAT_FORM3_AWAY"] = "PRESENT"
        else:
            feats["FEAT_FORM3_AWAY"] = None
            avail["FEAT_FORM3_AWAY"] = "INSUFFICIENT_HISTORY"

        if len(a_past) >= 5:
            feats["FEAT_FORM5_AWAY"] = float(sum(p.points for p in a_past[-5:]))
            avail["FEAT_FORM5_AWAY"] = "PRESENT"
        else:
            feats["FEAT_FORM5_AWAY"] = None
            avail["FEAT_FORM5_AWAY"] = "INSUFFICIENT_HISTORY"

        # Form Differences
        if feats["FEAT_FORM3_HOME"] is not None and feats["FEAT_FORM3_AWAY"] is not None:
            feats["FEAT_FORM3_DIFF"] = feats["FEAT_FORM3_HOME"] - feats["FEAT_FORM3_AWAY"]
            avail["FEAT_FORM3_DIFF"] = "PRESENT"
        else:
            feats["FEAT_FORM3_DIFF"] = None
            avail["FEAT_FORM3_DIFF"] = "INSUFFICIENT_HISTORY"

        if feats["FEAT_FORM5_HOME"] is not None and feats["FEAT_FORM5_AWAY"] is not None:
            feats["FEAT_FORM5_DIFF"] = feats["FEAT_FORM5_HOME"] - feats["FEAT_FORM5_AWAY"]
            avail["FEAT_FORM5_DIFF"] = "PRESENT"
        else:
            feats["FEAT_FORM5_DIFF"] = None
            avail["FEAT_FORM5_DIFF"] = "INSUFFICIENT_HISTORY"

        # --- Goal Averages ---
        if len(h_past) >= 5:
            feats["FEAT_GOALS_SCORED_AVG5_HOME"] = float(sum(p.goals_scored for p in h_past[-5:]) / 5.0)
            feats["FEAT_GOALS_CONCEDED_AVG5_HOME"] = float(sum(p.goals_conceded for p in h_past[-5:]) / 5.0)
            avail["FEAT_GOALS_SCORED_AVG5_HOME"] = "PRESENT"
            avail["FEAT_GOALS_CONCEDED_AVG5_HOME"] = "PRESENT"
        else:
            feats["FEAT_GOALS_SCORED_AVG5_HOME"] = None
            feats["FEAT_GOALS_CONCEDED_AVG5_HOME"] = None
            avail["FEAT_GOALS_SCORED_AVG5_HOME"] = "INSUFFICIENT_HISTORY"
            avail["FEAT_GOALS_CONCEDED_AVG5_HOME"] = "INSUFFICIENT_HISTORY"

        if len(a_past) >= 5:
            feats["FEAT_GOALS_SCORED_AVG5_AWAY"] = float(sum(p.goals_scored for p in a_past[-5:]) / 5.0)
            feats["FEAT_GOALS_CONCEDED_AVG5_AWAY"] = float(sum(p.goals_conceded for p in a_past[-5:]) / 5.0)
            avail["FEAT_GOALS_SCORED_AVG5_AWAY"] = "PRESENT"
            avail["FEAT_GOALS_CONCEDED_AVG5_AWAY"] = "PRESENT"
        else:
            feats["FEAT_GOALS_SCORED_AVG5_AWAY"] = None
            feats["FEAT_GOALS_CONCEDED_AVG5_AWAY"] = None
            avail["FEAT_GOALS_SCORED_AVG5_AWAY"] = "INSUFFICIENT_HISTORY"
            avail["FEAT_GOALS_CONCEDED_AVG5_AWAY"] = "INSUFFICIENT_HISTORY"

        # --- Rest Days ---
        if h_past:
            last_dt = datetime.strptime(h_past[-1].match_date, "%Y-%m-%d")
            curr_dt = datetime.strptime(m_date, "%Y-%m-%d")
            feats["FEAT_REST_DAYS_HOME"] = float((curr_dt - last_dt).days)
            avail["FEAT_REST_DAYS_HOME"] = "PRESENT"
        else:
            feats["FEAT_REST_DAYS_HOME"] = None
            avail["FEAT_REST_DAYS_HOME"] = "INSUFFICIENT_HISTORY"

        if a_past:
            last_dt = datetime.strptime(a_past[-1].match_date, "%Y-%m-%d")
            curr_dt = datetime.strptime(m_date, "%Y-%m-%d")
            feats["FEAT_REST_DAYS_AWAY"] = float((curr_dt - last_dt).days)
            avail["FEAT_REST_DAYS_AWAY"] = "PRESENT"
        else:
            feats["FEAT_REST_DAYS_AWAY"] = None
            avail["FEAT_REST_DAYS_AWAY"] = "INSUFFICIENT_HISTORY"

        # --- Head-to-Head ---
        h2h_key = tuple(sorted([h_id, a_id]))
        past_h2h = self.h2h_history.get(h2h_key, [])
        h_wins = sum(1 for m in past_h2h if m["winner_club_id"] == h_id)
        feats["FEAT_H2H_HOME_WINS"] = float(h_wins)
        avail["FEAT_H2H_HOME_WINS"] = "PRESENT" if past_h2h else "INSUFFICIENT_HISTORY"

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
        h_id = fixture.home_club_id
        a_id = fixture.away_club_id
        h_goals = fixture.full_time_home_goals
        a_goals = fixture.full_time_away_goals
        res = fixture.full_time_result

        h_pts = 3 if res == "H" else (1 if res == "D" else 0)
        a_pts = 3 if res == "A" else (1 if res == "D" else 0)

        # Home team state update
        if h_id not in self.team_history:
            self.team_history[h_id] = []
        self.team_history[h_id].append(
            TeamMatchState(
                match_date=m_date,
                is_home=True,
                opponent_club_id=a_id,
                goals_scored=h_goals,
                goals_conceded=a_goals,
                points=h_pts,
                shots=None,
                shots_on_target=None,
            )
        )

        # Away team state update
        if a_id not in self.team_history:
            self.team_history[a_id] = []
        self.team_history[a_id].append(
            TeamMatchState(
                match_date=m_date,
                is_home=False,
                opponent_club_id=h_id,
                goals_scored=a_goals,
                goals_conceded=h_goals,
                points=a_pts,
                shots=None,
                shots_on_target=None,
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
