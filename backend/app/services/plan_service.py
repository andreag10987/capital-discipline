"""
Servicio para gestionar planes y suscripciones.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from ..models.plan import Plan
from ..models.subscription import Subscription
from ..models.user import User
from ..config import settings


def get_plan_by_name(db: Session, plan_name: str) -> Optional[Plan]:
    """Obtiene un plan por nombre (FREE, BASIC, PRO)."""
    return db.query(Plan).filter(Plan.name == plan_name, Plan.is_active == True).first()


def get_all_plans(db: Session) -> list[Plan]:
    """Obtiene todos los planes activos."""
    return db.query(Plan).filter(Plan.is_active == True).order_by(Plan.price_usd).all()


def get_user_active_subscription(db: Session, user_id: int) -> Optional[Subscription]:
    """Obtiene la suscripción activa del usuario."""
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "ACTIVE"
    ).order_by(Subscription.created_at.desc()).first()


def get_user_plan(db: Session, user_id: int) -> Plan:
    """
    Obtiene el plan actual del usuario.
    Si no tiene suscripción, retorna FREE por defecto.

    ADMIN BYPASS:
    - Si ADMIN_BYPASS_PAYMENT=true y el email del usuario coincide con ADMIN_EMAIL,
      retornamos un plan sintético con límites altos (sin depender de que exista PRO en DB).
    """

    # ── ADMIN BYPASS (plan sintético) ───────────────────────────
    if settings.ADMIN_BYPASS_PAYMENT and settings.ADMIN_EMAIL:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email and user.email.lower() == settings.ADMIN_EMAIL.lower():
            return Plan(
                name="ADMIN",
                display_name_es="Administrador",
                display_name_en="Administrator",
                price_usd=0.0,
                features={
                    # permisos
                    "can_export_pdf": True,
                    "can_export_excel": True,
                    "can_generate_projections": True,
                    "can_create_goals": True,
                    "can_withdraw": True,
                    "can_recalculate_withdrawals": True,
                    # límites
                    "max_daily_sessions": 999,
                    "max_ops_per_session": 9999,
                    "max_active_goals": 999,
                    "history_days": 365,
                },
                is_active=True,
            )
    # ───────────────────────────────────────────────────────────

    subscription = get_user_active_subscription(db, user_id)

    if subscription and subscription.is_active():
        return subscription.plan

    # Si no tiene suscripción activa, retornar FREE
    free_plan = get_plan_by_name(db, "FREE")
    if not free_plan:
        raise Exception("FREE plan not found in database")

    return free_plan


def create_subscription(
    db: Session,
    user_id: int,
    plan_name: str,
    payment_provider: Optional[str] = None,
    external_subscription_id: Optional[str] = None
) -> Subscription:
    """
    Crea una nueva suscripción para el usuario.
    Cancela la suscripción activa anterior si existe.
    """
    # Obtener el plan
    plan = get_plan_by_name(db, plan_name)
    if not plan:
        raise ValueError(f"Plan {plan_name} not found")
    
    # Cancelar suscripción activa anterior
    active_sub = get_user_active_subscription(db, user_id)
    if active_sub:
        active_sub.status = "CANCELED"
        active_sub.updated_at = datetime.utcnow()
    
    # Crear nueva suscripción
    new_subscription = Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status="ACTIVE",
        start_date=datetime.utcnow(),
        end_date=None,  # Sin límite de tiempo
        payment_provider=payment_provider,
        external_subscription_id=external_subscription_id
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    
    return new_subscription


def assign_free_plan_to_new_user(db: Session, user_id: int) -> Subscription:
    """
    Asigna el plan FREE a un usuario recién registrado.
    Llamar esto desde el registro de usuario.
    """
    return create_subscription(db, user_id, "FREE", payment_provider="manual")


def cancel_subscription(db: Session, user_id: int) -> bool:
    """
    Cancela la suscripción activa del usuario.
    Retorna True si se canceló, False si no había suscripción activa.
    """
    subscription = get_user_active_subscription(db, user_id)
    if not subscription:
        return False
    
    subscription.status = "CANCELED"
    subscription.updated_at = datetime.utcnow()
    db.commit()
    
    return True