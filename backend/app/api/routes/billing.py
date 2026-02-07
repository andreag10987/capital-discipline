"""
Rutas para Google Play Billing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas.google_play import WebhookNotification, WebhookResponse
from ...services.google_play_webhook_service import process_google_play_notification

from ...database import get_db
from ...models.user import User
from ..deps import get_current_user
from ...schemas.google_play import (
    VerifyPurchaseRequest,
    VerifyPurchaseResponse,
    SubscriptionStatusResponse
)
from ...services.google_play_service import (
    verify_purchase,
    check_subscription_status,
    cancel_google_play_subscription
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/verify", response_model=VerifyPurchaseResponse)
def verify_purchase_endpoint(
    request: VerifyPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Verifica una compra de Google Play.
    
    El cliente Android envía:
    - purchase_token: Token de compra de Google Play
    - product_id: ID del producto (ej: "basic_monthly")
    - package_name: (opcional) Nombre del paquete Android
    """
    try:
        result = verify_purchase(
            db=db,
            user_id=current_user.id,
            purchase_token=request.purchase_token,
            product_id=request.product_id,
            package_name=request.package_name
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "verification_failed", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "Error al verificar compra"}
        )


@router.get("/status", response_model=SubscriptionStatusResponse)
def get_subscription_status_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Obtiene el estado actual de la suscripción de Google Play del usuario.
    """
    status = check_subscription_status(db, current_user.id)
    return status


@router.post("/cancel")
def cancel_subscription_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth)
):
    """
    Cancela la suscripción de Google Play.
    
    Nota: El usuario debe cancelar desde Google Play Store.
    Este endpoint solo actualiza nuestro registro local.
    """
    success = cancel_google_play_subscription(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "no_subscription", "message": "No se encontró suscripción activa"}
        )
    
    return {
        "message": "Subscription canceled successfully",
        "status": "canceled"
    }

@router.post("/webhook", response_model=WebhookResponse)
def google_play_webhook(
    notification: WebhookNotification,
    db: Session = Depends(get_db)
):
    """
    Endpoint webhook para Google Play Real-Time Developer Notifications.
    
    Google envía notificaciones sobre:
    - Renovaciones de suscripciones
    - Cancelaciones
    - Problemas de pago
    - Reembolsos
    - Etc.
    
    Configurar en Google Play Console:
    Monetize → Monetization setup → Real-time developer notifications
    """
    result = process_google_play_notification(db, notification.dict())
    return result