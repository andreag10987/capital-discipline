from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ============================================================
    # BASE DE DATOS
    # ============================================================

    # Cadena de conexión a la DB (PostgreSQL, etc.)
    DATABASE_URL: str

    # ============================================================
    # JWT / AUTENTICACIÓN
    # ============================================================

    # Clave secreta para firmar JWT (obligatoria)
    SECRET_KEY: str

    # Algoritmo de firma de JWT
    ALGORITHM: str = "HS256"

    # Expiración del token en minutos (10080 = 7 días)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # ============================================================
    # RATE LIMITING (PROTECCIÓN CONTRA FUERZA BRUTA)
    # ============================================================

    # Máximo de intentos de login en la ventana de tiempo
    RATE_LIMIT_LOGIN_MAX: int = 10

    # Ventana de tiempo (segundos) para el rate limit (300 = 5 min)
    RATE_LIMIT_LOGIN_WINDOW_SEC: int = 300

    # ============================================================
    # CORS (DOMINIOS PERMITIDOS PARA ACCEDER AL BACKEND)
    # ============================================================

    # Orígenes permitidos separados por coma
    # En producción debes poner tu dominio de Vercel
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte CORS_ORIGINS (string separado por comas) en una lista."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ============================================================
    # EMAIL SMTP (OPCIONAL)
    # ============================================================

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    # ============================================================
    # FRONTEND
    # ============================================================

    # URL del frontend (útil para redirects en OAuth, enlaces, etc.)
    FRONTEND_URL: str = "http://localhost:5173"

    # ============================================================
    # OAUTH (GOOGLE / FACEBOOK)
    # ============================================================

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""

    # ============================================================
    # GOOGLE PLAY BILLING (SI APLICA)
    # ============================================================

    GOOGLE_PLAY_SERVICE_ACCOUNT_JSON: str = ""
    GOOGLE_PLAY_PACKAGE_NAME: str = ""

    # ============================================================
    # ADMIN / BYPASS DE PAGO (PARA PRUEBAS INTERNAS)
    # ============================================================

    # Correo del superusuario. Si el usuario logueado tiene este email
    # y ADMIN_BYPASS_PAYMENT está en true, se le dará acceso total.
    ADMIN_EMAIL: str = ""

    # Activa/desactiva el bypass de pago para ese ADMIN_EMAIL
    # IMPORTANTE: déjalo en false en producción real.
    ADMIN_BYPASS_PAYMENT: bool = False

    # ============================================================
    # CONFIG Pydantic Settings
    # ============================================================

    class Config:
        # Archivo .env para desarrollo local
        env_file = ".env"


# Instancia global de configuración
settings = Settings()
