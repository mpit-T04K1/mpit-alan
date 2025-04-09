from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Union[str, Any] = None, data: dict = None, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создать JWT-токен доступа
    
    Args:
        subject: Субъект токена (обычно user_id или email)
        data: Данные для добавления в токен (словарь с 'sub' и другими полями)
        expires_delta: Время жизни токена
        
    Returns:
        Строка JWT-токена
    """
    if data is not None:
        # Если передан словарь data, используем его
        to_encode = data.copy()
    else:
        # Иначе создаем словарь с subject
        to_encode = {"sub": str(subject)}
    
    # Добавляем время истечения
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_LIFETIME)
    
    to_encode.update({"exp": expire})
    
    # Кодируем JWT
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить соответствие открытого пароля хешированному
    
    Args:
        plain_password: Открытый пароль
        hashed_password: Хешированный пароль
        
    Returns:
        True если пароли совпадают, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Получить хеш пароля
    
    Args:
        password: Открытый пароль
        
    Returns:
        Хешированный пароль
    """
    return pwd_context.hash(password) 