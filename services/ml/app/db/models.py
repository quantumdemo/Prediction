import datetime
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def default_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(64), nullable=False)
    base_url = Column(String(512))
    license_notes = Column(Text)
    reliability_notes = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class CountryModel(Base):
    __tablename__ = "countries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(3), nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    region = Column(String(128))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class CompetitionModel(Base):
    __tablename__ = "competitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_id = Column(String(36), ForeignKey("countries.id", ondelete="RESTRICT"))
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    competition_type = Column(String(64), nullable=False)
    governing_body = Column(String(128))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class SeasonModel(Base):
    __tablename__ = "seasons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    competition_id = Column(
        String(36), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False
    )
    label = Column(String(32), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_current = Column(Boolean, nullable=False, default=False)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        UniqueConstraint("competition_id", "label", name="uq_competition_season"),
    )


class VenueModel(Base):
    __tablename__ = "venues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_id = Column(String(36), ForeignKey("countries.id", ondelete="SET NULL"))
    canonical_name = Column(String(255), nullable=False)
    city = Column(String(128))
    capacity = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class ClubModel(Base):
    __tablename__ = "clubs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_id = Column(
        String(36), ForeignKey("countries.id", ondelete="RESTRICT"), nullable=False
    )
    canonical_name = Column(String(255), nullable=False, unique=True)
    short_name = Column(String(128))
    city = Column(String(128))
    venue_id = Column(String(36), ForeignKey("venues.id", ondelete="SET NULL"))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class ClubAliasModel(Base):
    __tablename__ = "club_aliases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    alias_name = Column(String(255), nullable=False, unique=True)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"))
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class ClubExternalIdModel(Base):
    __tablename__ = "club_external_ids"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    external_id = Column(String(255), nullable=False)
    source_club_name = Column(String(255))
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_source_external_club"),
    )


class ClubSeasonMembershipModel(Base):
    __tablename__ = "club_season_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    competition_id = Column(
        String(36), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False
    )
    season_id = Column(
        String(36), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False
    )
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        UniqueConstraint("club_id", "season_id", name="uq_club_season"),
    )


class PlayerModel(Base):
    __tablename__ = "players"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_id = Column(String(36), ForeignKey("countries.id", ondelete="SET NULL"))
    canonical_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    position = Column(String(64))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class PlayerClubMembershipModel(Base):
    __tablename__ = "player_club_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id = Column(
        String(36), ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    season_id = Column(
        String(36), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False
    )
    shirt_number = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    competition_id = Column(
        String(36), ForeignKey("competitions.id", ondelete="RESTRICT"), nullable=False
    )
    season_id = Column(
        String(36), ForeignKey("seasons.id", ondelete="RESTRICT"), nullable=False
    )
    home_club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="RESTRICT"), nullable=False
    )
    away_club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="RESTRICT"), nullable=False
    )
    venue_id = Column(String(36), ForeignKey("venues.id", ondelete="SET NULL"))
    scheduled_kickoff_utc = Column(DateTime, nullable=False)
    actual_kickoff_utc = Column(DateTime)
    status = Column(String(32), nullable=False, default="SCHEDULED")
    home_score = Column(Integer)
    away_score = Column(Integer)
    validation_state = Column(String(32), nullable=False, default="UNVERIFIED")
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    updated_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        CheckConstraint("home_club_id <> away_club_id", name="chk_different_clubs"),
    )


class MatchExternalIdModel(Base):
    __tablename__ = "match_external_ids"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(
        String(36), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    external_match_id = Column(String(255), nullable=False)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        UniqueConstraint("source_id", "external_match_id", name="uq_source_external_match"),
    )


class MatchStatisticModel(Base):
    __tablename__ = "match_statistics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(
        String(36), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    club_id = Column(String(36), ForeignKey("clubs.id", ondelete="CASCADE"))
    stat_type = Column(String(64), nullable=False)
    stat_value = Column(Numeric, nullable=False)
    period = Column(String(32), nullable=False, default="FULL_TIME")
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"))
    validation_state = Column(String(32), nullable=False, default="VERIFIED")
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class MatchEventModel(Base):
    __tablename__ = "match_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(
        String(36), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    player_id = Column(String(36), ForeignKey("players.id", ondelete="SET NULL"))
    event_category = Column(String(64), nullable=False)
    minute = Column(Integer, nullable=False)
    extra_minute = Column(Integer)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"))
    validation_state = Column(String(32), nullable=False, default="VERIFIED")
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class MatchLineupModel(Base):
    __tablename__ = "match_lineups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(
        String(36), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    club_id = Column(
        String(36), ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    player_id = Column(
        String(36), ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(32), nullable=False, default="STARTING")
    position = Column(String(64))
    shirt_number = Column(Integer)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="SET NULL"))
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)

    __table_args__ = (
        UniqueConstraint("match_id", "player_id", "role", name="uq_match_player_role"),
    )


class RawSourcePayloadModel(Base):
    __tablename__ = "raw_source_payloads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(
        String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    entity_type = Column(String(64), nullable=False)
    external_identifier = Column(String(255), nullable=False)
    raw_payload_json = Column(Text, nullable=False)
    retrieved_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    ingestion_run_id = Column(String(36))


class ProvenanceRecordModel(Base):
    __tablename__ = "provenance_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(36), nullable=False)
    source_id = Column(
        String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    source_url = Column(String(512))
    retrieved_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    validation_state = Column(String(32), nullable=False, default="UNVERIFIED")
    notes = Column(Text)


class DatasetVersionModel(Base):
    __tablename__ = "dataset_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_label = Column(String(64), nullable=False, unique=True)
    cutoff_timestamp_utc = Column(DateTime, nullable=False)
    record_count = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)


class IngestionRunModel(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(
        String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    status = Column(String(32), nullable=False, default="STARTED")
    records_ingested = Column(Integer, nullable=False, default=0)
    error_log = Column(Text)
    started_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
    completed_at_utc = Column(DateTime)


class PredictionReportModel(Base):
    __tablename__ = "prediction_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id = Column(String(128), nullable=False, unique=True)
    fixture_id = Column(String(128), nullable=False)
    prediction_timestamp_utc = Column(DateTime, nullable=False)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(64), nullable=False)
    calibration_method = Column(String(64), nullable=False)
    decision_status = Column(String(64), nullable=False)
    report_payload_json = Column(Text, nullable=False)
    audit_hash = Column(String(64), nullable=False)
    created_at_utc = Column(DateTime, nullable=False, default=default_utc_now)
