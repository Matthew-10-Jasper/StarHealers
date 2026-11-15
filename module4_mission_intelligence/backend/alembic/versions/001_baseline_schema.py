"""baseline schema

Revision ID: 001_baseline
Revises: 
Create Date: 2026-11-15 14:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline tables were initialized during Phase 1.
    # If tables do not exist, create them.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "mission_state" not in existing_tables:
        op.create_table(
            "mission_state",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("context_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("context_version", sa.Integer(), nullable=False, default=1),
            sa.Column("planned_profile_id", sa.String(length=64), nullable=False),
            sa.Column("actual_mission_phase", sa.String(length=128), nullable=False),
            sa.Column("operational_state", sa.String(length=32), nullable=False, default="NOMINAL"),
            sa.Column("gravity_environment", sa.String(length=64), nullable=False),
            sa.Column("gravity_value_g", sa.Float(), nullable=False, default=0.0001),
            sa.Column("communication_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("environment_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("data_quality_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("planned_context_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("data_source", sa.String(length=32), nullable=False, default="SIMULATED"),
            sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    if "environmental_observations" not in existing_tables:
        op.create_table(
            "environmental_observations",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("observation_id", sa.String(length=64), unique=True, nullable=False, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("parameter", sa.String(length=64), nullable=False, index=True),
            sa.Column("value_raw", sa.Text(), nullable=False),
            sa.Column("unit", sa.String(length=32), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.Column("source", sa.String(length=32), nullable=False, default="SIMULATED"),
            sa.Column("quality_status", sa.String(length=32), nullable=False, default="UNVERIFIED"),
            sa.Column("validation_status", sa.Boolean(), nullable=False, default=False),
            sa.Column("metadata_json", sa.Text(), nullable=False, default="{}"),
        )

    if "mission_deviations" not in existing_tables:
        op.create_table(
            "mission_deviations",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("deviation_id", sa.String(length=64), unique=True, nullable=False, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("deviation_name", sa.String(length=128), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("expected_condition", sa.String(length=256), nullable=False),
            sa.Column("actual_condition", sa.String(length=256), nullable=False),
            sa.Column("severity", sa.String(length=32), nullable=False),
            sa.Column("evidence_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.Column("source", sa.String(length=32), nullable=False, default="SIMULATED"),
            sa.Column("confirmation_status", sa.String(length=32), nullable=False, default="CONFIRMED"),
            sa.Column("resolved", sa.Boolean(), nullable=False, default=False),
            sa.Column("resolution_notes", sa.Text(), nullable=True),
        )

    if "state_transitions" not in existing_tables:
        op.create_table(
            "state_transitions",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("transition_id", sa.String(length=64), unique=True, nullable=False, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("from_state", sa.String(length=32), nullable=False),
            sa.Column("to_state", sa.String(length=32), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("evidence_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("operator_id", sa.String(length=64), nullable=False, default="MISSION_CONTROLLER"),
            sa.Column("is_valid", sa.Boolean(), nullable=False, default=True),
            sa.Column("context_version", sa.Integer(), nullable=False, default=1),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
        )

    if "audit_log" not in existing_tables:
        op.create_table(
            "audit_log",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("event_id", sa.String(length=64), unique=True, nullable=False, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("evidence_json", sa.Text(), nullable=False, default="{}"),
            sa.Column("operator_id", sa.String(length=64), nullable=False, default="SYSTEM"),
            sa.Column("context_version", sa.Integer(), nullable=False, default=1),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
        )

    if "queued_reports" not in existing_tables:
        op.create_table(
            "queued_reports",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("report_id", sa.String(length=64), unique=True, nullable=False, index=True),
            sa.Column("mission_id", sa.String(length=64), nullable=False, index=True),
            sa.Column("report_type", sa.String(length=64), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=False),
            sa.Column("delivery_status", sa.String(length=32), nullable=False, default="LOCALLY_GENERATED"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("transmitted_at", sa.DateTime(), nullable=True),
            sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
            sa.Column("acknowledgement_id", sa.String(length=64), nullable=True),
        )


def downgrade() -> None:
    op.drop_table("queued_reports")
    op.drop_table("audit_log")
    op.drop_table("state_transitions")
    op.drop_table("mission_deviations")
    op.drop_table("environmental_observations")
    op.drop_table("mission_state")
