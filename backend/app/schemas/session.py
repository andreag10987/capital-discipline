from pydantic import BaseModel, Field
from datetime import datetime

class SessionCreate(BaseModel):
    risk_percent: int = Field(..., ge=2, le=3)

class SessionResponse(BaseModel):
    id: int
    trading_day_id: int
    session_number: int
    status: str
    loss_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True