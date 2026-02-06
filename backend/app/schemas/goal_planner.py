from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class GoalCreate(BaseModel):
    target_capital: float = Field(..., gt=0, description="Meta de capital en USDT")

class GoalUpdate(BaseModel):
    target_capital: float = Field(..., gt=0, description="Meta de capital en USDT")

class GoalResponse(BaseModel):
    id: int
    account_id: int
    target_capital: float
    current_capital: float
    progress_percent: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlanCalculateRequest(BaseModel):
    sessions_per_day: int = Field(..., ge=2, le=3, description="Sesiones por día: 2 o 3")
    ops_per_session: int = Field(..., ge=4, le=5, description="Operaciones por sesión: 4 o 5")
    risk_percent: int = Field(..., ge=2, le=3, description="Riesgo por operación: 2% o 3%")
    winrate: float = Field(..., ge=0.50, le=0.80, description="Tasa de acierto esperada: 50%-80%")

class PlanCalculateResponse(BaseModel):
    # Configuración del plan
    sessions_per_day: int
    ops_per_session: int
    ops_per_day: int
    risk_percent: int
    winrate: float
    
    # Capital y configuración actual
    current_capital: float
    payout: float
    target_capital: Optional[float]
    
    # Cálculos por operación
    stake_per_operation: float
    win_profit: float
    loss_amount: float
    expected_return_per_op: float
    
    # Factor de crecimiento
    daily_growth_factor: float
    
    # Proyecciones
    projection_15_days: float
    projection_30_days: float
    days_to_goal: Optional[int]
    
    # Alertas y warnings
    blocked_recommended: bool
    warnings: List[str]
    
    # Reglas/límites recordatorios
    limits_reminder: Dict[str, str]