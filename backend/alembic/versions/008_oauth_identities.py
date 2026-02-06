"""add oauth user identities

Revision ID: 008_oauth_identities
Revises: 007_abuse_events
Create Date: 2026-02-04 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '008_oauth_identities'
down_revision: Union[str, None] = '007_abuse_events_fixed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla user_identities
    op.create_table(
        'user_identities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('provider_name', sa.String(255), nullable=True),
        sa.Column('provider_picture', sa.String(512), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='unique_provider_user')
    )
    
    # Índices
    op.create_index('ix_user_identities_user_id', 'user_identities', ['user_id'])
    op.create_index('ix_user_identities_provider', 'user_identities', ['provider'])
    op.create_index('ix_user_identities_provider_user_id', 'user_identities', ['provider_user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_identities_provider_user_id', table_name='user_identities')
    op.drop_index('ix_user_identities_provider', table_name='user_identities')
    op.drop_index('ix_user_identities_user_id', table_name='user_identities')
    op.drop_table('user_identities')