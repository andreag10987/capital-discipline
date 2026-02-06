from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class DailyPlanStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

class GoalDailyPlan(Base):
    __tablename__ = "goal_daily_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Capital del día
    capital_start_of_day = Column(Float, nullable=False)
    
    # Plan
    planned_sessions = Column(Integer, nullable=False)
    planned_ops_total = Column(Integer, nullable=False)
    planned_stake = Column(Float, nullable=False)
    expected_win_profit = Column(Float, nullable=False)
    expected_loss = Column(Float, nullable=False)
    
    # Realidad (actualizado al registrar operaciones)
    actual_sessions = Column(Integer, default=0)
    actual_ops = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    realized_pnl = Column(Float, default=0.0)
    
    # Estado
    status = Column(SQLEnum(DailyPlanStatus), default=DailyPlanStatus.PLANNED)
    notes = Column(Text, nullable=True)
    blocked_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goal = relationship("Goal", back_populates="daily_plans")
    
    __table_args__ = (
        # Constraint único: un plan por día por objetivo
        {'sqlite_autoincrement': True},
    )