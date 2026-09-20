"""Stage 20 Prediction Reports Schema Migration

Revision ID: 002_stage20_prediction_history_schema
Revises: 001_stage4_core_football_schema
Create Date: 2026-09-19 22:00:00.000000

"""

import alembic.op as op
import sqlalchemy as sa

revision = "002_stage20_prediction_history_schema"
down_revision = "001_stage4_core_football_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prediction_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("prediction_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("fixture_id", sa.String(length=128), nullable=False),
        sa.Column("prediction_timestamp_utc", sa.DateTime(), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("calibration_method", sa.String(length=64), nullable=False),
        sa.Column("decision_status", sa.String(length=64), nullable=False),
        sa.Column("report_payload_json", sa.Text(), nullable=False),
        sa.Column("audit_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_prediction_reports_fixture_id", "prediction_reports", ["fixture_id"])
    op.create_index("idx_prediction_reports_decision_status", "prediction_reports", ["decision_status"])


def downgrade() -> None:
    op.drop_index("idx_prediction_reports_decision_status", table_name="prediction_reports")
    op.drop_index("idx_prediction_reports_fixture_id", table_name="prediction_reports")
    op.drop_table("prediction_reports")
