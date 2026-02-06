from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WithdrawalCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Monto a retirar en USDT")
    note: Optional[str] = Field(None, max_length=500, description="Nota opcional del retiro")

class WithdrawalResponse(BaseModel):
    id: int
    account_id: int
    goal_id: Optional[int]
    amount: float
    withdrawn_at: datetime
    note: Optional[str]
    capital_before: float
    capital_after: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class WithdrawalListResponse(BaseModel):
    withdrawals: list[WithdrawalResponse]
    total_withdrawn: float
    count: int