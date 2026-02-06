"""
Modelo para almacenar huellas digitales de dispositivos.
Usado para detectar trial abuse (múltiples cuentas desde el mismo dispositivo).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Hash único del dispositivo (SHA-256)
    fingerprint_hash = Column(String(64), nullable=False, index=True)
    
    # Metadata del dispositivo (para logging/debugging)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4: 15 chars, IPv6: 45 chars
    screen_resolution = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    platform = Column(String(50), nullable=True)
    
    # Tracking
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    login_count = Column(Integer, default=1, nullable=False)
    
    # Relación
    user = relationship("User", backref="device_fingerprints")
    
    # Constraint: un usuario no puede tener el mismo fingerprint duplicado
    __table_args__ = (
        UniqueConstraint('fingerprint_hash', 'user_id', name='unique_device_per_user'),
    )
    
    def __repr__(self):
        return f"<DeviceFingerprint user={self.user_id} hash={self.fingerprint_hash[:8]}... logins={self.login_count}>"