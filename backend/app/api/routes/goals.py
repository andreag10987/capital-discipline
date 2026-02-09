from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.goal_extended import (
    GoalCreateExtended, GoalUpdate, GoalResponseExtended, GoalProgressResponse
)
from ...schemas.daily_plan import CalendarRangeRequest, CalendarResponse, DailyPlanCloseRequest, DailyPlanResponse
from ...services import goal_service, daily_plan_service

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.post("/", response_model=GoalResponseExtended, status_code=201)
def create_goal(
    goal_data: GoalCreateExtended,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Crear nuevo objetivo con configuración completa
    
    - **target_capital**: Meta de capital en USDT
    - **risk_percent**: 2% o 3% de riesgo por operación
    - **sessions_per_day**: 2 o 3 sesiones diarias
    - **ops_per_session**: 4 o 5 operaciones por sesión
    - **winrate_estimate**: Tasa de acierto esperada (50%-80%)
    """
    return goal_service.create_goal(db, current_user.id, goal_data, accept_language)

@router.get("/", response_model=list[GoalResponseExtended])
def get_all_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener todos los objetivos del usuario
    """
    return goal_service.get_goals(db, current_user.id, accept_language)

@router.get("/{goal_id}", response_model=GoalResponseExtended)
def get_goal_detail(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener detalle de un objetivo específico
    """
    return goal_service.get_goal(db, current_user.id, goal_id, accept_language)

@router.put("/{goal_id}", response_model=GoalResponseExtended)
def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Actualizar configuración del objetivo
    
    Permite modificar:
    - target_capital
    - risk_percent
    - sessions_per_day
    - ops_per_session
    - winrate_estimate
    - status (ACTIVE, PAUSED, COMPLETED, CANCELLED)
    """
    return goal_service.update_goal(db, current_user.id, goal_id, goal_data, accept_language)

@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Eliminar objetivo (esto también eliminará planes diarios asociados)
    """
    goal_service.delete_goal(db, current_user.id, goal_id, accept_language)
    return None

@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
def get_goal_progress(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener progreso detallado del objetivo
    
    Incluye:
    - Capital actual vs objetivo
    - Progreso porcentual
    - Días transcurridos
    - Winrate real (desde inicio del objetivo)
    - ETA (días estimados para alcanzar objetivo)
    - Factor de crecimiento diario
    """
    return goal_service.get_goal_progress(db, current_user.id, goal_id, accept_language)

@router.post("/{goal_id}/calendar", response_model=CalendarResponse)
def get_goal_calendar(
    goal_id: int,
    range_request: Optional[CalendarRangeRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Obtener almanaque (calendario) del objetivo
    
    Muestra planes diarios con:
    - Operaciones planificadas vs realizadas
    - Ganancias/pérdidas
    - Estado (PLANNED, IN_PROGRESS, COMPLETED, BLOCKED)
    - Winrate real del período
    
    **Filtros opcionales:**
    - from_date + to_date: rango específico
    - days: últimos N días
    - Si no se especifica: desde inicio del objetivo hasta hoy
    """
    return daily_plan_service.get_calendar(
        db, current_user.id, goal_id, range_request, accept_language
    )

@router.post("/{goal_id}/close-day", response_model=DailyPlanResponse)
def close_goal_day(
    goal_id: int,
    close_request: Optional[DailyPlanCloseRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cerrar manualmente un día del calendario del objetivo.

    Body opcional:
    - date: fecha a cerrar (por defecto hoy)
    - notes: nota de cierre
    - blocked_reason: si viene, el día queda BLOCKED
    - realized_pnl: ajuste manual del PnL del día
    """
    return daily_plan_service.close_goal_day(
        db=db,
        user_id=current_user.id,
        goal_id=goal_id,
        close_data=close_request,
    )
