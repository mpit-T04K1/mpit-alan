#!/usr/bin/env python3

# Скрипт, который создаст простой файл auth.py для доступа к админке

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schemas.user import UserResponse

# Настройка логгера
logger = logging.getLogger(__name__)

# Маршрутизатор
router = APIRouter(tags=["Аутентификация"])

# Схема OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

async def get_current_user_optional(
    request: Request = None,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserResponse]:
    """
    Тестовая функция для доступа к админке без реальной аутентификации
    """
    # Всегда возвращаем тестового админа
    test_user = UserResponse(
        id=9999,
        email="admin@example.com",
        first_name="Test",
        last_name="Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat()
    )
    logger.info(f"Используется тестовый пользователь: {test_user.email}")
    return test_user

# Остальные функции аутентификации могут быть заглушками
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    return await get_current_user_optional(request, token, db)

async def get_current_active_business_user(request: Request, current_user: UserResponse = Depends(get_current_user)):
    return current_user

async def get_current_moderation_user(request: Request, current_user: UserResponse = Depends(get_current_user)):
    return current_user

async def get_current_admin_user(request: Request, current_user: UserResponse = Depends(get_current_user)):
    return current_user 