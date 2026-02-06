"""add admin role and blocked status

Revision ID: 009_add_admin_role
Revises: 008_oauth_identities
Create Date: 2026-02-04 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '009_add_admin_role'
down_revision: Union[str, None] = '008_oauth_identities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columnas de administración a users
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('blocked_reason', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('blocked_at', sa.DateTime(), nullable=True))
    
    # Índice para búsquedas rápidas de admins
    op.create_index('ix_users_is_admin', 'users', ['is_admin'])
    op.create_index('ix_users_is_blocked', 'users', ['is_blocked'])


def downgrade() -> None:
    op.drop_index('ix_users_is_blocked', table_name='users')
    op.drop_index('ix_users_is_admin', table_name='users')
    op.drop_column('users', 'blocked_at')
    op.drop_column('users', 'blocked_reason')
    op.drop_column('users', 'is_blocked')
    op.drop_column('users', 'is_admin')