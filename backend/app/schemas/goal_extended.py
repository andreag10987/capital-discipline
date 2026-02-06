from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from ..models.goal import GoalStatus

class GoalCreateExtended(BaseModel):
    target_capital: float = Field(..., gt=0, description="Meta de capital en USDT")
    risk_percent: int = Field(2, ge=2, le=3, description="Riesgo por operación: 2% o 3%")
    sessions_per_day: int = Field(2, ge=2, le=3, description="Sesiones por día: 2 o 3")
    ops_per_session: int = Field(5, ge=4, le=5, description="Operaciones por sesión: 4 o 5")
    winrate_estimate: float = Field(0.60, ge=0.50, le=0.80, description="Tasa de acierto esperada: 50%-80%")

class GoalUpdate(BaseModel):
    target_capital: Optional[float] = Field(None, gt=0)
    risk_percent: Optional[int] = Field(None, ge=2, le=3)
    sessions_per_day: Optional[int] = Field(None, ge=2, le=3)
    ops_per_session: Optional[int] = Field(None, ge=4, le=5)
    winrate_estimate: Optional[float] = Field(None, ge=0.50, le=0.80)
    status: Optional[GoalStatus] = None

class GoalResponseExtended(BaseModel):
    id: int
    account_id: int
    target_capital: float
    start_capital_snapshot: float
    start_date: date
    payout_snapshot: float
    risk_percent: int
    sessions_per_day: int
    ops_per_session: int
    winrate_estimate: float
    status: GoalStatus
    not_recommended: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    current_capital: Optional[float] = None
    progress_percent: Optional[float] = None
    
    class Config:
        from_attributes = True

class GoalProgressResponse(BaseModel):
    goal: GoalResponseExtended
    current_capital: float
    capital_gained: float
    progress_percent: float
    days_elapsed: int
    real_winrate: Optional[float]
    estimated_days_to_goal: Optional[int]
    daily_growth_factor: float