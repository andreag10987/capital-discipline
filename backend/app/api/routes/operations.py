from fastapi import APIRouter, Depends, Header, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...models.operation import Operation
from ...models.trading_session import TradingSession
from ...schemas.operation import OperationCreate, OperationResponse
from ...services.operation_service import create_operation, get_operations_by_session
from ...middleware.plan_permissions import get_operation_limit

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post("", response_model=OperationResponse)
def add_operation(
    operation_data: OperationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en"),
    plan_and_limit: tuple = Depends(get_operation_limit),  # ← Plan limit
):
    """
    Crea una nueva operación.
    Protegido por límite de plan: max_ops_per_session.
    """
    plan, max_ops = plan_and_limit
    lang = "es" if "es" in accept_language.lower() else "en"
    
    # Verificar límite del plan
    session = db.query(TradingSession).filter(
        TradingSession.id == operation_data.session_id
    ).first()
    
    if session:
        op_count = db.query(Operation).filter(
            Operation.session_id == session.id
        ).count()
        
        if op_count >= max_ops:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "plan_limit_reached",
                    "message": f"Maximum operations per session ({max_ops}) reached. Upgrade your plan for more operations.",
                    "current_plan": plan.name,
                    "limit": max_ops
                }
            )
    
    return create_operation(db, current_user.id, operation_data, lang)


@router.get("", response_model=List[OperationResponse])
def get_session_operations(
    session_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene las operaciones de una sesión."""
    return get_operations_by_session(db, session_id, current_user.id)