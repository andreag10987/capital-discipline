"""
Servicio de envío de emails.
Configuración SMTP desde .env
"""

import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..config import settings
from ..models.user import User


def generate_verification_token() -> str:
    """Genera token aleatorio de 32 caracteres."""
    return secrets.token_urlsafe(32)


def create_verification_link(token: str) -> str:
    """Crea el link de verificación."""
    return f"{settings.FRONTEND_URL}/verify-email?token={token}"


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Envía un email usando SMTP.
    Retorna True si se envió correctamente, False si falló.
    
    NOTA: Si SMTP_HOST está vacío, solo loguea el email (modo desarrollo).
    """
    # Modo desarrollo: solo loguear
    if not settings.SMTP_HOST:
        print(f"\n{'='*60}")
        print(f"[EMAIL - DEV MODE]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{html_body}")
        print(f"{'='*60}\n")
        return True
    
    # Modo producción: enviar email real
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
        
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_verification_email(db: Session, user: User) -> bool:
    """
    Genera token de verificación y envía email al usuario.
    """
    # Generar token
    token = generate_verification_token()
    verification_link = create_verification_link(token)
    
    # Actualizar usuario
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.utcnow()
    db.commit()
    
    # Construir email
    subject = "Verify your email - Capital Manager"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
            <h1 style="color: white; margin: 0;">Capital Manager</h1>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9; border-radius: 10px; margin-top: 20px;">
            <h2 style="color: #333;">Verify Your Email</h2>
            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                Thank you for registering! Please click the button below to verify your email address.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 15px 40px; 
                          text-decoration: none; 
                          border-radius: 8px; 
                          display: inline-block;
                          font-weight: bold;">
                    Verify Email
                </a>
            </div>
            
            <p style="color: #888; font-size: 14px;">
                Or copy this link: <br>
                <a href="{verification_link}" style="color: #667eea;">{verification_link}</a>
            </p>
            
            <p style="color: #888; font-size: 14px; margin-top: 30px;">
                This link will expire in 24 hours.
            </p>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
            <p>If you didn't create an account, you can safely ignore this email.</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, html_body)


def verify_email_token(db: Session, token: str) -> Optional[User]:
    """
    Verifica el token de email.
    Retorna el usuario si el token es válido, None si no.
    """
    user = db.query(User).filter(User.email_verification_token == token).first()
    
    if not user:
        return None
    
    # Verificar que no haya expirado (24 horas)
    if user.email_verification_sent_at:
        expiry = user.email_verification_sent_at + timedelta(hours=24)
        if datetime.utcnow() > expiry:
            return None
    
    # Marcar como verificado
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_sent_at = None
    db.commit()
    
    return user