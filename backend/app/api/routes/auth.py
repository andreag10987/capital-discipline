from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.auth import (
    UserRegister, UserLogin, Token, 
    GoogleOAuthLogin, FacebookOAuthLogin, OAuthResponse
)
from ...services.auth_service import register_user, login_user
from ...services.email_service import verify_email_token
from ...services.oauth_google import google_oauth_login
from ...services.oauth_facebook import facebook_oauth_login
from ...middleware.rate_limit import check_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    accept_language: str = Header(default="en"),
    _rate: None = Depends(check_rate_limit),
):
    """Registra un nuevo usuario. Envía email de verificación automáticamente."""
    lang = "es" if "es" in accept_language.lower() else "en"
    return register_user(db, user_data, lang)


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
    accept_language: str = Header(default="en"),
    _rate: None = Depends(check_rate_limit),
):
    """Inicia sesión con email y password."""
    lang = "es" if "es" in accept_language.lower() else "en"
    return login_user(db, user_data.email, user_data.password, lang)


@router.get("/verify-email")
def verify_email(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Verifica el email del usuario mediante el token enviado por correo."""
    user = verify_email_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_token",
                "message": "Invalid or expired verification token"
            }
        )
    
    return {
        "message": "Email verified successfully",
        "email": user.email,
        "verified": True
    }


# ── OAuth Endpoints ────────────────────────────

@router.post("/google", response_model=OAuthResponse)
def google_login(
    oauth_data: GoogleOAuthLogin,
    db: Session = Depends(get_db),
    _rate: None = Depends(check_rate_limit),
):
    """
    Login con Google OAuth.
    
    El cliente envía el ID token obtenido de Google Sign-In.
    Retorna JWT de nuestra app si el token es válido.
    """
    return google_oauth_login(db, oauth_data.id_token)


@router.post("/facebook", response_model=OAuthResponse)
def facebook_login(
    oauth_data: FacebookOAuthLogin,
    db: Session = Depends(get_db),
    _rate: None = Depends(check_rate_limit),
):
    """
    Login con Facebook OAuth.
    
    El cliente envía el access token obtenido de Facebook Login.
    Retorna JWT de nuestra app si el token es válido.
    """
    return facebook_oauth_login(db, oauth_data.access_token)