from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.goal_planner import (
    GoalCreate, GoalResponse, 
    PlanCalculateRequest, PlanCalculateResponse
)
from ...services.goal_planner_service import (
    create_or_update_goal, get_goal, delete_goal, calculate_plan
)

router = APIRouter(prefix="/goal-planner", tags=["goal-planner"])

@router.post("/goal", response_model=GoalResponse)
def create_update_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    """Crear o actualizar objetivo de capital"""
    lang = "es" if "es" in accept_language.lower() else "en"
    return create_or_update_goal(db, current_user.id, goal_data, lang)

@router.get("/goal", response_model=Optional[GoalResponse])
def get_user_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    """Obtener objetivo actual del usuario"""
    lang = "es" if "es" in accept_language.lower() else "en"
    return get_goal(db, current_user.id, lang)

@router.delete("/goal")
def delete_user_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    """Eliminar objetivo del usuario"""
    lang = "es" if "es" in accept_language.lower() else "en"
    delete_goal(db, current_user.id, lang)
    return {"message": "Goal deleted successfully"}

@router.post("/calculate", response_model=PlanCalculateResponse)
def calculate_trading_plan(
    plan_request: PlanCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    """Calcular plan de trading diario y proyecciones"""
    lang = "es" if "es" in accept_language.lower() else "en"
    return calculate_plan(db, current_user.id, plan_request, lang)