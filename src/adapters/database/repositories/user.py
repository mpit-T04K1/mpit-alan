from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.models.user import User
from src.adapters.database.repositories.base import BaseRepository
from src.utils.exceptions import UserAlreadyExists, InvalidCredentials
from src.utils.security import verify_password


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Получить пользователя по телефону"""
        query = select(User).where(User.phone == phone)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def authenticate(self, email: str, password: str) -> User:
        """Аутентифицировать пользователя"""
        user = await self.get_by_email(email)
        if not user:
            raise InvalidCredentials("User not found")
        
        if not verify_password(password, user.password_hash):
            raise InvalidCredentials("Invalid password")
        
        # Обновляем время последнего входа
        user.last_login = datetime.utcnow()
        self.session.add(user)
        
        return user

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Создать нового пользователя"""
        # Проверяем, что пользователя с таким email еще нет
        existing_user = await self.get_by_email(user_data["email"])
        if existing_user:
            raise UserAlreadyExists("User with this email already exists")
        
        # Если указан телефон, проверяем его тоже
        if "phone" in user_data and user_data["phone"]:
            existing_user = await self.get_by_phone(user_data["phone"])
            if existing_user:
                raise UserAlreadyExists("User with this phone already exists")
        
        # Создаем пользователя
        user = await self.create(user_data)
        return user

    async def get_users_by_role(self, role: str) -> List[User]:
        """Получить пользователей по роли"""
        query = select(User).where(User.role == role)
        result = await self.session.execute(query)
        return list(result.scalars()) 