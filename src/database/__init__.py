"""
Пакет-обертка для импорта компонентов базы данных из адаптера.
"""
from src.db_adapter import (
    Base, 
    get_db, 
    check_db_connection, 
    engine, 
    async_session_factory,
    async_session_maker
)

__all__ = [
    "Base", 
    "get_db", 
    "check_db_connection", 
    "engine", 
    "async_session_factory",
    "async_session_maker"
]

# Прямой доступ к компонентам из основного модуля
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
import asyncio
from typing import AsyncGenerator

# Повторно создаем базовый класс для моделей
Base = declarative_base()

# Функция get_db, которая будет обращаться к основной функции
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает сессию базы данных"""
    # Импортируем здесь, чтобы избежать циклических импортов
    from src.database import async_session_factory
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Проверка соединения
async def check_db_connection() -> bool:
    """Проверка соединения с базой данных"""
    try:
        # Импортируем здесь, чтобы избежать циклических импортов
        from src.database import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

# Переименовываем модуль, чтобы избежать конфликтов
import sys
sys.modules["src.database.core"] = sys.modules["src.database"]

# Все компоненты будут доступны из основного модуля через патчер 