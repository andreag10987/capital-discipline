from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OperationCreate(BaseModel):
    session_id: int
    result: str = Field(..., pattern="^(WIN|LOSS|DRAW)$")
    risk_percent: int = Field(..., ge=2, le=3)

    # ✅ Opcional: si no llega, el backend lo calcula con el capital actual y risk_percent
    amount: Optional[float] = Field(default=None, gt=0)

    # ✅ Opcional: si no llega, el backend lo calcula (WIN=+0.92*amount, LOSS=-amount, DRAW=0)
    profit: Optional[float] = None

    comment: Optional[str] = None


class OperationResponse(BaseModel):
    id: int
    session_id: int
    result: str
    risk_percent: int
    amount: float
    profit: float
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
