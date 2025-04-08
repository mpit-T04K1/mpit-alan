from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import os

# Создаем базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/qwertytown")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
TESTING = os.environ.get("TESTING", "false").lower() == "true"

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    future=True,
    # В продакшене отключать пулинг не рекомендуется, это для примера
    poolclass=NullPool if TESTING else None
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