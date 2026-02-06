from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.withdrawal import (
    WithdrawalCreate, WithdrawalResponse, WithdrawalListResponse
)
from ...services import withdrawal_service

router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])

@router.post("/", response_model=WithdrawalResponse, status_code=201)
def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Registrar un retiro de capital
    
    - Reduce el capital de la cuenta automáticamente
    - Guarda snapshot de capital antes/después
    - Se asocia al objetivo activo si existe
    - Nota opcional para referencia
    
    **IMPORTANTE:** El retiro afecta el progreso del objetivo
    """
    return withdrawal_service.create_withdrawal(
        db, current_user.id, withdrawal_data, accept_language
    )

@router.get("/", response_model=WithdrawalListResponse)
def get_withdrawals(
    goal_id: Optional[int] = Query(None, description="Filtrar por objetivo específico"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de retiros a retornar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener historial de retiros
    
    - Ordenados del más reciente al más antiguo
    - Opcionalmente filtrar por objetivo
    - Incluye total retirado y conteo
    """
    return withdrawal_service.get_withdrawals(
        db, current_user.id, goal_id, limit, accept_language
    )

@router.get("/{withdrawal_id}", response_model=WithdrawalResponse)
def get_withdrawal_detail(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener detalle de un retiro específico
    """
    return withdrawal_service.get_withdrawal(
        db, current_user.id, withdrawal_id, accept_language
    )

@router.delete("/{withdrawal_id}", status_code=204)
def delete_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Eliminar registro de retiro
    
    **ADVERTENCIA:** Esto solo elimina el registro histórico.
    NO devuelve el dinero a la cuenta automáticamente.
    Use solo para correcciones de registros erróneos.
    """
    withdrawal_service.delete_withdrawal(
        db, current_user.id, withdrawal_id, accept_language
    )
    return None