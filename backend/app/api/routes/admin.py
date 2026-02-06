"""
Rutas de administración.
Todas las rutas están protegidas con require_admin.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...middleware.admin_required import require_admin
from ...schemas.admin import (
    UserListResponse,
    UserDetailResponse,
    BlockUserRequest,
    ChangePlanRequest,
    SystemMetricsResponse
)
from ...services.admin_service import (
    get_users_list,
    get_user_detail,
    block_user,
    unblock_user,
    change_user_plan,
    get_system_metrics
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    plan: str = Query(None, description="Filter by plan: FREE, BASIC, PRO"),
    is_blocked: bool = Query(None, description="Filter by blocked status"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Lista todos los usuarios (solo admins).
    
    Filtros disponibles:
    - plan: FREE, BASIC, PRO
    - is_blocked: true/false
    - skip/limit: paginación
    """
    return get_users_list(db, skip, limit, plan, is_blocked)


@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user_detail_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Obtiene detalles completos de un usuario (solo admins).
    Incluye: plan, dispositivos, eventos de abuso, métricas.
    """
    user_detail = get_user_detail(db, user_id)
    
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "message": "User not found"}
        )
    
    return user_detail


@router.post("/users/{user_id}/block")
def block_user_endpoint(
    user_id: int,
    request: BlockUserRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Bloquea un usuario (solo admins).
    """
    success = block_user(db, user_id, request.reason)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "message": "User not found"}
        )
    
    return {
        "message": "User blocked successfully",
        "user_id": user_id,
        "reason": request.reason
    }


@router.post("/users/{user_id}/unblock")
def unblock_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Desbloquea un usuario (solo admins).
    """
    success = unblock_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "message": "User not found"}
        )
    
    return {
        "message": "User unblocked successfully",
        "user_id": user_id
    }


@router.patch("/users/{user_id}/plan")
def change_user_plan_endpoint(
    user_id: int,
    request: ChangePlanRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Cambia el plan de un usuario manualmente (solo admins).
    """
    result = change_user_plan(db, user_id, request.plan_name)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "message": "User not found"}
        )
    
    return {
        "message": "Plan changed successfully",
        **result
    }


@router.get("/metrics", response_model=SystemMetricsResponse)
def get_metrics_endpoint(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    Obtiene métricas generales del sistema (solo admins).
    - Total usuarios
    - Usuarios por plan
    - Usuarios activos
    - Conversiones
    - Eventos de abuso
    """
    return get_system_metrics(db)