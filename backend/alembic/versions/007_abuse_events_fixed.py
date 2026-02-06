"""add abuse events logging fixed

Revision ID: 007_abuse_events_fixed
Revises: 006_device_fingerprints
Create Date: 2026-02-04 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007_abuse_events_fixed'
down_revision: Union[str, None] = '006_device_fingerprints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # La tabla ya existe, no hacer nada
    pass


def downgrade() -> None:
    # No hacer nada
    pass