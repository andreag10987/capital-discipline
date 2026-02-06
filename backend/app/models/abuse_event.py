"""
Modelo para logging de eventos de abuso.
Permite rastrear y analizar patrones sospechosos.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class AbuseEvent(Base):
    __tablename__ = "abuse_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    
    fingerprint_hash = Column(String(64), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    
    description = Column(Text, nullable=True)
    event_metadata = Column(JSON, nullable=True)  # ← CAMBIADO de metadata a event_metadata
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user = relationship("User", backref="abuse_events")
    
    def __repr__(self):
        return f"<AbuseEvent type={self.event_type} severity={self.severity} user={self.user_id}>"