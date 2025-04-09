from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
import sys
from pathlib import Path
from src.db_adapter import Base, get_db, check_db_connection, engine, async_session_factory

# Используем Base из основного модуля, чтобы было единое определение
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/qwertytown")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    future=True,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def check_db_connection():
    """Проверка соединения с базой данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False 