from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from ..models.goal_daily_plan import DailyPlanStatus

class DailyPlanCreate(BaseModel):
    goal_id: int
    date: date
    capital_start_of_day: float
    planned_sessions: int
    planned_ops_total: int
    planned_stake: float
    expected_win_profit: float
    expected_loss: float

class DailyPlanUpdate(BaseModel):
    actual_sessions: Optional[int] = None
    actual_ops: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    realized_pnl: Optional[float] = None
    status: Optional[DailyPlanStatus] = None
    notes: Optional[str] = None
    blocked_reason: Optional[str] = None

class DailyPlanCloseRequest(BaseModel):
    date: Optional[date] = None
    notes: Optional[str] = None
    blocked_reason: Optional[str] = None
    realized_pnl: Optional[float] = None

class DailyPlanResponse(BaseModel):
    id: int
    goal_id: int
    date: date
    
    # Capital
    capital_start_of_day: float
    
    # Plan
    planned_sessions: int
    planned_ops_total: int
    planned_stake: float
    expected_win_profit: float
    expected_loss: float
    
    # Realidad
    actual_sessions: int
    actual_ops: int
    wins: int
    losses: int
    draws: int
    realized_pnl: float
    
    # Estado
    status: DailyPlanStatus
    notes: Optional[str]
    blocked_reason: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CalendarRangeRequest(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    days: Optional[int] = Field(None, ge=1, le=365, description="Últimos N días")

class CalendarResponse(BaseModel):
    goal_id: int
    daily_plans: list[DailyPlanResponse]
    total_days: int
    completed_days: int
    blocked_days: int
    total_pnl: float
    total_wins: int
    total_losses: int
    total_draws: int
    real_winrate: Optional[float]
