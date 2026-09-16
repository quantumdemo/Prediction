import datetime
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.ml.app.db.models import (
    Base,
    ClubAliasModel,
    ClubModel,
    CompetitionModel,
    CountryModel,
    MatchModel,
    SeasonModel,
    SourceModel,
)


class TestORMModels(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def test_orm_table_creation_and_query(self):
        session = self.Session()

        # Insert source
        source = SourceModel(
            code="OPENFOOTBALL",
            name="OpenFootball Clubs Repository",
            source_type="PUBLIC_REPO",
            license_notes="CC0 Public Domain"
        )
        session.add(source)

        # Insert country
        country = CountryModel(code="ENG", name="England", region="Europe")
        session.add(country)
        session.commit()

        # Insert competition
        comp = CompetitionModel(
            country_id=country.id,
            code="PL",
            name="Premier League",
            competition_type="LEAGUE"
        )
        session.add(comp)
        session.commit()

        # Insert season
        season = SeasonModel(
            competition_id=comp.id,
            label="2024/2025",
            is_current=True
        )
        session.add(season)

        # Insert clubs
        club1 = ClubModel(country_id=country.id, canonical_name="Arsenal FC", short_name="Arsenal")
        club2 = ClubModel(country_id=country.id, canonical_name="Chelsea FC", short_name="Chelsea")
        session.add_all([club1, club2])
        session.commit()

        # Insert alias
        alias = ClubAliasModel(club_id=club1.id, alias_name="Gunners", source_id=source.id)
        session.add(alias)

        # Insert match
        match = MatchModel(
            competition_id=comp.id,
            season_id=season.id,
            home_club_id=club1.id,
            away_club_id=club2.id,
            scheduled_kickoff_utc=datetime.datetime.now(datetime.timezone.utc),
            status="SCHEDULED",
            validation_state="VERIFIED"
        )
        session.add(match)
        session.commit()

        # Query and assertions
        retrieved_match = session.query(MatchModel).filter_by(id=match.id).first()
        self.assertIsNotNone(retrieved_match)
        self.assertEqual(retrieved_match.home_club_id, club1.id)
        self.assertEqual(retrieved_match.status, "SCHEDULED")

        retrieved_alias = session.query(ClubAliasModel).filter_by(alias_name="Gunners").first()
        self.assertIsNotNone(retrieved_alias)
        self.assertEqual(retrieved_alias.club_id, club1.id)

        session.close()

if __name__ == "__main__":
    unittest.main()
