from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str


# ── OAuth Schemas ──────────────────────────────

class GoogleOAuthLogin(BaseModel):
    """Schema para login con Google."""
    id_token: str = Field(..., description="Google ID token from client")


class FacebookOAuthLogin(BaseModel):
    """Schema para login con Facebook."""
    access_token: str = Field(..., description="Facebook access token from client")


class OAuthResponse(BaseModel):
    """Respuesta extendida para OAuth."""
    access_token: str
    token_type: str = "bearer"
    user: dict
    is_new_user: bool
    linked: Optional[bool] = False