import datetime
import os
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
contracts_dir = os.path.join(ROOT_DIR, "packages/contracts/python")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if contracts_dir not in sys.path:
    sys.path.insert(0, contracts_dir)

import football_contracts as contracts  # noqa: E402

from services.ml.app.db.models import (  # noqa: E402
    Base,
    ClubExternalIdModel,
    ClubModel,
    CompetitionModel,
    CountryModel,
    MatchModel,
    ProvenanceRecordModel,
    SeasonModel,
    SourceModel,
)


class TestStage4DatabaseSchema(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def test_unique_canonical_club_constraint(self):
        session = self.Session()
        country = CountryModel(code="ENG", name="England")
        session.add(country)
        session.commit()

        club1 = ClubModel(country_id=country.id, canonical_name="Arsenal FC")
        session.add(club1)
        session.commit()

        club2 = ClubModel(country_id=country.id, canonical_name="Arsenal FC")
        session.add(club2)
        with self.assertRaises(IntegrityError):
            session.commit()
        session.rollback()
        session.close()

    def test_unique_external_club_id_per_source(self):
        session = self.Session()
        country = CountryModel(code="ENG", name="England")
        source = SourceModel(code="API_FOOTBALL", name="API-Football", source_type="API")
        session.add_all([country, source])
        session.commit()

        club = ClubModel(country_id=country.id, canonical_name="Liverpool FC")
        session.add(club)
        session.commit()

        ext1 = ClubExternalIdModel(
            club_id=club.id, source_id=source.id, external_id="40", source_club_name="Liverpool"
        )
        session.add(ext1)
        session.commit()

        ext2 = ClubExternalIdModel(
            club_id=club.id, source_id=source.id, external_id="40", source_club_name="Liverpool"
        )
        session.add(ext2)
        with self.assertRaises(IntegrityError):
            session.commit()
        session.rollback()
        session.close()

    def test_different_home_and_away_club_constraint(self):
        session = self.Session()
        country = CountryModel(code="ESP", name="Spain")
        session.add(country)
        session.commit()

        comp = CompetitionModel(
            country_id=country.id, code="LALIGA", name="La Liga", competition_type="LEAGUE"
        )
        session.add(comp)
        session.commit()

        season = SeasonModel(competition_id=comp.id, label="2024/2025")
        club = ClubModel(country_id=country.id, canonical_name="Real Madrid CF")
        session.add_all([season, club])
        session.commit()

        # Match with same home and away club
        match = MatchModel(
            competition_id=comp.id,
            season_id=season.id,
            home_club_id=club.id,
            away_club_id=club.id,
            scheduled_kickoff_utc=datetime.datetime.now(datetime.timezone.utc),
        )
        session.add(match)
        with self.assertRaises(IntegrityError):
            session.commit()
        session.rollback()
        session.close()

    def test_validation_states_and_provenance(self):
        session = self.Session()
        source = SourceModel(code="FD_UK", name="Football-Data.co.uk", source_type="CSV")
        session.add(source)
        session.commit()

        # Create provenance record
        prov = ProvenanceRecordModel(
            entity_type="MATCH",
            entity_id="test-match-uuid",
            source_id=source.id,
            source_url="https://www.football-data.co.uk/mmz4281/2425/E0.csv",
            validation_state=contracts.ValidationState.VERIFIED.value,
        )
        session.add(prov)
        session.commit()

        retrieved = session.query(ProvenanceRecordModel).filter_by(id=prov.id).first()
        self.assertEqual(retrieved.validation_state, "VERIFIED")
        self.assertEqual(
            retrieved.source_url, "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
        )
        session.close()

    def test_contract_pydantic_serialization(self):
        club_contract = contracts.Club(
            id="club-123",
            country_id="ctry-456",
            canonical_name="Bayern Munich",
            short_name="Bayern",
            is_active=True,
        )
        dumped = club_contract.model_dump()
        self.assertEqual(dumped["canonical_name"], "Bayern Munich")
        self.assertEqual(dumped["is_active"], True)

        reloaded = contracts.Club(**dumped)
        self.assertEqual(reloaded.id, "club-123")


if __name__ == "__main__":
    unittest.main()
