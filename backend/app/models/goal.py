from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, Boolean, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from ..database import Base

class GoalStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True, nullable=False)
    
    # Objetivo
    target_capital = Column(Float, nullable=False)
    
    # Snapshots iniciales
    start_capital_snapshot = Column(Float, nullable=True)  # Se llena al crear
    start_date = Column(Date, nullable=True)
    payout_snapshot = Column(Float, nullable=True)
    
    # Configuración del plan
    risk_percent = Column(Integer, default=2, nullable=True)
    sessions_per_day = Column(Integer, default=2, nullable=True)
    ops_per_session = Column(Integer, default=5, nullable=True)
    winrate_estimate = Column(Float, default=0.60, nullable=True)
    
    # Estado
    status = Column(SQLEnum(GoalStatus), default=GoalStatus.ACTIVE)
    not_recommended = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('target_capital > 0', name='check_target_capital_positive'),
        CheckConstraint('risk_percent IN (2, 3)', name='check_risk_percent_valid'),
        CheckConstraint('sessions_per_day IN (2, 3)', name='check_sessions_per_day_valid'),
        CheckConstraint('ops_per_session IN (4, 5)', name='check_ops_per_session_valid'),
        CheckConstraint('winrate_estimate >= 0.50 AND winrate_estimate <= 0.80', name='check_winrate_valid'),
    )
    
    # Relationships
    account = relationship("Account", back_populates="goal")
    daily_plans = relationship("GoalDailyPlan", back_populates="goal", cascade="all, delete-orphan")