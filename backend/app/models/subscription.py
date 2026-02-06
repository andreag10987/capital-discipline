from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(20), nullable=False)  # ACTIVE, CANCELED, EXPIRED, PENDING
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL = sin límite (FREE/trial eterno)
    
    # Para integraciones de pago (Etapa 6)
    payment_provider = Column(String(50), nullable=True)  # 'google_play', 'manual', etc.
    external_subscription_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    user = relationship("User", backref="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    
    def is_active(self) -> bool:
        """Verifica si la suscripción está activa."""
        if self.status != "ACTIVE":
            return False
        if self.end_date is None:
            return True
        return datetime.utcnow() < self.end_date
    
    def __repr__(self):
        return f"<Subscription user={self.user_id} plan={self.plan_id} status={self.status}>"