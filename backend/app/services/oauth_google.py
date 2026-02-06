"""
Servicio de autenticación OAuth con Google.
Verifica tokens ID de Google y gestiona usuarios.
"""

from typing import Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import requests

from ..config import settings
from ..models.user import User
from ..models.user_identity import UserIdentity
from ..services.plan_service import assign_free_plan_to_new_user
from ..utils.security import create_access_token


def verify_google_token(token: str) -> Optional[Dict]:
    """
    Verifica un token ID de Google.
    Retorna dict con info del usuario si es válido, None si no.
    
    Usa el endpoint de Google: https://oauth2.googleapis.com/tokeninfo
    """
    try:
        response = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': token},
            timeout=5
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Verificar que el token pertenece a nuestra app
        if settings.GOOGLE_CLIENT_ID and data.get('aud') != settings.GOOGLE_CLIENT_ID:
            return None
        
        # Verificar que el email está verificado
        if not data.get('email_verified'):
            return None
        
        return {
            'provider_user_id': data.get('sub'),
            'email': data.get('email'),
            'name': data.get('name'),
            'picture': data.get('picture'),
            'email_verified': data.get('email_verified', False)
        }
    
    except Exception as e:
        print(f"Error verifying Google token: {e}")
        return None


def google_oauth_login(db: Session, id_token: str) -> Dict:
    """
    Procesa login OAuth con Google.
    
    Flujo:
    1. Verifica el token con Google
    2. Busca si ya existe UserIdentity con ese provider_user_id
    3. Si existe → login
    4. Si no existe pero email coincide → vincular a cuenta existente
    5. Si no existe → crear usuario nuevo
    
    Retorna dict con:
    - access_token: JWT de nuestra app
    - user: info del usuario
    - is_new_user: bool
    """
    # Verificar token con Google
    google_user = verify_google_token(id_token)
    
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message": "Invalid Google token"
            }
        )
    
    provider_user_id = google_user['provider_user_id']
    email = google_user['email']
    
    # Caso 1: Ya existe identity → login directo
    identity = db.query(UserIdentity).filter(
        UserIdentity.provider == "google",
        UserIdentity.provider_user_id == provider_user_id
    ).first()
    
    if identity:
        # Actualizar last_login
        from datetime import datetime
        identity.last_login = datetime.utcnow()
        db.commit()
        
        # Generar JWT
        access_token = create_access_token(data={"sub": identity.user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": identity.user.id,
                "email": identity.user.email,
                "email_verified": identity.user.email_verified
            },
            "is_new_user": False
        }
    
    # Caso 2: No existe identity, pero el email coincide → vincular
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        # Crear identity vinculada
        new_identity = UserIdentity(
            user_id=existing_user.id,
            provider="google",
            provider_user_id=provider_user_id,
            provider_email=email,
            provider_name=google_user.get('name'),
            provider_picture=google_user.get('picture')
        )
        
        # Marcar email como verificado (Google ya lo verificó)
        existing_user.email_verified = True
        
        db.add(new_identity)
        db.commit()
        
        # Generar JWT
        access_token = create_access_token(data={"sub": existing_user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": existing_user.id,
                "email": existing_user.email,
                "email_verified": existing_user.email_verified
            },
            "is_new_user": False,
            "linked": True
        }
    
    # Caso 3: No existe → crear usuario nuevo
    from datetime import datetime
    
    new_user = User(
        email=email,
        hashed_password="",  # No tiene password (solo OAuth)
        email_verified=True,  # Google ya verificó el email
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.flush()  # Para obtener el ID
    
    # Crear identity
    new_identity = UserIdentity(
        user_id=new_user.id,
        provider="google",
        provider_user_id=provider_user_id,
        provider_email=email,
        provider_name=google_user.get('name'),
        provider_picture=google_user.get('picture')
    )
    
    db.add(new_identity)
    
    # Asignar plan FREE
    assign_free_plan_to_new_user(db, new_user.id)
    
    db.commit()
    db.refresh(new_user)
    
    # Generar JWT
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "email_verified": new_user.email_verified
        },
        "is_new_user": True
    }