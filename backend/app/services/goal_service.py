from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, datetime
from typing import Optional
import math
from ..models.goal import Goal, GoalStatus
from ..models.account import Account
from ..models.operation import Operation, OperationResult
from ..models.trading_session import TradingSession
from ..models.trading_day import TradingDay
from ..schemas.goal_extended import (
    GoalCreateExtended, GoalUpdate, GoalResponseExtended, GoalProgressResponse
)
from ..services.daily_plan_service import regenerate_goal_calendar
from ..utils.messages import get_message

def create_goal(
    db: Session, 
    user_id: int, 
    goal_data: GoalCreateExtended, 
    lang: str = "en"
) -> GoalResponseExtended:
    """Crear objetivo con configuración completa"""
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
    
    # Verificar si ya existe un objetivo activo
    existing_goal = db.query(Goal).filter(
        Goal.account_id == account.id,
        Goal.status.in_([GoalStatus.ACTIVE, GoalStatus.PAUSED])
    ).first()
    
    if existing_goal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un objetivo activo o pausado. Completa o cancela el objetivo actual primero."
        )
    
    # Determinar si no es recomendado (payout < 0.80)
    not_recommended = account.payout < 0.80
    
    # Crear nuevo objetivo
    new_goal = Goal(
        account_id=account.id,
        target_capital=goal_data.target_capital,
        start_capital_snapshot=account.capital,
        start_date=date.today(),
        payout_snapshot=account.payout,
        risk_percent=goal_data.risk_percent,
        sessions_per_day=goal_data.sessions_per_day,
        ops_per_session=goal_data.ops_per_session,
        winrate_estimate=goal_data.winrate_estimate,
        status=GoalStatus.ACTIVE,
        not_recommended=not_recommended
    )
    
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    # Generar plan diario proyectado desde hoy hasta alcanzar meta.
    regenerate_goal_calendar(db, new_goal.id)
    
    # Calcular progreso
    response = GoalResponseExtended.from_orm(new_goal)
    response.current_capital = account.capital
    response.progress_percent = (account.capital / new_goal.target_capital) * 100
    
    return response

def get_goals(db: Session, user_id: int, lang: str = "en") -> list[GoalResponseExtended]:
    """Obtener todos los objetivos del usuario"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goals = db.query(Goal).filter(Goal.account_id == account.id).order_by(Goal.created_at.desc()).all()
    
    result = []
    for goal in goals:
        response = GoalResponseExtended.from_orm(goal)
        response.current_capital = account.capital
        response.progress_percent = (account.capital / goal.target_capital) * 100
        result.append(response)
    
    return result

def get_goal(db: Session, user_id: int, goal_id: int, lang: str = "en") -> GoalResponseExtended:
    """Obtener detalle de un objetivo"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("goal_not_found", lang)
        )
    
    response = GoalResponseExtended.from_orm(goal)
    response.current_capital = account.capital
    response.progress_percent = (account.capital / goal.target_capital) * 100
    
    return response

def update_goal(
    db: Session, 
    user_id: int, 
    goal_id: int, 
    goal_data: GoalUpdate, 
    lang: str = "en"
) -> GoalResponseExtended:
    """Actualizar configuración del objetivo"""
    goal = get_goal(db, user_id, goal_id, lang)
    
    goal_obj = db.query(Goal).filter(Goal.id == goal_id).first()
    
    # Actualizar campos
    update_data = goal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal_obj, field, value)
    
    db.commit()
    db.refresh(goal_obj)

    # Si cambia la configuración/meta, recalcular todo el calendario futuro.
    regenerate_goal_calendar(db, goal_obj.id)
    
    return get_goal(db, user_id, goal_id, lang)

def delete_goal(db: Session, user_id: int, goal_id: int, lang: str = "en") -> bool:
    """Eliminar objetivo"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("goal_not_found", lang)
        )
    
    db.delete(goal)
    db.commit()
    return True

def get_goal_progress(
    db: Session, 
    user_id: int, 
    goal_id: int, 
    lang: str = "en"
) -> GoalProgressResponse:
    """Obtener progreso detallado del objetivo con winrate real y ETA"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("goal_not_found", lang)
        )
    
    # Calcular métricas
    current_capital = account.capital
    capital_gained = current_capital - goal.start_capital_snapshot
    progress_percent = (current_capital / goal.target_capital) * 100
    days_elapsed = (date.today() - goal.start_date).days
    
    # Calcular winrate real desde el inicio del objetivo
    operations = db.query(Operation).join(
        TradingSession, Operation.session_id == TradingSession.id
    ).join(
        TradingDay, TradingSession.trading_day_id == TradingDay.id
    ).filter(
        TradingDay.account_id == account.id,
        TradingDay.date >= goal.start_date
    ).all()
    
    real_winrate = None
    if operations:
        wins = sum(1 for op in operations if op.result == OperationResult.WIN)
        total = len(operations)
        real_winrate = wins / total if total > 0 else None
    
    # Calcular ETA usando winrate real o estimate
    winrate_for_calc = real_winrate if real_winrate is not None else goal.winrate_estimate
    
    risk_fraction = goal.risk_percent / 100.0
    ops_per_day = goal.sessions_per_day * goal.ops_per_session
    expected_return = winrate_for_calc * goal.payout_snapshot - (1 - winrate_for_calc)
    daily_growth_factor = 1 + (risk_fraction * ops_per_day * expected_return)
    
    estimated_days_to_goal = None
    if daily_growth_factor > 1 and current_capital < goal.target_capital:
        try:
            estimated_days_to_goal = math.log(goal.target_capital / current_capital) / math.log(daily_growth_factor)
            estimated_days_to_goal = int(math.ceil(estimated_days_to_goal))
        except (ValueError, ZeroDivisionError):
            estimated_days_to_goal = None
    
    # Construir respuesta
    goal_response = GoalResponseExtended.from_orm(goal)
    goal_response.current_capital = current_capital
    goal_response.progress_percent = progress_percent
    
    return GoalProgressResponse(
        goal=goal_response,
        current_capital=current_capital,
        capital_gained=capital_gained,
        progress_percent=round(progress_percent, 2),
        days_elapsed=days_elapsed,
        real_winrate=round(real_winrate, 4) if real_winrate is not None else None,
        estimated_days_to_goal=estimated_days_to_goal,
        daily_growth_factor=round(daily_growth_factor, 6)
    )

def calculate_real_winrate(db: Session, account_id: int, days: int = 30) -> Optional[float]:
    """Calcular winrate real de últimos N días"""
    from datetime import timedelta
    cutoff_date = date.today() - timedelta(days=days)
    
    operations = db.query(Operation).join(
        TradingSession, Operation.session_id == TradingSession.id
    ).join(
        TradingDay, TradingSession.trading_day_id == TradingDay.id
    ).filter(
        TradingDay.account_id == account_id,
        TradingDay.date >= cutoff_date
    ).all()
    
    if not operations:
        return None
    
    wins = sum(1 for op in operations if op.result == OperationResult.WIN)
    total = len(operations)
    
    return wins / total if total > 0 else 0.0
