"""
Stage 23 Migration: Production Database Hardening Indexes

Revision ID: 003_stage23_production_indexes
Revises: 002_stage20_prediction_history_schema
Create Date: 2026-03-01 12:00:00.000000

Adds targeted production indexes for high-frequency access patterns:
- Match lookup by kickoff & status (idx_matches_kickoff_status)
- Match lookup by clubs (idx_matches_clubs)
- Prediction report lookup by fixture & timestamp (idx_pred_reports_fixture_ts)
- Prediction report lookup by status & timestamp (idx_pred_reports_status_ts)
- Club alias lookup by alias name (idx_club_aliases_name)
"""

from alembic import op
import sqlalchemy as sa

revision = "003_stage23_production_indexes"
down_revision = "002_stage20_prediction_history_schema"
branch_labels = None
depends_on = None


def upgrade():
    # Matches table indexes
    op.create_index(
        "idx_matches_kickoff_status",
        "matches",
        ["scheduled_kickoff_utc", "status"],
        unique=False,
    )
    op.create_index(
        "idx_matches_clubs",
        "matches",
        ["home_club_id", "away_club_id"],
        unique=False,
    )

    # Prediction Reports table indexes
    op.create_index(
        "idx_pred_reports_fixture_ts",
        "prediction_reports",
        ["fixture_id", "prediction_timestamp_utc"],
        unique=False,
    )
    op.create_index(
        "idx_pred_reports_status_ts",
        "prediction_reports",
        ["decision_status", "created_at_utc"],
        unique=False,
    )

    # Club Aliases index
    op.create_index(
        "idx_club_aliases_name",
        "club_aliases",
        ["alias_name"],
        unique=False,
    )


def downgrade():
    op.drop_index("idx_club_aliases_name", table_name="club_aliases")
    op.drop_index("idx_pred_reports_status_ts", table_name="prediction_reports")
    op.drop_index("idx_pred_reports_fixture_ts", table_name="prediction_reports")
    op.drop_index("idx_matches_clubs", table_name="matches")
    op.drop_index("idx_matches_kickoff_status", table_name="matches")
