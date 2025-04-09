"""
Файл-обертка для импорта компонентов базы данных из адаптера.
"""
from src.db_adapter import (
    Base, 
    get_db, 
    check_db_connection, 
    engine, 
    async_session_factory
)

__all__ = [
    "Base", 
    "get_db", 
    "check_db_connection", 
    "engine", 
    "async_session_factory"
]

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from src.core.config import settings

# Создаем базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Преобразуем URL из PostgresDsn в строку для SQLAlchemy
database_url = str(settings.DATABASE_URL)

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    future=True,
    # В продакшене отключать пулинг не рекомендуется, это для примера
    poolclass=NullPool if settings.TESTING else None
)

# Создаем фабрику асинхронных сессий
async_session_factory = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncSession:
    """
    Зависимость для получения сессии базы данных.
    Используется в ручках FastAPI для получения соединения с БД.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Проверяет подключение к базе данных.
    Используется для проверки здоровья приложения.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False 