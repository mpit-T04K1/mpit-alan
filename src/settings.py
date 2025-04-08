import os
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Базовые настройки приложения
    APP_NAME: str = "QwertyTown Business Module"
    DEBUG: bool = False
    SECRET_KEY: SecretStr = Field(default=...)
    API_PREFIX: str = "/api"
    ADMIN_PATH: str = "/admin"
    
    # Настройки базы данных
    DATABASE_URL: str
    
    # Настройки JWT токенов
    JWT_SECRET_KEY: SecretStr = Field(default=...)
    JWT_TOKEN_LIFETIME: int = 60  # минуты
    JWT_ALGORITHM: str = "HS256"
    
    # S3 настройки
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[SecretStr] = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str = "qwertytown"
    
    # Пути к директориям
    BASE_DIR: Path = Path(__file__).parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    # Настройки Telegram
    TELEGRAM_BOT_TOKEN: Optional[SecretStr] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings() 