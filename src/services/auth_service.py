"""
Сервис аутентификации пользователей
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Union, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.core.config import settings
from src.repositories.user import UserRepository
from src.schemas.user import TokenData, UserResponse


# Oauth2 схема для получения токена из заголовка
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создать JWT-токен доступа
    
    Args:
        data: Данные для добавления в токен
        expires_delta: Время жизни токена
        
    Returns:
        Закодированный JWT-токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(settings.JWT_SECRET_KEY), algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def verify_token(token: str, db: AsyncSession) -> UserResponse:
    """
    Проверить JWT-токен и получить пользователя
    
    Args:
        token: JWT-токен
        db: Сессия базы данных
        
    Returns:
        Объект пользователя
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(token_data.user_id))
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Получить текущего пользователя по токену
    
    Args:
        token: JWT-токен
        db: Сессия базы данных
        
    Returns:
        Объект пользователя
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невозможно проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            str(settings.JWT_SECRET_KEY), 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(username)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_business_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Получить текущего активного бизнес-пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Объект пользователя
        
    Raises:
        HTTPException: Если пользователь не является бизнес-пользователем
    """
    if current_user.role not in ["business", "admin", "owner", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется бизнес-аккаунт"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Получить текущего активного администратора
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Объект пользователя
        
    Raises:
        HTTPException: Если пользователь не является администратором
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется аккаунт администратора"
        )
    
    return current_user 