from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.db_adapter import Base
from src.utils.exceptions import ResultNotFound

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с основными CRUD операциями"""

    def __init__(self, session: AsyncSession, model_cls: Type[ModelType]):
        self.session = session
        self.model_cls = model_cls

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Создать запись в БД"""
        item = self.model_cls(**data)
        self.session.add(item)
        return item

    async def find_all(self, **kwargs) -> List[ModelType]:
        """Найти все записи по указанным параметрам"""
        query = self._build_query(**kwargs)
        result = await self.session.execute(query)
        return list(result.scalars())

    async def find_one(self, **kwargs) -> ModelType:
        """Найти одну запись по указанным параметрам"""
        query = self._build_query(**kwargs)
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()
        if item is None:
            raise ResultNotFound(f"{self.model_cls.__name__} not found")
        return item

    async def update(self, id: int, data: Dict[str, Any]) -> ModelType:
        """Обновить запись по ID"""
        query = update(self.model_cls).where(self.model_cls.id == id).values(**data)
        await self.session.execute(query)
        return await self.find_one(id=id)

    async def delete(self, id: int) -> None:
        """Удалить запись по ID"""
        query = delete(self.model_cls).where(self.model_cls.id == id)
        await self.session.execute(query)

    async def count(self, **kwargs) -> int:
        """Подсчитать количество записей по указанным параметрам"""
        query = self._build_count_query(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one()

    def _build_query(self, **kwargs) -> Select:
        """Построить запрос с фильтрами"""
        query = select(self.model_cls)
        
        for key, value in kwargs.items():
            if hasattr(self.model_cls, key):
                query = query.where(getattr(self.model_cls, key) == value)
        
        return query

    def _build_count_query(self, **kwargs) -> Select:
        """Построить запрос для подсчета записей с фильтрами"""
        query = select(func.count(self.model_cls.id))
        
        for key, value in kwargs.items():
            if hasattr(self.model_cls, key):
                query = query.where(getattr(self.model_cls, key) == value)
        
        return query 