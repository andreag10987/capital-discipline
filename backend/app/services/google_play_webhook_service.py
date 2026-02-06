"""
Servicio para procesar webhooks de Google Play.
Google envía notificaciones sobre cambios en suscripciones.
"""

from sqlalchemy.orm import Session
from datetime import datetime
import base64
import json

from ..models.google_play_purchase import GooglePlayPurchase
from ..models.subscription import Subscription
from .abuse_detection import log_abuse_event


def process_google_play_notification(db: Session, notification_data: dict) -> dict:
    """
    Procesa una notificación de Google Play Real-Time Developer Notifications (RTDN).
    
    Args:
        db: Sesión de base de datos
        notification_data: Datos del webhook de Google
    
    Returns:
        dict con resultado del procesamiento
    """
    try:
        # Decodificar mensaje de Pub/Sub
        message = notification_data.get('message', {})
        data_encoded = message.get('data', '')
        
        # Decodificar base64
        data_decoded = base64.b64decode(data_encoded).decode('utf-8')
        data = json.loads(data_decoded)
        
        # Extraer información
        notification_type = data.get('notificationType')
        subscription_notification = data.get('subscriptionNotification', {})
        
        notification_type_id = subscription_notification.get('notificationType')
        purchase_token = subscription_notification.get('purchaseToken')
        subscription_id = subscription_notification.get('subscriptionId')
        
        if not purchase_token:
            return {"status": "skipped", "reason": "no_purchase_token"}
        
        # Buscar compra en base de datos
        purchase = db.query(GooglePlayPurchase).filter(
            GooglePlayPurchase.purchase_token == purchase_token
        ).first()
        
        if not purchase:
            return {"status": "skipped", "reason": "purchase_not_found"}
        
        # Procesar según tipo de notificación
        result = handle_notification_type(db, purchase, notification_type_id)
        
        db.commit()
        
        return {
            "status": "processed",
            "notification_type": notification_type_id,
            "purchase_id": purchase.id,
            "action": result
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


def handle_notification_type(db: Session, purchase: GooglePlayPurchase, notification_type: int) -> str:
    """
    Maneja diferentes tipos de notificaciones de Google Play.
    
    Tipos de notificación:
    1 = SUBSCRIPTION_RECOVERED (Recuperada después de problema de pago)
    2 = SUBSCRIPTION_RENEWED (Renovada exitosamente)
    3 = SUBSCRIPTION_CANCELED (Cancelada por el usuario)
    4 = SUBSCRIPTION_PURCHASED (Nueva compra)
    5 = SUBSCRIPTION_ON_HOLD (En espera por problema de pago)
    6 = SUBSCRIPTION_IN_GRACE_PERIOD (En período de gracia)
    7 = SUBSCRIPTION_RESTARTED (Reiniciada)
    8 = SUBSCRIPTION_PRICE_CHANGE_CONFIRMED (Cambio de precio confirmado)
    9 = SUBSCRIPTION_DEFERRED (Diferida)
    10 = SUBSCRIPTION_PAUSED (Pausada)
    11 = SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED (Cambio en programación de pausa)
    12 = SUBSCRIPTION_REVOKED (Revocada - reembolso)
    13 = SUBSCRIPTION_EXPIRED (Expirada)
    """
    
    notification_types = {
        1: handle_subscription_recovered,
        2: handle_subscription_renewed,
        3: handle_subscription_canceled,
        4: handle_subscription_purchased,
        5: handle_subscription_on_hold,
        6: handle_subscription_grace_period,
        7: handle_subscription_restarted,
        12: handle_subscription_revoked,
        13: handle_subscription_expired
    }
    
    handler = notification_types.get(notification_type)
    
    if handler:
        return handler(db, purchase)
    else:
        return f"unhandled_notification_type_{notification_type}"


def handle_subscription_recovered(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción recuperada después de problema de pago."""
    purchase.purchase_state = "PURCHASED"
    purchase.auto_renewing = True
    
    if purchase.subscription:
        purchase.subscription.status = "ACTIVE"
    
    return "recovered"


def handle_subscription_renewed(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción renovada exitosamente."""
    purchase.purchase_state = "PURCHASED"
    purchase.auto_renewing = True
    
    # Aquí podrías actualizar expiry_time_millis si Google lo provee en la notificación
    
    if purchase.subscription:
        purchase.subscription.status = "ACTIVE"
    
    return "renewed"


def handle_subscription_canceled(db: Session, purchase: GooglePlayPurchase) -> str:
    """Usuario canceló la suscripción."""
    purchase.purchase_state = "CANCELED"
    purchase.auto_renewing = False
    
    if purchase.subscription:
        purchase.subscription.status = "CANCELED"
        purchase.subscription.canceled_at = datetime.utcnow()
    
    return "canceled"


def handle_subscription_purchased(db: Session, purchase: GooglePlayPurchase) -> str:
    """Nueva compra realizada."""
    purchase.purchase_state = "PURCHASED"
    purchase.auto_renewing = True
    
    if purchase.subscription:
        purchase.subscription.status = "ACTIVE"
    
    return "purchased"


def handle_subscription_on_hold(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción en espera por problema de pago."""
    purchase.purchase_state = "PENDING"
    
    if purchase.subscription:
        purchase.subscription.status = "PAYMENT_PENDING"
    
    # Registrar evento de abuso (posible fraude)
    log_abuse_event(
        db=db,
        event_type="payment_on_hold",
        severity="medium",
        user_id=purchase.user_id,
        description=f"Google Play subscription on hold for purchase {purchase.id}"
    )
    
    return "on_hold"


def handle_subscription_grace_period(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción en período de gracia."""
    purchase.purchase_state = "PENDING"
    
    if purchase.subscription:
        purchase.subscription.status = "PAYMENT_PENDING"
    
    return "grace_period"


def handle_subscription_restarted(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción reiniciada."""
    purchase.purchase_state = "PURCHASED"
    purchase.auto_renewing = True
    
    if purchase.subscription:
        purchase.subscription.status = "ACTIVE"
    
    return "restarted"


def handle_subscription_revoked(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción revocada (reembolso)."""
    purchase.purchase_state = "REFUNDED"
    purchase.auto_renewing = False
    
    if purchase.subscription:
        purchase.subscription.status = "CANCELED"
        purchase.subscription.canceled_at = datetime.utcnow()
    
    # Registrar evento de abuso (posible fraude)
    log_abuse_event(
        db=db,
        event_type="subscription_refunded",
        severity="high",
        user_id=purchase.user_id,
        description=f"Google Play subscription refunded for purchase {purchase.id}"
    )
    
    return "revoked"


def handle_subscription_expired(db: Session, purchase: GooglePlayPurchase) -> str:
    """Suscripción expirada."""
    purchase.purchase_state = "CANCELED"
    purchase.auto_renewing = False
    
    if purchase.subscription:
        purchase.subscription.status = "EXPIRED"
    
    return "expired"


def verify_webhook_signature(request_data: str, signature: str) -> bool:
    """
    Verifica la firma del webhook de Google Play.
    
    Para producción, deberías verificar la firma usando tu clave pública.
    Por ahora retornamos True.
    """
    # TODO: Implementar verificación de firma en producción
    # https://developer.android.com/google/play/billing/rtdn-reference#verify
    return True