from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Header, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from typing import Optional, Any
import logging

from src.db.database import get_db
from src.core.config import settings
from src.core.security import create_access_token, verify_password
from src.core.errors import UnauthorizedError, ForbiddenError
from src.repositories.user import UserRepository
from src.schemas.user import Token, TokenData, UserResponse

# Настройка логгера
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Аутентификация"])

# Oauth2 схема для получения токена из заголовка
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token", auto_error=False)


async def get_token_from_request(
    request: Request, 
    token_cookie: Optional[str] = Cookie(None, alias="access_token")
) -> Optional[str]:
    """
    Получить токен из запроса
    
    Args:
        request: Запрос FastAPI
        token_cookie: Токен из cookie
        
    Returns:
        Токен, если найден, иначе None
    """
    # Улучшенная функция проверки формата JWT
    def is_valid_jwt_format(token_str: str) -> bool:
        if not isinstance(token_str, str):
            return False
        # JWT должен содержать 2 точки (3 части)
        if token_str.count('.') != 2:
            return False
        # Минимальная длина валидного JWT
        if len(token_str) < 20:
            return False
        return True
    
    # Функция для логирования и проверки формата токена
    def log_and_validate_token(source: str, token_str: Any) -> Optional[str]:
        if token_str is None:
            logger.debug(f"Токен из {source} отсутствует")
            return None
            
        try:
            # Преобразуем в строку, если это не строка
            if not isinstance(token_str, str):
                token_str = str(token_str)
                
            # Предварительный просмотр токена для логов
            token_preview = token_str[:15] + "..." if len(token_str) > 15 else token_str
            
            # Проверка валидности JWT
            if not is_valid_jwt_format(token_str):
                logger.warning(f"Токен из {source} имеет невалидный формат JWT: {token_preview}")
                return None
                
            logger.info(f"Найден валидный JWT-токен из {source}: {token_preview}")
            return token_str
        except Exception as e:
            logger.error(f"Ошибка при обработке токена из {source}: {str(e)}")
            return None
    
    # Приоритет 1: Проверяем заголовок Authorization
    if "Authorization" in request.headers:
        try:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                return log_and_validate_token("заголовка Authorization", token)
        except Exception as e:
            logger.error(f"Ошибка при обработке заголовка Authorization: {str(e)}")
    
    # Приоритет 2: Проверяем cookie из параметра Depends
    if token_cookie:
        token = log_and_validate_token("cookie параметра Depends", token_cookie)
        if token:
            return token
    
    # Приоритет 3: Проверяем cookies из request напрямую
    try:
        cookies = request.cookies
        logger.debug(f"Cookies в запросе: {cookies}")
        if "access_token" in cookies:
            token = cookies["access_token"]
            validated_token = log_and_validate_token("request.cookies", token)
            if validated_token:
                return validated_token
    except Exception as e:
        logger.error(f"Ошибка при получении cookies из запроса: {str(e)}")
    
    # Приоритет 4: Проверяем форму
    try:
        form = await request.form()
        if "token" in form:
            token = form["token"]
            validated_token = log_and_validate_token("request.form", token)
            if validated_token:
                return validated_token
    except Exception as e:
        logger.error(f"Ошибка при получении формы: {str(e)}")
    
    # Приоритет 5: Проверяем заголовки запроса напрямую (на случай кастомных заголовков)
    try:
        headers = request.headers
        header_keys = [k.lower() for k in headers.keys()]
        
        # Проверяем различные возможные заголовки
        for header_name in ["authorization", "x-access-token", "token"]:
            if header_name in header_keys:
                header_value = headers[header_name]
                # Убираем 'Bearer ' если есть
                if header_name == "authorization" and header_value.startswith("Bearer "):
                    header_value = header_value.replace("Bearer ", "")
                
                validated_token = log_and_validate_token(f"заголовка {header_name}", header_value)
                if validated_token:
                    return validated_token
    except Exception as e:
        logger.error(f"Ошибка при анализе заголовков запроса: {str(e)}")
    
    logger.warning("Токен не найден ни в одном из источников запроса")
    return None


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Получить текущего пользователя по токену
    
    Args:
        request: Запрос
        token: JWT-токен
        db: Сессия базы данных
        
    Returns:
        Объект пользователя
        
    Raises:
        UnauthorizedError: Если токен невалидный или пользователь не найден
    """
    # Если токен не передан через oauth2_scheme, пытаемся получить его из других источников
    if not token:
        logger.info("Токен не получен через oauth2_scheme, пытаемся получить из запроса")
        token = await get_token_from_request(request)
    else:
        token_preview = token[:15] if isinstance(token, str) and len(token) > 15 else token
        logger.info(f"Получен токен через oauth2_scheme: {token_preview}...")
    
    if not token:
        logger.warning("Токен отсутствует, возвращаем ошибку UnauthorizedError")
        raise UnauthorizedError("Токен отсутствует")
    
    try:
        token_preview = token[:15] if isinstance(token, str) and len(token) > 15 else token
        logger.info(f"Декодируем токен: {token_preview}...")
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        subject = payload.get("sub")
        logger.info(f"Декодированный subject из токена: {subject}")
        
        if subject is None:
            logger.warning("Subject в токене отсутствует, возвращаем ошибку UnauthorizedError")
            raise UnauthorizedError("Невалидный токен")
        
        # Создаем объект TokenData, но не используем его напрямую
        token_data = TokenData(user_id=subject)
    except JWTError as e:
        logger.error(f"Ошибка при декодировании токена: {str(e)}")
        raise UnauthorizedError("Невалидный токен")
    
    # Получаем пользователя по ID или email
    user_repo = UserRepository(db)
    user = None
    
    # Проверяем, является ли значение числом
    if subject.isdigit():
        logger.info(f"Subject является числом ({subject}), ищем пользователя по ID")
        user = await user_repo.get_by_id(int(subject))
    else:
        logger.info(f"Subject не является числом, ищем пользователя по email: {subject}")
        user = await user_repo.get_by_email(subject)
    
    if user is None:
        logger.warning(f"Пользователь с subject={subject} не найден")
        raise UnauthorizedError("Пользователь не найден")
    
    logger.info(f"Пользователь найден: ID={user.id}, email={user.email}, роль={user.role}")
    
    if not user.is_active:
        logger.warning(f"Пользователь {user.email} неактивен")
        raise ForbiddenError("Пользователь неактивен")
    
    return user


async def get_current_active_business_user(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Получить текущего активного бизнес-пользователя
    
    Args:
        request: Запрос
        current_user: Текущий пользователь
        
    Returns:
        Объект пользователя
    """
    # Логируем информацию о пользователе и его роли
    logger.info(f"Business user check: user {current_user.email}, role: {current_user.role} (type: {type(current_user.role)})")
    
    # Проверяем роль в нижнем регистре
    role = current_user.role.lower() if isinstance(current_user.role, str) else str(current_user.role).lower()
    
    # Разрешённые роли для бизнес-модуля
    allowed_roles = ["business", "admin", "owner", "manager"]
    
    if role not in allowed_roles:
        logger.warning(f"Доступ запрещен: пользователь {current_user.email} с ролью {role} пытается получить доступ к бизнес-модулю")
        raise ForbiddenError(f"Недостаточно прав для доступа. Ваша роль: {role}, требуется одна из: {', '.join(allowed_roles)}")
    
    logger.info(f"Доступ разрешен: пользователь {current_user.email} с ролью {role} получил доступ к бизнес-модулю")
    return current_user


