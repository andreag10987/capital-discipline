from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class OperationCreate(BaseModel):
    session_id: int
    result: str = Field(..., pattern="^(WIN|LOSS|DRAW)$")
    risk_percent: int = Field(..., ge=2, le=3)
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