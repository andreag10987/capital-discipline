from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..utils.security import decode_access_token
from ..config import settings

security = HTTPBearer()


def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extrae el JWT del header Authorization, lo decodifica y retorna el usuario.
    Si ADMIN_BYPASS_PAYMENT=true y el email coincide con ADMIN_EMAIL,
    marca al usuario como admin (en runtime) para habilitar rutas admin.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # ── Admin por variable de entorno (sin tocar DB) ─────────────
    if settings.ADMIN_BYPASS_PAYMENT and settings.ADMIN_EMAIL:
        if user.email and user.email.lower() == settings.ADMIN_EMAIL.lower():
            user.is_admin = True

    return user
