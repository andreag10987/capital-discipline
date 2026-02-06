"""add email verification

Revision ID: 005_email_verification
Revises: 004_add_plans
Create Date: 2026-02-04 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_email_verification'
down_revision: Union[str, None] = '004_add_plans'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columnas de verificación de email a users
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email_verification_sent_at', sa.DateTime(), nullable=True))
    
    # Índice para búsqueda rápida por token
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'])


def downgrade() -> None:
    op.drop_index('ix_users_email_verification_token', table_name='users')
    op.drop_column('users', 'email_verification_sent_at')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')