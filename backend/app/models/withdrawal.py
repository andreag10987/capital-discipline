from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Withdrawal(Base):
    __tablename__ = "withdrawals"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True, index=True)
    
    amount = Column(Float, nullable=False)
    withdrawn_at = Column(DateTime, nullable=False)
    note = Column(Text, nullable=True)
    
    # Snapshots de capital
    capital_before = Column(Float, nullable=False)
    capital_after = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_withdrawal_amount_positive'),
    )
    
    # Relationships
    account = relationship("Account", backref="withdrawals")
    goal = relationship("Goal", backref="withdrawals")