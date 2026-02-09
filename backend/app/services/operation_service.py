"""
Servicio para gestionar operaciones de trading.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from ..models.operation import Operation
from ..models.trading_session import TradingSession
from ..models.trading_day import TradingDay
from ..models.account import Account
from ..models.goal import Goal, GoalStatus
from ..schemas.operation import OperationCreate
from ..services.daily_plan_service import regenerate_goal_calendar


def create_operation(
    db: Session,
    user_id: int,
    operation_data: OperationCreate,
    lang: str = "en"
) -> Operation:
    """Crea una nueva operación y actualiza métricas básicas.

    - En este proyecto TradingSession NO guarda contadores wins/total, solo `loss_count`.
    - `amount` puede venir vacío desde frontend; si viene None, aquí se calcula.
    - `profit` puede venir vacío; si viene None, aquí se calcula con una convención conservadora.
    """

    # 1) Verificar que la sesión existe
    session = db.query(TradingSession).filter(
        TradingSession.id == operation_data.session_id
    ).first()

    if not session:
        raise ValueError("Session not found" if lang == "en" else "Sesión no encontrada")

    # 2) Verificar jerarquía: sesión -> día -> cuenta -> usuario
    trading_day = db.query(TradingDay).filter(TradingDay.id == session.trading_day_id).first()
    if not trading_day:
        raise ValueError("Trading day not found" if lang == "en" else "Día de trading no encontrado")

    account = db.query(Account).filter(Account.id == trading_day.account_id).first()
    if not account:
        raise ValueError("Account not found" if lang == "en" else "Cuenta no encontrada")

    if account.user_id != user_id:
        raise ValueError("Unauthorized" if lang == "en" else "No autorizado")

    # 3) Calcular amount si no viene desde el frontend
    # amount = capital_actual * (risk_percent/100)
    amount = operation_data.amount
    if amount is None:
        current_capital = float(account.capital or 0)
        if current_capital <= 0:
            raise ValueError("Invalid capital" if lang == "en" else "Capital inválido")

        amount = round(current_capital * (operation_data.risk_percent / 100), 6)

    # Validación extra por seguridad
    if amount <= 0:
        raise ValueError("Invalid amount" if lang == "en" else "Monto inválido")

    # 4) Calcular profit si no viene (convención conservadora)
    # WIN: +0.92 * amount
    # LOSS: -amount
    # DRAW: 0
    profit = operation_data.profit
    if profit is None:
        if operation_data.result == "WIN":
            profit = round(amount * 0.92, 6)
        elif operation_data.result == "LOSS":
            profit = round(-amount, 6)
        else:  # DRAW
            profit = 0.0

    # 5) Crear operación
    new_operation = Operation(
        session_id=operation_data.session_id,
        result=operation_data.result,
        risk_percent=operation_data.risk_percent,
        amount=amount,
        profit=profit,
        comment=operation_data.comment,
        created_at=datetime.utcnow()
    )

    db.add(new_operation)

    # 6) Actualizar contador de pérdidas de la sesión (campo existente)
    if operation_data.result == "LOSS":
        session.loss_count = (session.loss_count or 0) + 1

    # 7) Actualizar capital de la cuenta (neto)
    account.capital = float(account.capital or 0) + float(profit)

    db.commit()
    db.refresh(new_operation)

    # 8) Recalcular calendario de la meta activa para reajustar montos futuros.
    active_goal = db.query(Goal).filter(
        Goal.account_id == account.id,
        Goal.status == GoalStatus.ACTIVE
    ).first()
    if active_goal:
        regenerate_goal_calendar(db, active_goal.id)

    return new_operation


def get_operations_by_session(
    db: Session,
    session_id: int,
    user_id: int
) -> List[Operation]:
    """Obtiene todas las operaciones de una sesión."""

    # Verificar que la sesión pertenece al usuario
    session = db.query(TradingSession).filter(
        TradingSession.id == session_id
    ).first()

    if not session:
        return []

    trading_day = db.query(TradingDay).filter(TradingDay.id == session.trading_day_id).first()
    if not trading_day:
        return []

    account = db.query(Account).filter(Account.id == trading_day.account_id).first()
    if not account:
        return []

    if account.user_id != user_id:
        return []

    # Obtener operaciones
    operations = db.query(Operation).filter(
        Operation.session_id == session_id
    ).order_by(Operation.created_at.desc()).all()

    return operations
