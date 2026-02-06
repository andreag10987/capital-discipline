"""
Schemas para planes y suscripciones.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlanFeatures(BaseModel):
    """Features del plan."""
    max_daily_sessions: int
    max_ops_per_session: int
    max_active_goals: int
    history_days: int
    can_export_pdf: bool
    can_export_excel: bool
    can_see_projections: bool
    can_recalculate_withdrawals: bool


class PlanResponse(BaseModel):
    """Respuesta con información del plan."""
    id: int
    name: str
    display_name_es: str
    display_name_en: str
    price_usd: float
    features: dict
    is_active: bool
    
    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Respuesta con información de suscripción."""
    id: int
    user_id: int
    plan_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    payment_provider: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPlanResponse(BaseModel):
    """Respuesta con plan del usuario + suscripción."""
    plan: PlanResponse
    subscription: Optional[SubscriptionResponse]
    is_active: bool