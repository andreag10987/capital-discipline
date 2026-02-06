"""expand_goals_add_daily_plans_withdrawals

Revision ID: bf5c870d8d82
Revises: 4d7427f3428d
Create Date: 2026-02-01 18:47:43.540229

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'bf5c870d8d82'
down_revision: Union[str, None] = '4d7427f3428d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Crear tipos ENUM explícitamente ANTES de usarlos
    conn = op.get_bind()
    
    # Crear goalstatus si no existe
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE goalstatus AS ENUM ('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Crear dailyplanstatus si no existe
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE dailyplanstatus AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # 1. Crear tabla goal_daily_plans
    op.create_table('goal_daily_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('capital_start_of_day', sa.Float(), nullable=False),
        sa.Column('planned_sessions', sa.Integer(), nullable=False),
        sa.Column('planned_ops_total', sa.Integer(), nullable=False),
        sa.Column('planned_stake', sa.Float(), nullable=False),
        sa.Column('expected_win_profit', sa.Float(), nullable=False),
        sa.Column('expected_loss', sa.Float(), nullable=False),
        sa.Column('actual_sessions', sa.Integer(), nullable=True),
        sa.Column('actual_ops', sa.Integer(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('losses', sa.Integer(), nullable=True),
        sa.Column('draws', sa.Integer(), nullable=True),
        sa.Column('realized_pnl', sa.Float(), nullable=True),
        sa.Column('status', postgresql.ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED', name='dailyplanstatus', create_type=False), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('blocked_reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goal_daily_plans_date'), 'goal_daily_plans', ['date'], unique=False)
    op.create_index(op.f('ix_goal_daily_plans_goal_id'), 'goal_daily_plans', ['goal_id'], unique=False)
    op.create_index(op.f('ix_goal_daily_plans_id'), 'goal_daily_plans', ['id'], unique=False)
    
    # 2. Crear tabla withdrawals
    op.create_table('withdrawals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('withdrawn_at', sa.DateTime(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('capital_before', sa.Float(), nullable=False),
        sa.Column('capital_after', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('amount > 0', name='check_withdrawal_amount_positive'),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_withdrawals_account_id'), 'withdrawals', ['account_id'], unique=False)
    op.create_index(op.f('ix_withdrawals_goal_id'), 'withdrawals', ['goal_id'], unique=False)
    op.create_index(op.f('ix_withdrawals_id'), 'withdrawals', ['id'], unique=False)
    
    # 3. Añadir columnas nuevas a goals
    op.add_column('goals', sa.Column('start_capital_snapshot', sa.Float(), nullable=True))
    op.add_column('goals', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('goals', sa.Column('payout_snapshot', sa.Float(), nullable=True))
    op.add_column('goals', sa.Column('risk_percent', sa.Integer(), nullable=True))
    op.add_column('goals', sa.Column('sessions_per_day', sa.Integer(), nullable=True))
    op.add_column('goals', sa.Column('ops_per_session', sa.Integer(), nullable=True))
    op.add_column('goals', sa.Column('winrate_estimate', sa.Float(), nullable=True))
    op.add_column('goals', sa.Column('status', postgresql.ENUM('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED', name='goalstatus', create_type=False), nullable=True))
    op.add_column('goals', sa.Column('not_recommended', sa.Boolean(), nullable=True))
    op.add_column('goals', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # 4. Poblar valores por defecto para goals existentes
    op.execute("""
        UPDATE goals 
        SET 
            start_date = DATE(created_at),
            risk_percent = 2,
            sessions_per_day = 2,
            ops_per_session = 5,
            winrate_estimate = 0.60,
            status = 'ACTIVE',
            not_recommended = FALSE
        WHERE start_date IS NULL
    """)
    
    # Poblar desde accounts
    op.execute("""
        UPDATE goals 
        SET 
            start_capital_snapshot = (
                SELECT capital 
                FROM accounts 
                WHERE accounts.id = goals.account_id
            ),
            payout_snapshot = (
                SELECT payout 
                FROM accounts 
                WHERE accounts.id = goals.account_id
            )
        WHERE start_capital_snapshot IS NULL
    """)
    
    # 5. Añadir constraints CHECK a goals
    op.create_check_constraint(
        'check_target_capital_positive',
        'goals',
        'target_capital > 0'
    )
    op.create_check_constraint(
        'check_risk_percent_valid',
        'goals',
        'risk_percent IN (2, 3)'
    )
    op.create_check_constraint(
        'check_sessions_per_day_valid',
        'goals',
        'sessions_per_day IN (2, 3)'
    )
    op.create_check_constraint(
        'check_ops_per_session_valid',
        'goals',
        'ops_per_session IN (4, 5)'
    )
    op.create_check_constraint(
        'check_winrate_valid',
        'goals',
        'winrate_estimate >= 0.50 AND winrate_estimate <= 0.80'
    )


def downgrade() -> None:
    # 1. Eliminar constraints de goals
    op.drop_constraint('check_winrate_valid', 'goals', type_='check')
    op.drop_constraint('check_ops_per_session_valid', 'goals', type_='check')
    op.drop_constraint('check_sessions_per_day_valid', 'goals', type_='check')
    op.drop_constraint('check_risk_percent_valid', 'goals', type_='check')
    op.drop_constraint('check_target_capital_positive', 'goals', type_='check')
    
    # 2. Eliminar columnas de goals
    op.drop_column('goals', 'completed_at')
    op.drop_column('goals', 'not_recommended')
    op.drop_column('goals', 'status')
    op.drop_column('goals', 'winrate_estimate')
    op.drop_column('goals', 'ops_per_session')
    op.drop_column('goals', 'sessions_per_day')
    op.drop_column('goals', 'risk_percent')
    op.drop_column('goals', 'payout_snapshot')
    op.drop_column('goals', 'start_date')
    op.drop_column('goals', 'start_capital_snapshot')
    
    # 3. Eliminar tabla withdrawals
    op.drop_index(op.f('ix_withdrawals_id'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_goal_id'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_account_id'), table_name='withdrawals')
    op.drop_table('withdrawals')
    
    # 4. Eliminar tabla goal_daily_plans
    op.drop_index(op.f('ix_goal_daily_plans_id'), table_name='goal_daily_plans')
    op.drop_index(op.f('ix_goal_daily_plans_goal_id'), table_name='goal_daily_plans')
    op.drop_index(op.f('ix_goal_daily_plans_date'), table_name='goal_daily_plans')
    op.drop_table('goal_daily_plans')
    
    # 5. Eliminar tipos ENUM
    conn = op.get_bind()
    conn.execute(sa.text("DROP TYPE IF EXISTS dailyplanstatus"))
    conn.execute(sa.text("DROP TYPE IF EXISTS goalstatus"))