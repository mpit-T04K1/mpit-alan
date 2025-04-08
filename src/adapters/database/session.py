from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.settings import settings


logger = logging.getLogger(__name__)


engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных.
    Используется в FastAPI ручках.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()





