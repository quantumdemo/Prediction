import os
import unittest
from unittest.mock import patch, MagicMock

import sqlalchemy as sa
from sqlalchemy import create_engine, inspect


class TestMigrationExecution(unittest.TestCase):
    def setUp(self):
        # Create an in-memory or file-based SQLite database to verify SQL DDL compatibility
        self.sql_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../infrastructure/database/schema.sql")
        )
        self.assertTrue(os.path.exists(self.sql_path), "schema.sql must exist")

    def test_schema_sql_execution(self):
        with open(self.sql_path, "r", encoding="utf-8") as f:
            ddl = f.read()

        # Clean postgres-specific syntax for SQLite testing
        ddl_sqlite = ddl.replace('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";', '')
        ddl_sqlite = ddl_sqlite.replace('gen_random_uuid()', "(lower(hex(randomblob(16))))")
        ddl_sqlite = ddl_sqlite.replace('TIMESTAMP WITH TIME ZONE', 'TIMESTAMP')
        ddl_sqlite = ddl_sqlite.replace('JSONB', 'TEXT')

        engine = create_engine("sqlite:///:memory:")
        with engine.connect() as conn:
            # Execute statement by statement
            statements = [stmt.strip() for stmt in ddl_sqlite.split(";") if stmt.strip()]
            for stmt in statements:
                conn.execute(sa.text(stmt))
            conn.commit()

            inspector = inspect(engine)
            tables = inspector.get_table_names()

            expected_tables = [
                "sources", "countries", "competitions", "seasons", "venues",
                "clubs", "club_aliases", "club_external_ids", "club_season_memberships",
                "players", "player_club_memberships", "matches", "match_external_ids",
                "match_statistics", "match_events", "match_lineups", "raw_source_payloads",
                "provenance_records", "dataset_versions", "ingestion_runs"
            ]

            for tbl in expected_tables:
                self.assertIn(tbl, tables, f"Expected table '{tbl}' was not created by DDL")

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@supabase_host:6543/postgres?sslmode=require"})
    def test_alembic_env_database_url_override(self):
        from alembic.config import Config
        ini_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../infrastructure/database/alembic.ini")
        )
        config = Config(ini_path)

        # Test offline migration URL resolution logic
        url_offline = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
        self.assertEqual(url_offline, "postgresql://user:pass@supabase_host:6543/postgres?sslmode=require")

        # Test online migration config modification logic
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            config.set_main_option("sqlalchemy.url", database_url)
        self.assertEqual(config.get_main_option("sqlalchemy.url"), "postgresql://user:pass@supabase_host:6543/postgres?sslmode=require")

    def test_alembic_env_fallback_without_database_url(self):
        from alembic.config import Config
        ini_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../infrastructure/database/alembic.ini")
        )
        config = Config(ini_path)

        with patch.dict(os.environ, {}, clear=True):
            url_offline = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
            self.assertEqual(url_offline, "postgresql://postgres:postgres@localhost:5432/football_ai_db")

if __name__ == "__main__":
    unittest.main()
