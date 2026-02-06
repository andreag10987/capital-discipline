from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # FREE, BASIC, PRO
    display_name_es = Column(String(100), nullable=False)
    display_name_en = Column(String(100), nullable=False)
    price_usd = Column(Float, nullable=False)
    features = Column(JSONB, nullable=False)  # Estructura JSON con límites
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def get_feature(self, feature_name: str, default=None):
        """Helper para obtener features del JSON."""
        return self.features.get(feature_name, default)
    
    def __repr__(self):
        return f"<Plan {self.name} - ${self.price_usd}>"