"""
Modelo para almacenar identidades OAuth vinculadas a usuarios.
Permite login con Google, Facebook, etc.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class UserIdentity(Base):
    __tablename__ = "user_identities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Proveedor OAuth
    provider = Column(String(50), nullable=False, index=True)
    # Valores: "google", "facebook"
    
    # ID del usuario en el proveedor
    provider_user_id = Column(String(255), nullable=False, index=True)
    
    # Información del perfil (opcional, para display)
    provider_email = Column(String(255), nullable=True)
    provider_name = Column(String(255), nullable=True)
    provider_picture = Column(String(512), nullable=True)
    
    # Tokens OAuth (para refresh si es necesario)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación
    user = relationship("User", backref="oauth_identities")
    
    # Constraint: un provider_user_id solo puede estar vinculado a un usuario
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='unique_provider_user'),
    )
    
    def __repr__(self):
        return f"<UserIdentity user={self.user_id} provider={self.provider} provider_id={self.provider_user_id}>"
    
    def is_token_valid(self) -> bool:
        """Verifica si el access_token aún es válido."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at