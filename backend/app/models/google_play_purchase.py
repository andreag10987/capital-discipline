"""
Modelo para compras de Google Play.
Almacena y rastrea suscripciones compradas a través de Google Play Store.
"""

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class GooglePlayPurchase(Base):
    __tablename__ = "google_play_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    
    # Datos de Google Play
    purchase_token = Column(String(512), nullable=False, unique=True, index=True)
    product_id = Column(String(255), nullable=False, index=True)
    order_id = Column(String(255), nullable=True)
    package_name = Column(String(255), nullable=False)
    
    # Estado de la compra
    purchase_state = Column(String(50), nullable=False, index=True)
    acknowledgement_state = Column(String(50), nullable=False)
    
    # Timestamps
    purchase_time_millis = Column(BigInteger, nullable=False)
    expiry_time_millis = Column(BigInteger, nullable=True)
    auto_renewing = Column(Boolean, nullable=True)
    
    # Verificación
    verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Raw response
    google_response = Column(JSON, nullable=True)
    
    # Timestamps locales
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    user = relationship("User", backref="google_play_purchases")
    subscription = relationship("Subscription", backref="google_play_purchase")
    
    def __repr__(self):
        return f"<GooglePlayPurchase user={self.user_id} product={self.product_id} state={self.purchase_state}>"
    
    @property
    def is_active(self) -> bool:
        """Verifica si la compra está activa."""
        if self.purchase_state != "PURCHASED":
            return False
        
        if self.expiry_time_millis:
            expiry_timestamp = self.expiry_time_millis / 1000
            current_timestamp = datetime.utcnow().timestamp()
            return current_timestamp < expiry_timestamp
        
        return True
    
    @property
    def purchase_datetime(self) -> datetime:
        """Convierte purchase_time_millis a datetime."""
        return datetime.fromtimestamp(self.purchase_time_millis / 1000)
    
    @property
    def expiry_datetime(self) -> datetime:
        """Convierte expiry_time_millis a datetime."""
        if self.expiry_time_millis:
            return datetime.fromtimestamp(self.expiry_time_millis / 1000)
        return None