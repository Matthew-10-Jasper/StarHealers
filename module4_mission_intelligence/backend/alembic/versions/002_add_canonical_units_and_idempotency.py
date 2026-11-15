"""add canonical units and idempotency

Revision ID: 002_units_idempotency
Revises: 001_baseline
Create Date: 2026-11-15 14:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_units_idempotency'
down_revision: Union[str, None] = '001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('environmental_observations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('canonical_value', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('canonical_unit', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('idempotency_key', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_environmental_observations_idempotency_key'), ['idempotency_key'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('environmental_observations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_environmental_observations_idempotency_key'))
        batch_op.drop_column('idempotency_key')
        batch_op.drop_column('canonical_unit')
        batch_op.drop_column('canonical_value')
