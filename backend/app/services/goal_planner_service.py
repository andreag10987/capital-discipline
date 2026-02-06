from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
import math
from ..models.goal import Goal
from ..models.account import Account
from ..schemas.goal_planner import (
    GoalCreate, GoalUpdate, GoalResponse, 
    PlanCalculateRequest, PlanCalculateResponse
)
from ..utils.messages import get_message

def create_or_update_goal(
    db: Session, 
    user_id: int, 
    goal_data: GoalCreate, 
    lang: str = "en"
) -> GoalResponse:
    """Crear o actualizar el objetivo de capital del usuario"""
    # Obtener cuenta del usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    # Validar que el objetivo sea mayor al capital actual
    if goal_data.target_capital <= account.capital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("goal_must_be_greater", lang)
        )
    
    # Buscar si ya existe un objetivo
    existing_goal = db.query(Goal).filter(Goal.account_id == account.id).first()
    
    if existing_goal:
        # Actualizar
        existing_goal.target_capital = goal_data.target_capital
        db.commit()
        db.refresh(existing_goal)
        goal = existing_goal
    else:
        # Crear nuevo
        new_goal = Goal(
            account_id=account.id,
            target_capital=goal_data.target_capital
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        goal = new_goal
    
    # Calcular progreso
    progress_percent = (account.capital / goal.target_capital) * 100
    
    return GoalResponse(
        id=goal.id,
        account_id=goal.account_id,
        target_capital=goal.target_capital,
        current_capital=account.capital,
        progress_percent=round(progress_percent, 2),
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )

def get_goal(db: Session, user_id: int, lang: str = "en") -> Optional[GoalResponse]:
    """Obtener el objetivo actual del usuario"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goal = db.query(Goal).filter(Goal.account_id == account.id).first()
    if not goal:
        return None
    
    progress_percent = (account.capital / goal.target_capital) * 100
    
    return GoalResponse(
        id=goal.id,
        account_id=goal.account_id,
        target_capital=goal.target_capital,
        current_capital=account.capital,
        progress_percent=round(progress_percent, 2),
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )

def delete_goal(db: Session, user_id: int, lang: str = "en") -> bool:
    """Eliminar el objetivo del usuario"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goal = db.query(Goal).filter(Goal.account_id == account.id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("goal_not_found", lang)
        )
    
    db.delete(goal)
    db.commit()
    return True

def calculate_plan(
    db: Session, 
    user_id: int, 
    plan_request: PlanCalculateRequest, 
    lang: str = "en"
) -> PlanCalculateResponse:
    """Calcular plan de trading diario y proyecciones"""
    # Obtener cuenta del usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    # Obtener objetivo si existe
    goal = db.query(Goal).filter(Goal.account_id == account.id).first()
    target_capital = goal.target_capital if goal else None
    
    # Cálculos básicos
    current_capital = account.capital
    payout = account.payout
    
    # Stake por operación
    stake = current_capital * (plan_request.risk_percent / 100.0)
    
    # Ganancia por WIN y pérdida por LOSS
    win_profit = stake * payout
    loss_amount = stake
    
    # Retorno esperado por operación
    expected_return_per_op = (
        plan_request.winrate * payout - 
        (1 - plan_request.winrate) * 1.0
    )
    
    # Operaciones por día
    ops_per_day = plan_request.sessions_per_day * plan_request.ops_per_session
    
    # Factor de crecimiento diario
    risk_fraction = plan_request.risk_percent / 100.0
    daily_return = risk_fraction * ops_per_day * expected_return_per_op
    daily_growth_factor = 1 + daily_return
    
    # Proyecciones
    if daily_growth_factor > 0:
        projection_15 = current_capital * (daily_growth_factor ** 15)
        projection_30 = current_capital * (daily_growth_factor ** 30)
    else:
        projection_15 = 0
        projection_30 = 0
    
    # Días para alcanzar meta
    days_to_goal = None
    if target_capital and daily_growth_factor > 1:
        try:
            days_to_goal = math.log(target_capital / current_capital) / math.log(daily_growth_factor)
            days_to_goal = int(math.ceil(days_to_goal))
        except (ValueError, ZeroDivisionError):
            days_to_goal = None
    
    # Warnings y alertas
    warnings = []
    blocked_recommended = False
    
    if payout < 0.80:
        warnings.append(get_message("goal_payout_warning", lang))
        blocked_recommended = True
    
    if daily_growth_factor <= 1:
        warnings.append(get_message("goal_no_growth_warning", lang))
        if target_capital:
            warnings.append(get_message("goal_unreachable_warning", lang))
    
    if plan_request.winrate < 0.55:
        warnings.append(get_message("goal_low_winrate_warning", lang))
    
    # Límites recordatorios
    limits_reminder = {
        "session_loss_limit": get_message("limit_session_losses", lang),
        "day_loss_limit": get_message("limit_day_losses", lang),
        "drawdown_limit": get_message("limit_drawdown", lang),
        "unlock_time": get_message("limit_unlock_time", lang)
    }
    
    return PlanCalculateResponse(
        sessions_per_day=plan_request.sessions_per_day,
        ops_per_session=plan_request.ops_per_session,
        ops_per_day=ops_per_day,
        risk_percent=plan_request.risk_percent,
        winrate=plan_request.winrate,
        current_capital=round(current_capital, 2),
        payout=payout,
        target_capital=target_capital,
        stake_per_operation=round(stake, 2),
        win_profit=round(win_profit, 2),
        loss_amount=round(loss_amount, 2),
        expected_return_per_op=round(expected_return_per_op, 4),
        daily_growth_factor=round(daily_growth_factor, 6),
        projection_15_days=round(projection_15, 2),
        projection_30_days=round(projection_30, 2),
        days_to_goal=days_to_goal,
        blocked_recommended=blocked_recommended,
        warnings=warnings,
        limits_reminder=limits_reminder
    )