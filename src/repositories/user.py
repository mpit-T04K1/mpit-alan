"""
Репозиторий для работы с пользователями
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.models.user import User, UserRole


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Объект пользователя или None
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Объект пользователя или None
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """
        Получить пользователя по телефону
        
        Args:
            phone: Телефон пользователя
            
        Returns:
            Объект пользователя или None
        """
        query = select(User).where(User.phone == phone)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        """
        Создать нового пользователя
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            Объект созданного пользователя
        """
        # Если передана роль, убедимся, что она в правильном регистре (нижнем)
        if "role" in user_data:
            # Если роль - это строка в верхнем регистре, преобразуем её в нижний
            if isinstance(user_data["role"], str):
                user_data["role"] = user_data["role"].lower()
        
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """
        Обновить данные пользователя
        
        Args:
            user_id: ID пользователя
            user_data: Новые данные пользователя
            
        Returns:
            Объект обновленного пользователя или None
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Предварительная обработка ролей
        if "role" in user_data:
            # Если роль - это строка или enum, преобразуем их в строку нижнего регистра
            if isinstance(user_data["role"], str):
                user_data["role"] = user_data["role"].lower()
            elif hasattr(user_data["role"], "value"):
                # Если это enum с атрибутом value
                user_data["role"] = user_data["role"].value.lower()

        for key, value in user_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если пользователь удален, иначе False
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить список пользователей
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_role(self, role, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить пользователей по роли
        
        Args:
            role: Роль пользователя (строка или UserRole)
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей с указанной ролью
        """
        # Преобразуем роль в нижний регистр, если это строка
        if isinstance(role, str):
            role = role.lower()
            
        query = select(User).where(User.role == role).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all() 