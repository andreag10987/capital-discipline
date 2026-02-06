"""
Schemas para Google Play Billing.
"""

from pydantic import BaseModel
from typing import Optional


class VerifyPurchaseRequest(BaseModel):
    """Request para verificar una compra."""
    purchase_token: str
    product_id: str
    package_name: Optional[str] = None


class VerifyPurchaseResponse(BaseModel):
    """Response de verificación de compra."""
    status: str  # verified, already_verified, error
    purchase_id: Optional[int] = None
    verified: bool
    plan: Optional[str] = None
    expiry: Optional[str] = None
    auto_renewing: Optional[bool] = None


class SubscriptionStatusResponse(BaseModel):
    """Response de estado de suscripción."""
    has_subscription: bool
    plan: str
    purchase_id: Optional[int] = None
    expiry: Optional[str] = None
    auto_renewing: Optional[bool] = None
    expired_at: Optional[str] = None

class WebhookNotification(BaseModel):
    """Schema para notificaciones webhook de Google Play."""
    message: dict
    subscription: Optional[str] = None


class WebhookResponse(BaseModel):
    """Response del procesamiento de webhook."""
    status: str
    notification_type: Optional[int] = None
    purchase_id: Optional[int] = None
    action: Optional[str] = None
    reason: Optional[str] = None
    message: Optional[str] = None