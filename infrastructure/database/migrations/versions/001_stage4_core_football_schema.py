"""001_stage4_core_football_schema

Revision ID: 001_stage4_core_schema
Revises: None
Create Date: 2026-09-16 02:00:00.000000

"""
import os
from typing import Sequence, Union

from alembic import op

revision: str = '001_stage4_core_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "../../schema.sql")
    if os.path.exists(sql_path):
        with open(sql_path, "r", encoding="utf-8") as f:
            ddl = f.read()
        op.execute(ddl)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ingestion_runs CASCADE;")
    op.execute("DROP TABLE IF EXISTS dataset_versions CASCADE;")
    op.execute("DROP TABLE IF EXISTS provenance_records CASCADE;")
    op.execute("DROP TABLE IF EXISTS raw_source_payloads CASCADE;")
    op.execute("DROP TABLE IF EXISTS match_lineups CASCADE;")
    op.execute("DROP TABLE IF EXISTS match_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS match_statistics CASCADE;")
    op.execute("DROP TABLE IF EXISTS match_external_ids CASCADE;")
    op.execute("DROP TABLE IF EXISTS matches CASCADE;")
    op.execute("DROP TABLE IF EXISTS player_club_memberships CASCADE;")
    op.execute("DROP TABLE IF EXISTS players CASCADE;")
    op.execute("DROP TABLE IF EXISTS club_season_memberships CASCADE;")
    op.execute("DROP TABLE IF EXISTS club_external_ids CASCADE;")
    op.execute("DROP TABLE IF EXISTS club_aliases CASCADE;")
    op.execute("DROP TABLE IF EXISTS clubs CASCADE;")
    op.execute("DROP TABLE IF EXISTS venues CASCADE;")
    op.execute("DROP TABLE IF EXISTS seasons CASCADE;")
    op.execute("DROP TABLE IF EXISTS competitions CASCADE;")
    op.execute("DROP TABLE IF EXISTS countries CASCADE;")
    op.execute("DROP TABLE IF EXISTS sources CASCADE;")
