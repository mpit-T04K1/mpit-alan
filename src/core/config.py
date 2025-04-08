import os
from typing import List, Optional

from pydantic import HttpUrl, PostgresDsn, AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения
    """
    # Основные настройки
    APP_NAME: str = "QwertyTown Business Module"
    DEBUG: bool = False
    SECRET_KEY: str
    API_PREFIX: str = "/api"
    ADMIN_PATH: str = "/admin"
    ENVIRONMENT: str = "production"  # Возможные значения: "development", "test", "production"
    
    # Версионирование API
    API_V1_STR: str = "/v1"
    
    # CORS настройки (в продакшене заменить на конкретные домены)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Настройки базы данных
    DATABASE_URL: PostgresDsn
    
    # Настройки JWT
    JWT_SECRET_KEY: str
    JWT_TOKEN_LIFETIME: int = 60  # минуты
    JWT_ALGORITHM: str = "HS256"
    
    # Настройки S3 для хранения файлов
    S3_ENDPOINT: Optional[HttpUrl] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    
    # Настройки Telegram (опционально)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[HttpUrl] = None
    TELEGRAM_WEBHOOK_API_KEY: Optional[str] = None  # API ключ для защиты вебхука
    
    # Настройки тестирования
    TESTING: bool = False
    
    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # Настройки статических файлов
    STATIC_DIR: str = "static"
    TEMPLATES_DIR: str = "templates"
    
    # Настройки безопасности
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECURE_COOKIES: bool = False  # Установить в True для production с HTTPS
    
    # Настройки хеширования
    PWD_HASH_ITERATIONS: int = 100000
    
    # Настройки для Pydantic: загрузка из .env файла
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Создаем глобальный экземпляр настроек для импорта в других модулях
settings = Settings() 