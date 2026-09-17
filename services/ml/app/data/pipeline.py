import datetime
import json
import logging
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from services.ml.app.data.adapters.football_data_uk import (
    LEAGUE_MAP,
    SEASON_MAP,
    FootballDataUKAdapter,
)
from services.ml.app.data.adapters.openfootball_reference import (
    OpenFootballReferenceAdapter,
)
from services.ml.app.db.models import (
    ClubAliasModel,
    ClubExternalIdModel,
    ClubModel,
    ClubSeasonMembershipModel,
    CompetitionModel,
    CountryModel,
    DatasetVersionModel,
    IngestionRunModel,
    MatchModel,
    MatchStatisticModel,
    ProvenanceRecordModel,
    RawSourcePayloadModel,
    SeasonModel,
    SourceModel,
)

logger = logging.getLogger("football_ml.data.pipeline")


class HistoricalIngestionPipeline:
    """
    Historical Dataset Ingestion Pipeline Manager (Stage 6)

    Handles idempotent acquisition, raw payload preservation, entity mapping,
    canonical match persistence, statistics storage, and dataset snapshot versioning.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.fd_adapter = FootballDataUKAdapter()
        self.of_adapter = OpenFootballReferenceAdapter()

    def ensure_sources_registered(self) -> Dict[str, str]:
        source_records = [
            {
                "code": "FOOTBALL_DATA_UK",
                "name": "Football-Data.co.uk",
                "source_type": "BULK_CSV",
                "base_url": "https://www.football-data.co.uk/mmz4281",
                "license_notes": "Open Data / Citation Required",
            },
            {
                "code": "OPENFOOTBALL",
                "name": "OpenFootball Clubs Repository",
                "source_type": "PUBLIC_REPO",
                "base_url": "https://raw.githubusercontent.com/openfootball/clubs/master",
                "license_notes": "CC0 Public Domain",
            },
            {
                "code": "API_FOOTBALL",
                "name": "API-Football / API-Sports",
                "source_type": "REST_API",
                "base_url": "https://v3.football.api-sports.io",
                "license_notes": "Commercial Subscription API",
            },
        ]

        source_map = {}
        for src in source_records:
            existing = (
                self.db.query(SourceModel).filter_by(code=src["code"]).first()
            )
            if not existing:
                existing = SourceModel(
                    code=src["code"],
                    name=src["name"],
                    source_type=src["source_type"],
                    base_url=src["base_url"],
                    license_notes=src["license_notes"],
                )
                self.db.add(existing)
                self.db.commit()
                self.db.refresh(existing)
            source_map[src["code"]] = existing.id

        return source_map

    def ensure_reference_entities(self, source_map: Dict[str, str]):
        countries_data = [
            ("ENG", "England", "Europe"),
            ("ESP", "Spain", "Europe"),
            ("ITA", "Italy", "Europe"),
            ("GER", "Germany", "Europe"),
            ("FRA", "France", "Europe"),
        ]
        country_map = {}
        for code, name, region in countries_data:
            c = self.db.query(CountryModel).filter_by(code=code).first()
            if not c:
                c = CountryModel(code=code, name=name, region=region)
                self.db.add(c)
                self.db.commit()
                self.db.refresh(c)
            country_map[code] = c.id

        comp_map = {}
        season_map = {}
        for comp_code, comp_info in LEAGUE_MAP.items():
            ctry_id = country_map.get(comp_info["country"])
            comp = (
                self.db.query(CompetitionModel)
                .filter_by(code=comp_code)
                .first()
            )
            if not comp:
                comp = CompetitionModel(
                    country_id=ctry_id,
                    code=comp_code,
                    name=comp_info["name"],
                    competition_type="LEAGUE",
                )
                self.db.add(comp)
                self.db.commit()
                self.db.refresh(comp)
            comp_map[comp_code] = comp.id

            for s_label in SEASON_MAP.keys():
                s = (
                    self.db.query(SeasonModel)
                    .filter_by(competition_id=comp.id, label=s_label)
                    .first()
                )
                if not s:
                    s = SeasonModel(
                        competition_id=comp.id,
                        label=s_label,
                        is_current=(s_label == "2024/2025"),
                    )
                    self.db.add(s)
                    self.db.commit()
                    self.db.refresh(s)
                season_map[(comp_code, s_label)] = s.id

        of_source_id = source_map.get("OPENFOOTBALL")
        for club_ref in self.of_adapter.load_reference_clubs():
            ctry_id = country_map.get(club_ref["country_code"])
            c = (
                self.db.query(ClubModel)
                .filter_by(canonical_name=club_ref["canonical_name"])
                .first()
            )
            if not c and ctry_id:
                c = ClubModel(
                    country_id=ctry_id,
                    canonical_name=club_ref["canonical_name"],
                    short_name=club_ref["short_name"],
                    city=club_ref["city"],
                )
                self.db.add(c)
                self.db.commit()
                self.db.refresh(c)

            if c and of_source_id:
                for alias_name in club_ref["aliases"]:
                    alias = (
                        self.db.query(ClubAliasModel)
                        .filter_by(alias_name=alias_name)
                        .first()
                    )
                    if not alias:
                        alias = ClubAliasModel(
                            club_id=c.id,
                            alias_name=alias_name,
                            source_id=of_source_id,
                        )
                        self.db.add(alias)
                self.db.commit()

        return country_map, comp_map, season_map

    def resolve_or_create_club(
        self, team_name: str, country_id: str, source_id: str
    ) -> str:
        clean_name = team_name.strip()

        club = (
            self.db.query(ClubModel)
            .filter_by(canonical_name=clean_name)
            .first()
        )
        if club:
            return club.id

        alias = (
            self.db.query(ClubAliasModel)
            .filter_by(alias_name=clean_name)
            .first()
        )
        if alias:
            return alias.club_id

        ext = (
            self.db.query(ClubExternalIdModel)
            .filter_by(source_id=source_id, source_club_name=clean_name)
            .first()
        )
        if ext:
            return ext.club_id

        new_club = ClubModel(
            country_id=country_id,
            canonical_name=clean_name,
            short_name=clean_name,
        )
        self.db.add(new_club)
        self.db.commit()
        self.db.refresh(new_club)

        new_alias = ClubAliasModel(
            club_id=new_club.id, alias_name=clean_name, source_id=source_id
        )
        new_ext = ClubExternalIdModel(
            club_id=new_club.id,
            source_id=source_id,
            external_id=f"fd-{clean_name.lower().replace(' ', '-')}",
            source_club_name=clean_name,
        )
        self.db.add_all([new_alias, new_ext])
        self.db.commit()

        return new_club.id

    def ensure_club_season_membership(
        self, club_id: str, competition_id: str, season_id: str
    ):
        """
        Idempotently registers historical club-season membership relationship.
        """
        existing = (
            self.db.query(ClubSeasonMembershipModel)
            .filter_by(club_id=club_id, season_id=season_id)
            .first()
        )
        if not existing:
            mship = ClubSeasonMembershipModel(
                club_id=club_id,
                competition_id=competition_id,
                season_id=season_id,
            )
            self.db.add(mship)
            self.db.commit()

    def run_historical_ingestion(
        self,
        competitions: List[str] = None,
        seasons: List[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        if competitions is None:
            competitions = ["EPL", "LALIGA", "SERIEA", "BUNDESLIGA", "LIGUE1"]
        if seasons is None:
            seasons = list(SEASON_MAP.keys())

        source_map = self.ensure_sources_registered()
        fd_source_id = source_map["FOOTBALL_DATA_UK"]

        country_map, comp_map, season_map = self.ensure_reference_entities(
            source_map
        )

        ingestion_run = IngestionRunModel(
            source_id=fd_source_id,
            status="RUNNING",
            started_at_utc=datetime.datetime.now(datetime.timezone.utc),
        )
        self.db.add(ingestion_run)
        self.db.commit()
        self.db.refresh(ingestion_run)

        run_id = ingestion_run.id
        total_discovered = 0
        total_accepted = 0
        total_duplicates = 0
        total_rejected = 0
        coverage_by_comp = {}

        for comp_code in competitions:
            if comp_code not in LEAGUE_MAP:
                continue
            comp_id = comp_map[comp_code]
            ctry_code = LEAGUE_MAP[comp_code]["country"]
            ctry_id = country_map[ctry_code]

            comp_accepted = 0

            for s_label in seasons:
                if s_label not in SEASON_MAP:
                    continue
                s_id = season_map[(comp_code, s_label)]

                success, msg, records, url = (
                    self.fd_adapter.fetch_season_league_data(
                        comp_code, s_label
                    )
                )

                if not success or not records:
                    logger.warning(
                        f"No records retrieved for {comp_code} {s_label}: {msg}"
                    )
                    continue

                raw_entry = self.fd_adapter.create_raw_payload_entry(
                    source_id=fd_source_id,
                    entity_type="MATCH_BATCH_CSV",
                    external_identifier=f"{comp_code}-{s_label}",
                    raw_payload_json=json.dumps(
                        {"count": len(records), "url": url}
                    ),
                    ingestion_run_id=run_id,
                )
                raw_model = RawSourcePayloadModel(**raw_entry)
                self.db.add(raw_model)

                prov_entry = self.fd_adapter.create_provenance_entry(
                    entity_type="BATCH_CSV",
                    entity_id=raw_model.id,
                    source_id=fd_source_id,
                    source_url=url,
                    validation_state="VERIFIED",
                    notes=f"Fetched {len(records)} records for {comp_code} {s_label}",
                )
                self.db.add(ProvenanceRecordModel(**prov_entry))
                self.db.commit()

                for rec in records:
                    total_discovered += 1

                    home_club_id = self.resolve_or_create_club(
                        rec["home_team"], ctry_id, fd_source_id
                    )
                    away_club_id = self.resolve_or_create_club(
                        rec["away_team"], ctry_id, fd_source_id
                    )

                    if home_club_id == away_club_id:
                        total_rejected += 1
                        continue

                    # Maintain club-season memberships deterministically
                    self.ensure_club_season_membership(
                        home_club_id, comp_id, s_id
                    )
                    self.ensure_club_season_membership(
                        away_club_id, comp_id, s_id
                    )

                    existing_match = (
                        self.db.query(MatchModel)
                        .filter_by(
                            competition_id=comp_id,
                            season_id=s_id,
                            home_club_id=home_club_id,
                            away_club_id=away_club_id,
                            scheduled_kickoff_utc=rec["kickoff_utc"],
                        )
                        .first()
                    )

                    if existing_match:
                        total_duplicates += 1
                        match_obj = existing_match
                        match_obj.home_score = rec["home_score"]
                        match_obj.away_score = rec["away_score"]
                        match_obj.status = "COMPLETED"
                        match_obj.validation_state = "VERIFIED"
                    else:
                        match_obj = MatchModel(
                            competition_id=comp_id,
                            season_id=s_id,
                            home_club_id=home_club_id,
                            away_club_id=away_club_id,
                            scheduled_kickoff_utc=rec["kickoff_utc"],
                            status="COMPLETED",
                            home_score=rec["home_score"],
                            away_score=rec["away_score"],
                            validation_state="VERIFIED",
                        )
                        self.db.add(match_obj)
                        self.db.commit()
                        self.db.refresh(match_obj)
                        total_accepted += 1
                        comp_accepted += 1

                    self._persist_match_stats(
                        match_obj.id,
                        home_club_id,
                        away_club_id,
                        rec["stats"],
                        fd_source_id,
                    )

                self.db.commit()

            coverage_by_comp[comp_code] = comp_accepted

        ingestion_run.status = "COMPLETED"
        ingestion_run.records_ingested = total_accepted
        ingestion_run.completed_at_utc = datetime.datetime.now(
            datetime.timezone.utc
        )
        self.db.commit()

        timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        dataset_ver = DatasetVersionModel(
            version_label=f"v1.0-historical-{timestamp_str}",
            cutoff_timestamp_utc=datetime.datetime.now(
                datetime.timezone.utc
            ),
            record_count=total_accepted,
            notes=f"Historical dataset ingested via pipeline run {run_id}",
        )
        self.db.add(dataset_ver)
        self.db.commit()

        summary = {
            "run_id": run_id,
            "status": "COMPLETED",
            "total_discovered": total_discovered,
            "total_accepted": total_accepted,
            "total_duplicates": total_duplicates,
            "total_rejected": total_rejected,
            "coverage_by_competition": coverage_by_comp,
            "dataset_version": dataset_ver.version_label,
        }

        logger.info(f"Ingestion run completed summary: {summary}")
        return run_id, summary

    def _persist_match_stats(
        self,
        match_id: str,
        home_club_id: str,
        away_club_id: str,
        stats: Dict[str, Any],
        source_id: str,
    ):
        stat_mappings = [
            ("home_shots", home_club_id, "SHOTS"),
            ("away_shots", away_club_id, "SHOTS"),
            ("home_shots_on_target", home_club_id, "SHOTS_ON_TARGET"),
            ("away_shots_on_target", away_club_id, "SHOTS_ON_TARGET"),
            ("home_corners", home_club_id, "CORNERS"),
            ("away_corners", away_club_id, "CORNERS"),
            ("home_fouls", home_club_id, "FOULS"),
            ("away_fouls", away_club_id, "FOULS"),
            ("home_yellow_cards", home_club_id, "YELLOW_CARDS"),
            ("away_yellow_cards", away_club_id, "YELLOW_CARDS"),
            ("home_red_cards", home_club_id, "RED_CARDS"),
            ("away_red_cards", away_club_id, "RED_CARDS"),
        ]

        for key, club_id, stat_type in stat_mappings:
            val = stats.get(key)
            if val is None:
                continue

            existing = (
                self.db.query(MatchStatisticModel)
                .filter_by(
                    match_id=match_id, club_id=club_id, stat_type=stat_type
                )
                .first()
            )

            if existing:
                existing.stat_value = val
            else:
                stat_obj = MatchStatisticModel(
                    match_id=match_id,
                    club_id=club_id,
                    stat_type=stat_type,
                    stat_value=val,
                    period="FULL_TIME",
                    source_id=source_id,
                    validation_state="VERIFIED",
                )
                self.db.add(stat_obj)
