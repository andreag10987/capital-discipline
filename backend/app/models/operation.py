from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class OperationResult(str, enum.Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"

class Operation(Base):
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("trading_sessions.id"), nullable=False)
    result = Column(Enum(OperationResult), nullable=False)
    risk_percent = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    profit = Column(Float, default=0.0)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('risk_percent IN (2, 3)', name='check_risk_percent'),
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
    
    session = relationship("TradingSession", back_populates="operations")