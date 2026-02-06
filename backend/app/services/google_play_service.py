"""
Servicio para verificación de compras de Google Play.
"""

from sqlalchemy.orm import Session
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json
import os

from ..models.google_play_purchase import GooglePlayPurchase
from ..models.subscription import Subscription
from ..models.plan import Plan
from ..config import settings
from .plan_service import create_subscription


def get_google_play_service():
    """
    Inicializa el servicio de Google Play Developer API.
    """
    if not settings.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON:
        raise ValueError("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON no configurado")
    
    # Cargar credenciales desde JSON
    credentials_info = json.loads(settings.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )
    
    service = build('androidpublisher', 'v3', credentials=credentials)
    return service


def verify_purchase(
    db: Session,
    user_id: int,
    purchase_token: str,
    product_id: str,
    package_name: str = None
) -> dict:
    """
    Verifica una compra con Google Play y la registra en la base de datos.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        purchase_token: Token de compra de Google
        product_id: ID del producto (ej: "basic_monthly")
        package_name: Nombre del paquete (opcional, usa el de config si no se provee)
    
    Returns:
        dict con información de la compra verificada
    """
    if not package_name:
        package_name = settings.GOOGLE_PLAY_PACKAGE_NAME
    
    # Verificar si la compra ya existe
    existing_purchase = db.query(GooglePlayPurchase).filter(
        GooglePlayPurchase.purchase_token == purchase_token
    ).first()
    
    if existing_purchase:
        return {
            "status": "already_verified",
            "purchase_id": existing_purchase.id,
            "verified": existing_purchase.verified
        }
    
    try:
        # Obtener servicio de Google Play
        service = get_google_play_service()
        
        # Verificar la compra con Google
        result = service.purchases().subscriptions().get(
            packageName=package_name,
            subscriptionId=product_id,
            token=purchase_token
        ).execute()
        
        # Extraer información
        purchase_time_millis = int(result.get('startTimeMillis', 0))
        expiry_time_millis = int(result.get('expiryTimeMillis', 0))
        auto_renewing = result.get('autoRenewing', False)
        payment_state = result.get('paymentState', 0)
        acknowledgement_state = result.get('acknowledgementState', 0)
        order_id = result.get('orderId', '')
        
        # Mapear estados
        purchase_state = "PURCHASED" if payment_state == 1 else "PENDING"
        ack_state = "ACKNOWLEDGED" if acknowledgement_state == 1 else "NOT_ACKNOWLEDGED"
        
        # Crear registro de compra
        purchase = GooglePlayPurchase(
            user_id=user_id,
            purchase_token=purchase_token,
            product_id=product_id,
            order_id=order_id,
            package_name=package_name,
            purchase_state=purchase_state,
            acknowledgement_state=ack_state,
            purchase_time_millis=purchase_time_millis,
            expiry_time_millis=expiry_time_millis,
            auto_renewing=auto_renewing,
            verified=True,
            verified_at=datetime.utcnow(),
            google_response=result
        )
        
        db.add(purchase)
        db.flush()
        
        # Mapear product_id a plan
        plan_mapping = {
            "basic_monthly": "BASIC",
            "basic_annual": "BASIC",
            "pro_monthly": "PRO",
            "pro_annual": "PRO"
        }
        
        plan_name = plan_mapping.get(product_id, "FREE")
        
        # Crear o actualizar suscripción
        if purchase_state == "PURCHASED":
            subscription = create_subscription(
                db=db,
                user_id=user_id,
                plan_name=plan_name,
                payment_provider="google_play"
            )
            
            purchase.subscription_id = subscription.id
        
        db.commit()
        
        # Reconocer compra si no está reconocida
        if ack_state == "NOT_ACKNOWLEDGED":
            acknowledge_purchase(service, package_name, product_id, purchase_token)
        
        return {
            "status": "verified",
            "purchase_id": purchase.id,
            "verified": True,
            "plan": plan_name,
            "expiry": purchase.expiry_datetime.isoformat() if purchase.expiry_datetime else None,
            "auto_renewing": auto_renewing
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error verifying purchase: {e}")
        raise ValueError(f"Error al verificar compra: {str(e)}")


def acknowledge_purchase(service, package_name: str, product_id: str, purchase_token: str):
    """
    Reconoce una compra en Google Play.
    Esto debe hacerse dentro de 3 días de la compra.
    """
    try:
        service.purchases().subscriptions().acknowledge(
            packageName=package_name,
            subscriptionId=product_id,
            token=purchase_token
        ).execute()
        
        print(f"Purchase acknowledged: {purchase_token}")
        return True
    except Exception as e:
        print(f"Error acknowledging purchase: {e}")
        return False


def check_subscription_status(db: Session, user_id: int) -> dict:
    """
    Verifica el estado actual de la suscripción de Google Play del usuario.
    """
    # Obtener la compra más reciente del usuario
    purchase = db.query(GooglePlayPurchase).filter(
        GooglePlayPurchase.user_id == user_id,
        GooglePlayPurchase.verified == True
    ).order_by(GooglePlayPurchase.created_at.desc()).first()
    
    if not purchase:
        return {
            "has_subscription": False,
            "plan": "FREE"
        }
    
    # Verificar si está activa
    is_active = purchase.is_active
    
    if not is_active:
        return {
            "has_subscription": False,
            "plan": "FREE",
            "expired_at": purchase.expiry_datetime.isoformat() if purchase.expiry_datetime else None
        }
    
    # Obtener plan asociado
    plan_name = "FREE"
    if purchase.subscription:
        plan_name = purchase.subscription.plan.name
    
    return {
        "has_subscription": True,
        "plan": plan_name,
        "purchase_id": purchase.id,
        "expiry": purchase.expiry_datetime.isoformat() if purchase.expiry_datetime else None,
        "auto_renewing": purchase.auto_renewing
    }


def cancel_google_play_subscription(db: Session, user_id: int) -> bool:
    """
    Marca una suscripción de Google Play como cancelada.
    Nota: El usuario debe cancelar desde Google Play, esto solo actualiza nuestro registro.
    """
    purchase = db.query(GooglePlayPurchase).filter(
        GooglePlayPurchase.user_id == user_id,
        GooglePlayPurchase.verified == True,
        GooglePlayPurchase.purchase_state == "PURCHASED"
    ).order_by(GooglePlayPurchase.created_at.desc()).first()
    
    if not purchase:
        return False
    
    purchase.purchase_state = "CANCELED"
    purchase.auto_renewing = False
    
    # Cancelar suscripción asociada
    if purchase.subscription:
        purchase.subscription.status = "CANCELED"
        purchase.subscription.canceled_at = datetime.utcnow()
    
    db.commit()
    return True