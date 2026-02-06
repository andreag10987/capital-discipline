from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..schemas.auth import UserRegister, Token
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..utils.messages import get_message
from ..services.email_service import send_verification_email

def register_user(db: Session, user_data: UserRegister, lang: str = "en") -> Token:
    try:
        password_bytes = user_data.password.encode('utf-8')
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message("password_too_long", lang)
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("password_too_long", lang)
        )
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_message("email_exists", lang)
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    send_verification_email(db, new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return Token(access_token=access_token)

def login_user(db: Session, email: str, password: str, lang: str = "en") -> Token:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("invalid_credentials", lang)
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)