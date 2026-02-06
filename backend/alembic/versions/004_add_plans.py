"""add plans and subscriptions

Revision ID: 004_add_plans
Revises: 003_expand_goals
Create Date: 2026-02-04 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_plans'
down_revision: Union[str, None] = 'bf5c870d8d82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear tabla plans
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name_es', sa.String(100), nullable=False),
        sa.Column('display_name_en', sa.String(100), nullable=False),
        sa.Column('price_usd', sa.Float(), nullable=False),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Crear tabla subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('payment_provider', sa.String(50), nullable=True),
        sa.Column('external_subscription_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    
    # Seed data - Planes iniciales
    op.execute("""
        INSERT INTO plans (name, display_name_es, display_name_en, price_usd, features) VALUES
        ('FREE', 'Gratis', 'Free', 0.0, '{
            "max_daily_sessions": 1,
            "max_ops_per_session": 3,
            "max_active_goals": 1,
            "history_days": 3,
            "can_export_pdf": false,
            "can_export_excel": false,
            "can_see_projections": false,
            "can_recalculate_withdrawals": false
        }'),
        ('BASIC', 'Básico', 'Basic', 10.0, '{
            "max_daily_sessions": 2,
            "max_ops_per_session": 5,
            "max_active_goals": 1,
            "history_days": 30,
            "can_export_pdf": false,
            "can_export_excel": false,
            "can_see_projections": true,
            "can_recalculate_withdrawals": false
        }'),
        ('PRO', 'Pro', 'Pro', 20.0, '{
            "max_daily_sessions": 999,
            "max_ops_per_session": 999,
            "max_active_goals": 999,
            "history_days": 999,
            "can_export_pdf": true,
            "can_export_excel": true,
            "can_see_projections": true,
            "can_recalculate_withdrawals": true
        }')
    """)


def downgrade() -> None:
    op.drop_index('ix_subscriptions_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_table('plans')