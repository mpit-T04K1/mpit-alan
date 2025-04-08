"""
Единый модуль для работы с базой данных.
Этот модуль предоставляет общие компоненты для взаимодействия с базой данных
и импортируется другими модулями проекта.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from src.settings import settings

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # В продакшене обычно нужно убрать NullPool
    poolclass=NullPool if hasattr(settings, "TESTING") and settings.TESTING else None
)

# Создаем фабрику сессий
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Зависимость для получения сессии базы данных.
    Используется в FastAPI ручках.
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
    """Проверка соединения с базой данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False 