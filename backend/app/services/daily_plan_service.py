from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, datetime, timedelta
from typing import Optional, List
from ..models.goal import Goal
from ..models.goal_daily_plan import GoalDailyPlan, DailyPlanStatus
from ..models.account import Account
from ..schemas.daily_plan import (
    DailyPlanCreate, DailyPlanUpdate, DailyPlanResponse,
    CalendarRangeRequest, CalendarResponse
)
from ..utils.messages import get_message

def create_or_get_daily_plan(
    db: Session,
    goal_id: int,
    plan_date: date,
    capital_start_of_day: float
) -> GoalDailyPlan:
    """Crear o obtener plan diario"""
    # Buscar si ya existe
    existing = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date == plan_date
    ).first()
    
    if existing:
        return existing
    
    # Obtener configuración del objetivo
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Calcular valores del plan
    stake = capital_start_of_day * (goal.risk_percent / 100.0)
    ops_total = goal.sessions_per_day * goal.ops_per_session
    
    # Crear nuevo plan
    new_plan = GoalDailyPlan(
        goal_id=goal_id,
        date=plan_date,
        capital_start_of_day=capital_start_of_day,
        planned_sessions=goal.sessions_per_day,
        planned_ops_total=ops_total,
        planned_stake=stake,
        expected_win_profit=stake * goal.payout_snapshot,
        expected_loss=stake,
        status=DailyPlanStatus.PLANNED
    )
    
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    
    return new_plan

def update_daily_plan(
    db: Session,
    plan_id: int,
    update_data: DailyPlanUpdate
) -> GoalDailyPlan:
    """Actualizar plan diario"""
    plan = db.query(GoalDailyPlan).filter(GoalDailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")
    
    # Actualizar campos
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return plan

def get_calendar(
    db: Session,
    user_id: int,
    goal_id: int,
    range_request: Optional[CalendarRangeRequest] = None,
    lang: str = "en"
) -> CalendarResponse:
    """Obtener almanaque (calendario) del objetivo"""
    # Verificar que el objetivo pertenece al usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Determinar rango de fechas
    if range_request and range_request.from_date and range_request.to_date:
        from_date = range_request.from_date
        to_date = range_request.to_date
    elif range_request and range_request.days:
        to_date = date.today()
        from_date = to_date - timedelta(days=range_request.days - 1)
    else:
        # Por defecto: desde inicio del objetivo hasta hoy
        from_date = goal.start_date
        to_date = date.today()
    
    # Obtener planes del rango
    daily_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date >= from_date,
        GoalDailyPlan.date <= to_date
    ).order_by(GoalDailyPlan.date).all()
    
    # Calcular métricas
    total_days = len(daily_plans)
    completed_days = sum(1 for p in daily_plans if p.status == DailyPlanStatus.COMPLETED)
    blocked_days = sum(1 for p in daily_plans if p.status == DailyPlanStatus.BLOCKED)
    total_pnl = sum(p.realized_pnl for p in daily_plans)
    total_wins = sum(p.wins for p in daily_plans)
    total_losses = sum(p.losses for p in daily_plans)
    total_draws = sum(p.draws for p in daily_plans)
    
    total_ops = total_wins + total_losses + total_draws
    real_winrate = total_wins / total_ops if total_ops > 0 else None
    
    # Convertir a responses
    plan_responses = [DailyPlanResponse.from_orm(p) for p in daily_plans]
    
    return CalendarResponse(
        goal_id=goal_id,
        daily_plans=plan_responses,
        total_days=total_days,
        completed_days=completed_days,
        blocked_days=blocked_days,
        total_pnl=round(total_pnl, 2),
        total_wins=total_wins,
        total_losses=total_losses,
        total_draws=total_draws,
        real_winrate=round(real_winrate, 4) if real_winrate is not None else None
    )

def get_daily_plan_by_date(
    db: Session,
    goal_id: int,
    plan_date: date
) -> Optional[GoalDailyPlan]:
    """Obtener plan de un día específico"""
    return db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date == plan_date
    ).first()