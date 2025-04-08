import logging
from sqlalchemy import text

from .session import engine

logger = logging.getLogger(__name__)


async def check_db_connection() -> bool:
    """Проверка соединения с базой данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке соединения с БД: {e}")
        return False
