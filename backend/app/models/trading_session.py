from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class TradingSession(Base):
    __tablename__ = "trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    trading_day_id = Column(Integer, ForeignKey("trading_days.id"), nullable=False)
    session_number = Column(Integer, nullable=False)
    status = Column(String, default="active")
    loss_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('session_number >= 1 AND session_number <= 3', name='check_session_number'),
    )
    
    trading_day = relationship("TradingDay", back_populates="sessions")
    operations = relationship("Operation", back_populates="session")