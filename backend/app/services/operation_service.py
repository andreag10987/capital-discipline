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
from ..schemas.operation import OperationCreate


def create_operation(
    db: Session,
    user_id: int,
    operation_data: OperationCreate,
    lang: str = "en"
) -> Operation:
    """Crea una nueva operación y actualiza métricas básicas.

    Nota: El modelo TradingSession en este proyecto NO guarda contadores (wins/losses/total_operations).
    Por eso, aquí solo se actualiza `loss_count` (que sí existe) y el capital de la cuenta.
    """

    # Verificar que la sesión existe
    session = db.query(TradingSession).filter(
        TradingSession.id == operation_data.session_id
    ).first()

    if not session:
        raise ValueError("Session not found" if lang == "en" else "Sesión no encontrada")

    # Verificar jerarquía: sesión -> día -> cuenta -> usuario
    trading_day = db.query(TradingDay).filter(TradingDay.id == session.trading_day_id).first()
    if not trading_day:
        raise ValueError("Trading day not found" if lang == "en" else "Día de trading no encontrado")

    account = db.query(Account).filter(Account.id == trading_day.account_id).first()
    if not account:
        raise ValueError("Account not found" if lang == "en" else "Cuenta no encontrada")

    if account.user_id != user_id:
        raise ValueError("Unauthorized" if lang == "en" else "No autorizado")

    # Calcular profit si no viene (convención conservadora)
    profit = operation_data.profit
    if profit is None:
        if operation_data.result == "WIN":
            # payout típico 92% (ajústalo si tu app usa otro)
            profit = round(operation_data.amount * 0.92, 6)
        elif operation_data.result == "LOSS":
            profit = round(-operation_data.amount, 6)
        else:  # DRAW
            profit = 0.0

    # Crear operación
    new_operation = Operation(
        session_id=operation_data.session_id,
        result=operation_data.result,
        risk_percent=operation_data.risk_percent,
        amount=operation_data.amount,
        profit=profit,
        comment=operation_data.comment,
        created_at=datetime.utcnow()
    )

    db.add(new_operation)

    # Actualizar contador de pérdidas de la sesión (campo existente)
    if operation_data.result == "LOSS":
        session.loss_count = (session.loss_count or 0) + 1

    # Actualizar capital de la cuenta (neto)
    account.current_capital = (account.current_capital or 0) + profit

    db.commit()
    db.refresh(new_operation)

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
    account = db.query(Account).filter(Account.id == trading_day.account_id).first()
    
    if account.user_id != user_id:
        return []
    
    # Obtener operaciones
    operations = db.query(Operation).filter(
        Operation.session_id == session_id
    ).order_by(Operation.created_at.desc()).all()
    
    return operations