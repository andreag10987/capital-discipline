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
    """Crea una nueva operación y actualiza los contadores de la sesión."""
    
    # Verificar que la sesión pertenece al usuario
    session = db.query(TradingSession).filter(
        TradingSession.id == operation_data.session_id
    ).first()
    
    if not session:
        raise ValueError("Session not found" if lang == "en" else "Sesión no encontrada")
    
    trading_day = db.query(TradingDay).filter(TradingDay.id == session.trading_day_id).first()
    account = db.query(Account).filter(Account.id == trading_day.account_id).first()
    
    if account.user_id != user_id:
        raise ValueError("Unauthorized" if lang == "en" else "No autorizado")
    
    # Crear operación
    new_operation = Operation(
        session_id=operation_data.session_id,
        result=operation_data.result,
        amount=operation_data.amount,
        profit=operation_data.profit if operation_data.profit is not None else 0.0,
        comment=operation_data.comment,
        created_at=datetime.utcnow()
    )
    
    db.add(new_operation)
    
    # Actualizar contadores de sesión
    if operation_data.result == "WIN":
        session.wins += 1
    elif operation_data.result == "LOSS":
        session.losses += 1
    elif operation_data.result == "DRAW":
        session.draws += 1
    
    session.total_operations += 1
    
    # Actualizar capital de la cuenta
    account.current_capital += (operation_data.profit if operation_data.profit else 0.0)
    
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