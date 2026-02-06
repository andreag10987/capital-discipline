from pydantic import BaseModel, Field
from datetime import datetime

class AccountCreate(BaseModel):
    capital: float = Field(..., gt=0)
    payout: float = Field(..., ge=0.80, le=0.92)

class AccountUpdate(BaseModel):
    capital: float | None = Field(None, gt=0)
    payout: float | None = Field(None, ge=0.80, le=0.92)

class AccountResponse(BaseModel):
    id: int
    user_id: int
    capital: float
    payout: float
    created_at: datetime
    
    class Config:
        from_attributes = True