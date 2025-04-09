from datetime import datetime, timedelta
from typing import Dict, Optional, Union

import jwt
from passlib.context import CryptContext

from src.settings import settings

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


# Алиас для совместимости с разными частями приложения
get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Union[str, int]], expires_delta: Optional[timedelta] = None
) -> str:
    """Создание JWT токена доступа"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_LIFETIME)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY.get_secret_value(), 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Union[str, int]]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        raise ValueError("Invalid token") 