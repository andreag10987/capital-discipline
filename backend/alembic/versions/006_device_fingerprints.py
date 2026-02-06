"""add device fingerprints

Revision ID: 006_device_fingerprints
Revises: 005_email_verification
Create Date: 2026-02-04 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006_device_fingerprints'
down_revision: Union[str, None] = '005_email_verification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla device_fingerprints
    op.create_table(
        'device_fingerprints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('fingerprint_hash', sa.String(64), nullable=False),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('screen_resolution', sa.String(20), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('platform', sa.String(50), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_seen', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices para búsquedas rápidas
    op.create_index('ix_device_fingerprints_user_id', 'device_fingerprints', ['user_id'])
    op.create_index('ix_device_fingerprints_hash', 'device_fingerprints', ['fingerprint_hash'])
    op.create_index('ix_device_fingerprints_hash_user', 'device_fingerprints', ['fingerprint_hash', 'user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_device_fingerprints_hash_user', table_name='device_fingerprints')
    op.drop_index('ix_device_fingerprints_hash', table_name='device_fingerprints')
    op.drop_index('ix_device_fingerprints_user_id', table_name='device_fingerprints')
    op.drop_table('device_fingerprints')