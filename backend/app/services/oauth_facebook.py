"""
Servicio de autenticación OAuth con Facebook.
Verifica access tokens de Facebook y gestiona usuarios.
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


def verify_facebook_token(access_token: str) -> Optional[Dict]:
    """
    Verifica un access token de Facebook.
    Retorna dict con info del usuario si es válido, None si no.
    
    Usa el Facebook Graph API: https://graph.facebook.com/me
    """
    try:
        # Obtener info del usuario
        response = requests.get(
            'https://graph.facebook.com/me',
            params={
                'access_token': access_token,
                'fields': 'id,email,name,picture'
            },
            timeout=5
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Verificar que tiene email
        if not data.get('email'):
            return None
        
        # Validar token contra app_id (si está configurado)
        if settings.FACEBOOK_APP_ID:
            debug_response = requests.get(
                'https://graph.facebook.com/debug_token',
                params={
                    'input_token': access_token,
                    'access_token': f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
                },
                timeout=5
            )
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json().get('data', {})
                if not debug_data.get('is_valid'):
                    return None
                if debug_data.get('app_id') != settings.FACEBOOK_APP_ID:
                    return None
        
        return {
            'provider_user_id': data.get('id'),
            'email': data.get('email'),
            'name': data.get('name'),
            'picture': data.get('picture', {}).get('data', {}).get('url'),
            'email_verified': True  # Facebook solo retorna emails verificados
        }
    
    except Exception as e:
        print(f"Error verifying Facebook token: {e}")
        return None


def facebook_oauth_login(db: Session, access_token: str) -> Dict:
    """
    Procesa login OAuth con Facebook.
    
    Flujo idéntico a Google:
    1. Verifica el token con Facebook
    2. Busca si ya existe UserIdentity con ese provider_user_id
    3. Si existe → login
    4. Si no existe pero email coincide → vincular a cuenta existente
    5. Si no existe → crear usuario nuevo
    
    Retorna dict con:
    - access_token: JWT de nuestra app
    - user: info del usuario
    - is_new_user: bool
    """
    # Verificar token con Facebook
    facebook_user = verify_facebook_token(access_token)
    
    if not facebook_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message": "Invalid Facebook token"
            }
        )
    
    provider_user_id = facebook_user['provider_user_id']
    email = facebook_user['email']
    
    # Caso 1: Ya existe identity → login directo
    identity = db.query(UserIdentity).filter(
        UserIdentity.provider == "facebook",
        UserIdentity.provider_user_id == provider_user_id
    ).first()
    
    if identity:
        # Actualizar last_login
        from datetime import datetime
        identity.last_login = datetime.utcnow()
        db.commit()
        
        # Generar JWT
        access_token_jwt = create_access_token(data={"sub": identity.user.email})
        
        return {
            "access_token": access_token_jwt,
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
            provider="facebook",
            provider_user_id=provider_user_id,
            provider_email=email,
            provider_name=facebook_user.get('name'),
            provider_picture=facebook_user.get('picture')
        )
        
        # Marcar email como verificado (Facebook ya lo verificó)
        existing_user.email_verified = True
        
        db.add(new_identity)
        db.commit()
        
        # Generar JWT
        access_token_jwt = create_access_token(data={"sub": existing_user.email})
        
        return {
            "access_token": access_token_jwt,
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
        email_verified=True,  # Facebook ya verificó el email
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.flush()  # Para obtener el ID
    
    # Crear identity
    new_identity = UserIdentity(
        user_id=new_user.id,
        provider="facebook",
        provider_user_id=provider_user_id,
        provider_email=email,
        provider_name=facebook_user.get('name'),
        provider_picture=facebook_user.get('picture')
    )
    
    db.add(new_identity)
    
    # Asignar plan FREE
    assign_free_plan_to_new_user(db, new_user.id)
    
    db.commit()
    db.refresh(new_user)
    
    # Generar JWT
    access_token_jwt = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token_jwt,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "email_verified": new_user.email_verified
        },
        "is_new_user": True
    }