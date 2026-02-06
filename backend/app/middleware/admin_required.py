"""
Middleware para proteger rutas de administrador.
Solo usuarios con is_admin=True pueden acceder.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..api.deps import get_current_user


def require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que verifica si el usuario es administrador.
    Lanza 403 si no lo es.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "admin_required",
                "message": "Administrator privileges required"
            }
        )
    
    return current_user


def check_admin_or_self(
    target_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica si el usuario es admin O está accediendo a sus propios datos.
    Útil para endpoints donde users pueden ver su propia info pero admins pueden ver cualquiera.
    """
    if not current_user.is_admin and current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "unauthorized_access",
                "message": "You can only access your own data"
            }
        )
    
    return current_user