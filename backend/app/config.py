from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_MAX: int = 10
    RATE_LIMIT_LOGIN_WINDOW_SEC: int = 300  # 5 minutos
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Email SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    
    # Google Play Billing
    GOOGLE_PLAY_SERVICE_ACCOUNT_JSON: str = ""
    GOOGLE_PLAY_PACKAGE_NAME: str = ""
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte CORS_ORIGINS string a lista."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"


settings = Settings()