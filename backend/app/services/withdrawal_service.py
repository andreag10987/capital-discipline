from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
from ..models.withdrawal import Withdrawal
from ..models.account import Account
from ..models.goal import Goal, GoalStatus
from ..services.daily_plan_service import regenerate_goal_calendar
from ..schemas.withdrawal import WithdrawalCreate, WithdrawalResponse, WithdrawalListResponse
from ..utils.messages import get_message

def create_withdrawal(
    db: Session,
    user_id: int,
    withdrawal_data: WithdrawalCreate,
    lang: str = "en"
) -> WithdrawalResponse:
    """Registrar un retiro de capital"""
    # Obtener cuenta del usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    # Validar que haya suficiente capital
    if withdrawal_data.amount > account.capital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay suficiente capital para realizar el retiro"
        )
    
    # Buscar objetivo activo
    active_goal = db.query(Goal).filter(
        Goal.account_id == account.id,
        Goal.status == GoalStatus.ACTIVE
    ).first()
    
    # Capturar capital antes y después
    capital_before = account.capital
    capital_after = capital_before - withdrawal_data.amount
    
    # Actualizar capital de la cuenta
    account.capital = capital_after
    
    # Crear registro de retiro
    new_withdrawal = Withdrawal(
        account_id=account.id,
        goal_id=active_goal.id if active_goal else None,
        amount=withdrawal_data.amount,
        withdrawn_at=datetime.utcnow(),
        note=withdrawal_data.note,
        capital_before=capital_before,
        capital_after=capital_after
    )
    
    db.add(new_withdrawal)
    db.commit()
    db.refresh(new_withdrawal)

    # Recalcular calendario de meta activa con el nuevo capital base.
    if active_goal:
        regenerate_goal_calendar(db, active_goal.id)

    return WithdrawalResponse.from_orm(new_withdrawal)

def get_withdrawals(
    db: Session,
    user_id: int,
    goal_id: Optional[int] = None,
    limit: int = 100,
    lang: str = "en"
) -> WithdrawalListResponse:
    """Obtener historial de retiros"""
    # Obtener cuenta del usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    # Query base
    query = db.query(Withdrawal).filter(Withdrawal.account_id == account.id)
    
    # Filtrar por objetivo si se especifica
    if goal_id:
        query = query.filter(Withdrawal.goal_id == goal_id)
    
    # Ordenar y limitar
    withdrawals = query.order_by(Withdrawal.withdrawn_at.desc()).limit(limit).all()
    
    # Calcular total retirado
    total_withdrawn = sum(w.amount for w in withdrawals)
    
    # Convertir a responses
    withdrawal_responses = [WithdrawalResponse.from_orm(w) for w in withdrawals]
    
    return WithdrawalListResponse(
        withdrawals=withdrawal_responses,
        total_withdrawn=round(total_withdrawn, 2),
        count=len(withdrawals)
    )

def get_withdrawal(
    db: Session,
    user_id: int,
    withdrawal_id: int,
    lang: str = "en"
) -> WithdrawalResponse:
    """Obtener detalle de un retiro específico"""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    withdrawal = db.query(Withdrawal).filter(
        Withdrawal.id == withdrawal_id,
        Withdrawal.account_id == account.id
    ).first()
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retiro no encontrado"
        )
    
    return WithdrawalResponse.from_orm(withdrawal)

def delete_withdrawal(
    db: Session,
    user_id: int,
    withdrawal_id: int,
    lang: str = "en"
) -> bool:
    """
    Eliminar/revertir un retiro (solo para correcciones, no recomendado)
    NOTA: Esto NO devuelve el dinero a la cuenta, solo elimina el registro
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    withdrawal = db.query(Withdrawal).filter(
        Withdrawal.id == withdrawal_id,
        Withdrawal.account_id == account.id
    ).first()
    
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retiro no encontrado"
        )
    
    # Advertencia: esto solo elimina el registro, no revierte el capital
    db.delete(withdrawal)
    db.commit()
    
    return True
