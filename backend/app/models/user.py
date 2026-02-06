from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Email verification (ETAPA 3)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True, index=True)
    email_verification_sent_at = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False, index=True)
    is_blocked = Column(Boolean, default=False, nullable=False, index=True)
    blocked_reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    
    account = relationship("Account", back_populates="user", uselist=False)