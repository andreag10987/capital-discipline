from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    capital = Column(Float, nullable=False)
    payout = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('payout >= 0.80 AND payout <= 0.92', name='check_payout_range'),
        CheckConstraint('capital > 0', name='check_capital_positive'),
    )
    
    user = relationship("User", back_populates="account")
    trading_days = relationship("TradingDay", back_populates="account")
    goal = relationship("Goal", back_populates="account", uselist=False)