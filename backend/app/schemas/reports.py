from pydantic import BaseModel
from typing import List
from datetime import date

class DailyMetric(BaseModel):
    date: date
    capital: float
    profit: float
    loss: float
    operations: int
    wins: int
    losses: int
    draws: int

class ReportResponse(BaseModel):
    metrics: List[DailyMetric]
    total_operations: int
    total_profit: float
    total_loss: float
    winrate: float
    avg_drawdown: float

class ProjectionResponse(BaseModel):
    days: int
    estimated_capital: float
    estimated_profit: float
    scenario: str