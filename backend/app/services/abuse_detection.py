"""
Servicio de detección de abuso.
Analiza patrones sospechosos y registra eventos.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ..models.user import User
from ..models.device_fingerprint import DeviceFingerprint
from ..models.abuse_event import AbuseEvent
from ..models.subscription import Subscription


def log_abuse_event(
    db: Session,
    event_type: str,
    severity: str,
    user_id: Optional[int] = None,
    fingerprint_hash: Optional[str] = None,
    ip_address: Optional[str] = None,
    description: Optional[str] = None,
    event_metadata: Optional[dict] = None  # ← CAMBIADO
) -> AbuseEvent:
    """
    Registra un evento de abuso en la base de datos.
    """
    event = AbuseEvent(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        fingerprint_hash=fingerprint_hash,
        ip_address=ip_address,
        description=description,
        event_metadata=event_metadata  # ← CAMBIADO
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


def check_device_trial_abuse(db: Session, fingerprint_hash: str) -> dict:
    """
    Verifica si un dispositivo está siendo usado para trial abuse.
    Retorna dict con:
    - is_abuse: bool
    - device_count: int (número de cuentas FREE desde este dispositivo)
    - should_block: bool (si debe bloquearse)
    """
    # Buscar todas las huellas digitales con este hash
    devices = db.query(DeviceFingerprint).filter(
        DeviceFingerprint.fingerprint_hash == fingerprint_hash
    ).all()
    
    if not devices:
        return {
            "is_abuse": False,
            "device_count": 0,
            "should_block": False,
            "users": []
        }
    
    # Obtener usuarios únicos
    user_ids = list(set([d.user_id for d in devices]))
    
    # Contar cuántos están en plan FREE
    free_count = 0
    for user_id in user_ids:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "ACTIVE"
        ).order_by(Subscription.created_at.desc()).first()
        
        # Si no tiene suscripción o está en FREE
        if not subscription or subscription.plan.name == "FREE":
            free_count += 1
    
    # Criterio de abuso: más de 3 cuentas FREE desde el mismo dispositivo
    is_abuse = free_count > 3
    should_block = free_count > 5  # Bloquear si tiene más de 5 cuentas
    
    return {
        "is_abuse": is_abuse,
        "device_count": len(user_ids),
        "free_accounts": free_count,
        "should_block": should_block,
        "users": user_ids
    }


def check_registration_rate(db: Session, ip_address: str, hours: int = 24) -> dict:
    """
    Verifica si hay demasiados registros desde la misma IP.
    Retorna dict con:
    - is_suspicious: bool
    - registration_count: int
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Buscar eventos de registro recientes desde esta IP
    events = db.query(AbuseEvent).filter(
        AbuseEvent.event_type == "registration",
        AbuseEvent.ip_address == ip_address,
        AbuseEvent.created_at >= cutoff
    ).count()
    
    # Criterio: más de 5 registros en 24 horas es sospechoso
    is_suspicious = events > 5
    
    return {
        "is_suspicious": is_suspicious,
        "registration_count": events,
        "hours": hours
    }


def record_device_fingerprint(
    db: Session,
    user_id: int,
    fingerprint_hash: str,
    metadata: dict,
    ip_address: Optional[str] = None
) -> DeviceFingerprint:
    """
    Registra o actualiza la huella digital del dispositivo.
    Detecta trial abuse automáticamente.
    """
    # Buscar si ya existe este dispositivo para este usuario
    existing = db.query(DeviceFingerprint).filter(
        DeviceFingerprint.user_id == user_id,
        DeviceFingerprint.fingerprint_hash == fingerprint_hash
    ).first()
    
    if existing:
        # Actualizar last_seen y login_count
        existing.last_seen = datetime.utcnow()
        existing.login_count += 1
        if ip_address:
            existing.ip_address = ip_address
        db.commit()
        db.refresh(existing)
        return existing
    
    # Crear nuevo registro
    device = DeviceFingerprint(
        user_id=user_id,
        fingerprint_hash=fingerprint_hash,
        user_agent=metadata.get("user_agent"),
        ip_address=ip_address or metadata.get("ip_address"),
        screen_resolution=metadata.get("screen_resolution"),
        timezone=metadata.get("timezone"),
        language=metadata.get("language"),
        platform=metadata.get("platform"),
        login_count=1
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    # Verificar trial abuse
    abuse_check = check_device_trial_abuse(db, fingerprint_hash)
    
    if abuse_check["is_abuse"]:
        log_abuse_event(
            db=db,
            event_type="multiple_accounts_same_device",
            severity="high" if abuse_check["should_block"] else "medium",
            user_id=user_id,
            fingerprint_hash=fingerprint_hash,
            ip_address=ip_address,
            description=f"Device has {abuse_check['free_accounts']} FREE accounts",
            event_metadata={  # ← CAMBIADO
                "device_count": abuse_check["device_count"],
                "free_accounts": abuse_check["free_accounts"],
                "users": abuse_check["users"]
            }
        )
    
    return device


def get_user_abuse_score(db: Session, user_id: int) -> dict:
    """
    Calcula un score de abuso para el usuario.
    Retorna dict con:
    - score: int (0-100, donde 100 es muy sospechoso)
    - flags: list[str] (razones del score)
    """
    flags = []
    score = 0
    
    # 1. Verificar eventos de abuso registrados
    abuse_events = db.query(AbuseEvent).filter(
        AbuseEvent.user_id == user_id
    ).count()
    
    if abuse_events > 0:
        score += min(abuse_events * 15, 50)
        flags.append(f"{abuse_events} abuse events logged")
    
    # 2. Verificar múltiples dispositivos
    devices = db.query(DeviceFingerprint).filter(
        DeviceFingerprint.user_id == user_id
    ).count()
    
    if devices > 3:
        score += 20
        flags.append(f"{devices} devices registered")
    
    # 3. Verificar cambios frecuentes de IP
    unique_ips = db.query(DeviceFingerprint.ip_address).filter(
        DeviceFingerprint.user_id == user_id,
        DeviceFingerprint.ip_address.isnot(None)
    ).distinct().count()
    
    if unique_ips > 5:
        score += 15
        flags.append(f"{unique_ips} different IP addresses")
    
    return {
        "score": min(score, 100),
        "flags": flags,
        "risk_level": "low" if score < 30 else "medium" if score < 60 else "high"
    }