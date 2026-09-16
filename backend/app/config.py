import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "ALLSTREAK"
    TAGLINE: str = "Automate. Engage. Convert."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # URLs
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Database (Default SQLite for instant local zero-dependency testing, Postgres in prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./allstreak.db"
    SYNC_DATABASE_URL: str = "sqlite:///./allstreak.db"
    
    # Redis / Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False  # Set to True when Redis is running
    
    # Security / JWT
    JWT_SECRET: str = "allstreak-super-secret-production-jwt-key-change-in-prod-2026"
    JWT_REFRESH_SECRET: str = "allstreak-super-secret-refresh-key-change-in-prod-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Meta WhatsApp Cloud API
    META_GRAPH_URL: str = "https://graph.facebook.com"
    META_API_VERSION: str = "v21.0"
    META_ACCESS_TOKEN: str = ""
    META_VERIFY_TOKEN: str = "allstreak_secure_verify_token_2026"
    META_APP_SECRET: str = ""
    META_PHONE_NUMBER_ID: str = ""
    META_WABA_ID: str = ""
    META_BUSINESS_ID: str = ""
    
    # WhatsApp Customer Service Window (hours)
    WHATSAPP_WINDOW_HOURS: int = 24
    
    # AI Engine
    OPENAI_API_KEY: str = ""
    AI_DEFAULT_MODEL: str = "gpt-4o-mini"
    
    # Demo Mode
    DEMO_MODE_ENABLED: bool = True

settings = Settings()
