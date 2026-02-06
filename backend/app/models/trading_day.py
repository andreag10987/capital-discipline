from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class TradingDay(Base):
    __tablename__ = "trading_days"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_capital = Column(Float, nullable=False)
    status = Column(String, default="active")
    blocked_until = Column(DateTime, nullable=True)
    loss_count = Column(Integer, default=0)
    drawdown = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('account_id', 'date', name='unique_account_date'),
    )
    
    account = relationship("Account", back_populates="trading_days")
    sessions = relationship("TradingSession", back_populates="trading_day")