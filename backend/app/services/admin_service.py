"""
Servicio de administración.
Lógica de negocio para gestión de usuarios, métricas, etc.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from typing import List, Optional

from ..models.user import User
from ..models.subscription import Subscription
from ..models.plan import Plan
from ..models.device_fingerprint import DeviceFingerprint
from ..models.abuse_event import AbuseEvent
from ..services.abuse_detection import get_user_abuse_score
from ..services.plan_service import create_subscription, cancel_subscription


def get_users_list(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    plan_filter: Optional[str] = None,
    is_blocked: Optional[bool] = None
) -> dict:
    """
    Obtiene lista de usuarios con filtros.
    Retorna dict con users y total count.
    """
    query = db.query(User)
    
    # Filtro por plan
    if plan_filter:
        query = query.join(Subscription).join(Plan).filter(
            Subscription.status == "ACTIVE",
            Plan.name == plan_filter
        )
    
    # Filtro por blocked
    if is_blocked is not None:
        query = query.filter(User.is_blocked == is_blocked)
    
    # Count total
    total = query.count()
    
    # Paginación
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # Enriquecer con datos adicionales
    users_data = []
    for user in users:
        # Obtener plan actual
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "ACTIVE"
        ).order_by(Subscription.created_at.desc()).first()
        
        plan_name = subscription.plan.name if subscription else "FREE"
        
        # Contar dispositivos
        device_count = db.query(DeviceFingerprint).filter(
            DeviceFingerprint.user_id == user.id
        ).count()
        
        # Contar eventos de abuso
        abuse_count = db.query(AbuseEvent).filter(
            AbuseEvent.user_id == user.id
        ).count()
        
        users_data.append({
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_blocked": user.is_blocked,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "plan": plan_name,
            "device_count": device_count,
            "abuse_events": abuse_count
        })
    
    return {
        "users": users_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


def get_user_detail(db: Session, user_id: int) -> dict:
    """
    Obtiene detalles completos de un usuario.
    Incluye: plan, dispositivos, abuse score, métricas.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Plan actual
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "ACTIVE"
    ).order_by(Subscription.created_at.desc()).first()
    
    plan_info = None
    if subscription:
        plan_info = {
            "id": subscription.plan.id,
            "name": subscription.plan.name,
            "display_name": subscription.plan.display_name_en,
            "price_usd": subscription.plan.price_usd,
            "started_at": subscription.start_date
        }
    
    # Dispositivos
    devices = db.query(DeviceFingerprint).filter(
        DeviceFingerprint.user_id == user.id
    ).order_by(DeviceFingerprint.last_seen.desc()).all()
    
    devices_data = [
        {
            "id": d.id,
            "fingerprint_hash": d.fingerprint_hash[:16] + "...",
            "platform": d.platform,
            "first_seen": d.first_seen,
            "last_seen": d.last_seen,
            "login_count": d.login_count
        }
        for d in devices
    ]
    
    # Eventos de abuso
    abuse_events = db.query(AbuseEvent).filter(
        AbuseEvent.user_id == user.id
    ).order_by(AbuseEvent.created_at.desc()).limit(10).all()
    
    abuse_data = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "severity": e.severity,
            "description": e.description,
            "created_at": e.created_at
        }
        for e in abuse_events
    ]
    
    # Abuse score
    abuse_score = get_user_abuse_score(db, user.id)
    
    # Identidades OAuth
    oauth_identities = []
    for identity in user.oauth_identities:
        oauth_identities.append({
            "provider": identity.provider,
            "provider_email": identity.provider_email,
            "created_at": identity.created_at,
            "last_login": identity.last_login
        })
    
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_blocked": user.is_blocked,
        "blocked_reason": user.blocked_reason,
        "blocked_at": user.blocked_at,
        "email_verified": user.email_verified,
        "created_at": user.created_at,
        "plan": plan_info,
        "devices": devices_data,
        "abuse_events": abuse_data,
        "abuse_score": abuse_score,
        "oauth_identities": oauth_identities
    }


def block_user(db: Session, user_id: int, reason: str) -> bool:
    """Bloquea un usuario."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    user.is_blocked = True
    user.blocked_reason = reason
    user.blocked_at = datetime.utcnow()
    
    db.commit()
    
    # Registrar evento
    from ..services.abuse_detection import log_abuse_event
    log_abuse_event(
        db=db,
        event_type="user_blocked",
        severity="high",
        user_id=user_id,
        description=f"User blocked by admin. Reason: {reason}"
    )
    
    return True


def unblock_user(db: Session, user_id: int) -> bool:
    """Desbloquea un usuario."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    user.is_blocked = False
    user.blocked_reason = None
    user.blocked_at = None
    
    db.commit()
    
    return True


def change_user_plan(db: Session, user_id: int, plan_name: str) -> dict:
    """Cambia el plan de un usuario manualmente."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Cancelar suscripción actual
    cancel_subscription(db, user_id)
    
    # Crear nueva suscripción
    subscription = create_subscription(
        db=db,
        user_id=user_id,
        plan_name=plan_name,
        payment_provider="manual_admin"
    )
    
    return {
        "user_id": user_id,
        "new_plan": subscription.plan.name,
        "changed_at": datetime.utcnow()
    }


def get_system_metrics(db: Session) -> dict:
    """
    Obtiene métricas generales del sistema.
    """
    # Total usuarios
    total_users = db.query(User).count()
    
    # Usuarios por plan
    users_by_plan = db.query(
        Plan.name,
        func.count(distinct(Subscription.user_id))
    ).join(Subscription).filter(
        Subscription.status == "ACTIVE"
    ).group_by(Plan.name).all()
    
    plan_distribution = {plan: count for plan, count in users_by_plan}
    
    # Usuarios activos (últimos 7 días)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(distinct(DeviceFingerprint.user_id))).filter(
        DeviceFingerprint.last_seen >= week_ago
    ).scalar()
    
    # Usuarios bloqueados
    blocked_users = db.query(User).filter(User.is_blocked == True).count()
    
    # Eventos de abuso (últimos 30 días)
    month_ago = datetime.utcnow() - timedelta(days=30)
    abuse_events = db.query(AbuseEvent).filter(
        AbuseEvent.created_at >= month_ago
    ).count()
    
    # Eventos de abuso por severidad
    abuse_by_severity = db.query(
        AbuseEvent.severity,
        func.count(AbuseEvent.id)
    ).filter(
        AbuseEvent.created_at >= month_ago
    ).group_by(AbuseEvent.severity).all()
    
    severity_distribution = {sev: count for sev, count in abuse_by_severity}
    
    # Nuevos usuarios (últimos 30 días)
    new_users = db.query(User).filter(
        User.created_at >= month_ago
    ).count()
    
    # Tasa de conversión (FREE a PAID)
    total_free = plan_distribution.get("FREE", 0)
    total_paid = sum(plan_distribution.get(p, 0) for p in ["BASIC", "PRO"])
    conversion_rate = (total_paid / total_users * 100) if total_users > 0 else 0
    
    return {
        "total_users": total_users,
        "active_users_7d": active_users or 0,
        "blocked_users": blocked_users,
        "new_users_30d": new_users,
        "plan_distribution": plan_distribution,
        "conversion_rate": round(conversion_rate, 2),
        "abuse_events_30d": abuse_events,
        "abuse_by_severity": severity_distribution
    }