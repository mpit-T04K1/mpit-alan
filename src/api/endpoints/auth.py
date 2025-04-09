"""
Эндпоинты для аутентификации и управления пользователями
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.db_adapter import get_db
from src.services.auth_service import create_access_token
from src.models.user import UserRole
from src.repositories.user import UserRepository
from src.schemas.user import (
    UserCreate, 
    UserResponse, 
    UserUpdate, 
    Token, 
    LoginRequest,
    PasswordChange
)
from src.utils.security import verify_password, get_password_hash
from src.core.config import settings

# Настройка логгера
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    Args:
        user_data: Данные нового пользователя
        db: Сессия базы данных
        
    Returns:
        Данные созданного пользователя
    """
    return await register_user(user_data, db)


# Экспортируемая функция для использования в app.py
async def register_user(
    user: UserCreate,
    db: AsyncSession
) -> UserResponse:
    """
    Функция регистрации пользователя
    
    Args:
        user: Данные нового пользователя
        db: Сессия базы данных
        
    Returns:
        Данные созданного пользователя
    """
    try:
        logger.info(f"Попытка регистрации пользователя с email: {user.email}")
        
        # Проверяем, что пользователь с таким email не существует
        user_repo = UserRepository(db)
        existing_user = await user_repo.get_by_email(user.email)
        if existing_user:
            logger.warning(f"Пользователь с email {user.email} уже существует")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
        
        # Проверяем, что пользователь с таким телефоном не существует
        if user.phone:
            existing_phone = await user_repo.get_by_phone(user.phone)
            if existing_phone:
                logger.warning(f"Пользователь с телефоном {user.phone} уже существует")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким телефоном уже существует"
                )
        
        # Создаем пользователя
        user_dict = user.dict(exclude={"password_confirm", "is_active", "is_superuser"})
        user_dict["hashed_password"] = get_password_hash(user_dict["password"])
        user_dict.pop("password", None)
        
        # Обеспечиваем безопасность: обычные пользователи не могут регистрироваться как администраторы
        if user_dict.get("role") == UserRole.ADMIN:
            logger.warning(f"Попытка создания администратора через регистрацию: {user.email}")
            user_dict["role"] = "client"
        else:
            # Преобразуем UserRole в строковое значение, если роль передана как enum
            if "role" in user_dict and isinstance(user_dict["role"], UserRole):
                user_dict["role"] = user_dict["role"].value
            elif "role" in user_dict and isinstance(user_dict["role"], str):
                # Убеждаемся, что роль всегда в нижнем регистре
                user_dict["role"] = user_dict["role"].lower()
            else:
                # По умолчанию используем роль клиента
                user_dict["role"] = "client"
        
        logger.info(f"Создание пользователя с данными: {user_dict}")
        user = await user_repo.create(user_dict)
        logger.info(f"Пользователь успешно создан с ID: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {str(e)}")
        if "Multiple classes found for path" in str(e):
            logger.error(f"Ошибка связана с конфликтом моделей: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера при регистрации. Пожалуйста, свяжитесь с администратором."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации: {str(e)}"
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему
    
    Args:
        request: Запрос
        form_data: Данные для входа
        db: Сессия базы данных
        
    Returns:
        Токен доступа
    """
    try:
        logger.info(f"Попытка входа пользователя с username: {form_data.username}")
        logger.info(f"User-Agent: {request.headers.get('user-agent')}")
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(form_data.username)
        
        if not user:
            logger.warning(f"Пользователь с email {form_data.username} не найден")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Неверный пароль для пользователя: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Дополнительный лог для отладки роли пользователя
        logger.info(f"Пользователь {user.email} имеет роль: {user.role} (тип: {type(user.role)})")
        
        if not user.is_active:
            logger.warning(f"Попытка входа неактивного пользователя: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь неактивен"
            )
        
        # Создаем JWT токен
        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"Создан токен для пользователя {user.email}: {access_token[:15]}...")
        
        # Отладочный лог полного токена в тестовой среде
        if settings.ENVIRONMENT == "test" or settings.ENVIRONMENT == "development":
            logger.debug(f"ТЕСТОВОЕ ОКРУЖЕНИЕ: Полный токен: {access_token}")
        
        # Формируем ответ
        from fastapi.responses import JSONResponse
        response_data = {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_email": user.email,
            "user_role": user.role,
        }
        
        response = JSONResponse(content=response_data)
        
        # Устанавливаем cookie с токеном
        logger.info(f"Установка cookie access_token для пользователя {user.email}")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=60 * 60,  # 1 час
            path="/",         # Доступен для всего сайта
        )
        
        logger.info(f"Успешный вход пользователя: {user.email}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при входе пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при входе: {str(e)}"
        ) 