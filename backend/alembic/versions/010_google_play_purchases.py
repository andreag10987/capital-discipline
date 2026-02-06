"""add google play purchases

Revision ID: 010_google_play_purchases
Revises: 009_add_admin_role
Create Date: 2026-02-05 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '010_google_play_purchases'
down_revision: Union[str, None] = '009_add_admin_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla google_play_purchases
    op.create_table(
        'google_play_purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        
        # Datos de Google Play
        sa.Column('purchase_token', sa.String(512), nullable=False, unique=True),
        sa.Column('product_id', sa.String(255), nullable=False),
        sa.Column('order_id', sa.String(255), nullable=True),
        sa.Column('package_name', sa.String(255), nullable=False),
        
        # Estado de la compra
        sa.Column('purchase_state', sa.String(50), nullable=False),
        # Valores: PENDING, PURCHASED, CANCELED, REFUNDED
        
        sa.Column('acknowledgement_state', sa.String(50), nullable=False),
        # Valores: NOT_ACKNOWLEDGED, ACKNOWLEDGED
        
        # Timestamps
        sa.Column('purchase_time_millis', sa.BigInteger(), nullable=False),
        sa.Column('expiry_time_millis', sa.BigInteger(), nullable=True),
        sa.Column('auto_renewing', sa.Boolean(), nullable=True),
        
        # Verificación
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        
        # Raw response de Google
        sa.Column('google_response', sa.JSON(), nullable=True),
        
        # Timestamps locales
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('ix_google_play_purchases_user_id', 'google_play_purchases', ['user_id'])
    op.create_index('ix_google_play_purchases_purchase_token', 'google_play_purchases', ['purchase_token'], unique=True)
    op.create_index('ix_google_play_purchases_product_id', 'google_play_purchases', ['product_id'])
    op.create_index('ix_google_play_purchases_purchase_state', 'google_play_purchases', ['purchase_state'])


def downgrade() -> None:
    op.drop_index('ix_google_play_purchases_purchase_state', table_name='google_play_purchases')
    op.drop_index('ix_google_play_purchases_product_id', table_name='google_play_purchases')
    op.drop_index('ix_google_play_purchases_purchase_token', table_name='google_play_purchases')
    op.drop_index('ix_google_play_purchases_user_id', table_name='google_play_purchases')
    op.drop_table('google_play_purchases')