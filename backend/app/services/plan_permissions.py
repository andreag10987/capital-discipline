"""
Middleware para validar permisos basados en el plan del usuario.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.plan import Plan
from ..api.deps import get_current_user
from ..services.plan_service import get_user_plan


class PlanPermission:
    """Dependencia reutilizable para verificar permisos del plan."""
    
    def __init__(self, required_feature: str, required_value=True):
        """
        Args:
            required_feature: Nombre del feature en plan.features (ej: 'can_export_pdf')
            required_value: Valor esperado (por defecto True)
        """
        self.required_feature = required_feature
        self.required_value = required_value
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Plan:
        """Verifica si el usuario tiene el permiso requerido."""
        plan = get_user_plan(db, current_user.id)
        
        feature_value = plan.get_feature(self.required_feature)
        
        if feature_value != self.required_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "plan_restriction",
                    "message": f"This feature requires a higher plan. Your current plan: {plan.name}",
                    "current_plan": plan.name,
                    "required_feature": self.required_feature
                }
            )
        
        return plan


class PlanLimit:
    """Dependencia para verificar límites numéricos del plan."""
    
    def __init__(self, limit_feature: str):
        """
        Args:
            limit_feature: Nombre del límite en plan.features (ej: 'max_daily_sessions')
        """
        self.limit_feature = limit_feature
    
    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> tuple[Plan, int]:
        """Retorna el plan y el límite numérico."""
        plan = get_user_plan(db, current_user.id)
        limit = plan.get_feature(self.limit_feature, 0)
        
        return plan, limit


# ── Dependencias preconstruidas para usar en routes ──────────────

# Permisos booleanos
require_pdf_export = PlanPermission("can_export_pdf", True)
require_excel_export = PlanPermission("can_export_excel", True)
require_projections = PlanPermission("can_see_projections", True)
require_withdrawal_recalc = PlanPermission("can_recalculate_withdrawals", True)

# Límites numéricos (retornan tupla: plan, límite)
get_session_limit = PlanLimit("max_daily_sessions")
get_operation_limit = PlanLimit("max_ops_per_session")
get_goal_limit = PlanLimit("max_active_goals")
get_history_limit = PlanLimit("history_days")