async def get_current_moderation_user(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Получить пользователя с правами модерации
    
    Args:
        request: Запрос
        current_user: Текущий пользователь
        
    Returns:
        Объект пользователя
        
    Raises:
        ForbiddenError: Если пользователь не имеет прав модерации
    """
    if current_user.role not in ["business", "admin"]:
        raise ForbiddenError("Недостаточно прав для доступа к модерации")
    
    return current_user


async def get_current_admin_user(
    request: Request,
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Получить текущего активного администратора
    
    Args:
        request: Запрос
        current_user: Текущий пользователь
        
    Returns:
        Объект пользователя
        
    Raises:
        ForbiddenError: Если пользователь не является администратором
    """
    if current_user.role != "admin":
        raise ForbiddenError("Недостаточно прав. Требуется аккаунт администратора")
    
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить JWT-токен по логину и паролю
    
    Args:
        request: Запрос
        form_data: Форма с данными для авторизации
        db: Сессия базы данных
        
    Returns:
        JWT-токен
        
    Raises:
        UnauthorizedError: Если логин или пароль неверны
    """
    # Получаем пользователя по email
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(form_data.username)
    if not user:
        raise UnauthorizedError("Неверный email или пароль")
    
    # Проверяем пароль
    if not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError("Неверный email или пароль")
    
    # Создаем токен доступа
    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Создан токен доступа для пользователя {user.email}")
    
    # Создаем базовый ответ
    response_data = {"access_token": access_token, "token_type": "bearer"}
    
    # Проверяем, является ли запрос из веб-браузера
    user_agent = request.headers.get("user-agent", "").lower()
    is_browser = "mozilla" in user_agent or "chrome" in user_agent or "safari" in user_agent or "edge" in user_agent
    
    # Если запрос из браузера, устанавливаем куки
    if is_browser:
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=response_data)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return response
    
    # Иначе возвращаем обычный JSON-ответ
    return response_data 