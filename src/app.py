from fastapi import FastAPI, Depends, Request, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from jose import jwt
from src.core.errors import UnauthorizedError
import urllib.parse
import logging

from src.settings import settings
from src.adapters.database.session import get_db
from src.api.health import router as health_router
from src.api.auth import router as auth_router
from src.api.companies import router as companies_router
from src.api.services import router as services_router
from src.api.bookings import router as bookings_router
from src.api.schedule import router as schedule_router
from src.api.analytics import router as analytics_router
from src.api.users import router as users_router
from src.api.notifications import router as notifications_router
from src.api.form_config import router as form_config_router
from src.api.business_module import router as business_module_router
from src.core.jinja_filters import configure_jinja_filters
from src.api.auth import register_user, login_for_access_token
from src.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from src.repositories.user import UserRepository

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание экземпляра FastAPI
app = FastAPI(
    title="Сервис бронирования",
    description="API для сервиса бронирования услуг компаний",
    version="1.0.0",
)

# Создание таблиц происходит в скрипте миграций
# При использовании асинхронного движка нельзя напрямую вызывать create_all

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует ограничить до конкретных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
app.state.templates = templates

# Настройка Jinja2 фильтров
configure_jinja_filters(app)

# Подключение API роутеров
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}")
app.include_router(
    companies_router, prefix=f"{settings.API_PREFIX}/companies", tags=["Companies"]
)
app.include_router(
    services_router, prefix=f"{settings.API_PREFIX}/services", tags=["Services"]
)
app.include_router(
    bookings_router, prefix=f"{settings.API_PREFIX}/bookings", tags=["Bookings"]
)
app.include_router(
    schedule_router, prefix=f"{settings.API_PREFIX}/schedule", tags=["Schedule"]
)
app.include_router(
    analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"]
)
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(
    notifications_router,
    prefix=f"{settings.API_PREFIX}/notifications",
    tags=["Notifications"],
)
app.include_router(
    form_config_router,
    prefix=f"{settings.API_PREFIX}/form-configs",
    tags=["FormConfigs"],
)

# Подключение бизнес-модуля
app.include_router(
    business_module_router, prefix=f"{settings.ADMIN_PATH}", tags=["BusinessModule"]
)



@app.get("/")
def read_root(request: Request):
    """
    Главная страница приложения

    Args:
        request: Запрос

    Returns:
        HTML шаблон главной страницы
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
def login_page(request: Request):
    """
    Страница входа

    Args:
        request: Запрос

    Returns:
        HTML шаблон страницы входа
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
def logout(request: Request):
    """
    Выход из системы

    Args:
        request: Запрос

    Returns:
        Перенаправление на страницу входа
    """
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    return response


@app.get("/register")
def register_page(request: Request):
    """
    Страница регистрации

    Args:
        request: Запрос

    Returns:
        HTML шаблон страницы регистрации
    """
    return templates.TemplateResponse("register.html", {"request": request})


# Прямой маршрут для регистрации пользователя
@app.post("/api/auth/register", response_model=UserResponse)
async def register_direct(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация пользователя напрямую

    Args:
        user: Данные пользователя
        db: Сессия базы данных

    Returns:
        Данные созданного пользователя
    """
    print(f"Попытка регистрации пользователя с email: {user.email}")

    # Используем функцию из auth.py для унификации логики
    return await register_user(user=user, db=db)


# Прямой маршрут для входа пользователя
@app.post("/api/auth/token", response_model=Token)
async def login_direct(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Аутентификация пользователя и получение токена напрямую

    Args:
        form_data: Форма входа
        db: Сессия базы данных

    Returns:
        Токен доступа
    """
    print(f"Попытка входа с email: {login_data.email}")

    # Создаем форму OAuth2 из данных логина
    form_data = OAuth2PasswordRequestForm(
        username=login_data.email,
        password=login_data.password,
        scope="",
        client_id=None,
        client_secret=None,
    )

    # Используем функцию из auth.py для унификации логики
    return await login_for_access_token(form_data=form_data, db=db)


# Диагностический маршрут для проверки состояния приложения
@app.get("/api/test-api")
async def test_api():
    """
    Диагностический маршрут для проверки работы API

    Returns:
        Информация о состоянии API
    """
    # Собираем информацию о зарегистрированных маршрутах
    routes_info = []
    for route in app.routes:
        routes_info.append(
            {
                "path": getattr(route, "path", None),
                "name": getattr(route, "name", None),
                "methods": getattr(route, "methods", None),
            }
        )

    # Информация о настройках приложения
    config_info = {
        "API_PREFIX": settings.API_PREFIX,
        "ADMIN_PATH": settings.ADMIN_PATH,
        "HOST": settings.HOST,
        "PORT": settings.PORT,
    }

    return {
        "status": "ok",
        "message": "API работает корректно",
        "routes_count": len(app.routes),
        "sample_routes": routes_info[:10],  # Возвращаем первые 10 маршрутов
        "config": config_info,
    }


# Мост для аутентификации при переходе в административную панель
@app.get("/auth-bridge")
def auth_bridge(request: Request):
    """
    Страница-мост для передачи токена аутентификации

    Args:
        request: Запрос

    Returns:
        HTML шаблон страницы-моста для аутентификации
    """
    return templates.TemplateResponse("auth_bridge.html", {"request": request})


# Обработчик POST-запросов административного интерфейса с токеном в форме
@app.post("/admin{path:path}")
async def admin_post_handler(
    request: Request,
    path: str = Path(...),
    token: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Обработчик POST-запросов к административной панели с передачей токена через форму

    Args:
        request: Запрос
        path: Путь запроса
        token: Токен аутентификации
        db: Сессия базы данных

    Returns:
        Перенаправляет запрос к бизнес-модулю с сохранением токена в сессии
    """
    try:
        # Логирование входящего запроса
        logger.info(f"POST /admin{path} - Получен token: {token[:15]}...")
        logger.info(f"User-Agent: {request.headers.get('user-agent')}")
        logger.info(f"Cookies: {request.cookies}")

        # Проверяем, что токен имеет формат JWT (содержит две точки)
        if token.count(".") != 2:
            logger.error(f"Токен не соответствует формату JWT: {token[:15]}...")
            raise UnauthorizedError("Невалидный формат токена")

        # Декодируем токен
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            logger.info(f"Токен декодирован успешно: {payload}")
        except jwt.JWTError as e:
            logger.error(f"Ошибка при декодировании токена: {str(e)}")
            raise UnauthorizedError(f"Ошибка декодирования токена: {str(e)}")

        subject = payload.get("sub")
        logger.info(f"Subject из токена: {subject}")

        if not subject:
            logger.error("Ошибка: subject отсутствует в токене")
            raise UnauthorizedError("Невалидный токен: отсутствует subject")

        # Получаем пользователя по ID или email
        user_repo = UserRepository(db)
        user = None

        # Проверяем, является ли значение числом
        if isinstance(subject, str) and subject.isdigit():
            logger.info(f"Поиск пользователя по ID: {subject}")
            user = await user_repo.get_by_id(int(subject))
        else:
            logger.info(f"Поиск пользователя по email: {subject}")
            user = await user_repo.get_by_email(subject)

        if not user:
            logger.error(f"Пользователь с subject={subject} не найден")
            raise UnauthorizedError("Пользователь не найден")

        logger.info(f"Пользователь найден: {user.email}, роль: {user.role}")

        if not user.is_active:
            logger.error(f"Пользователь {user.email} неактивен")
            raise UnauthorizedError("Пользователь неактивен")

        # Добавляем токен в заголовок запроса
        logger.info("Добавление токена в заголовок запроса")
        request.headers.__dict__["_list"].append(
            (b"authorization", f"Bearer {token}".encode())
        )

        # Формируем URL для перенаправления
        redirect_url = f"{settings.ADMIN_PATH}/{path}"
        logger.info(f"Подготовка перенаправления на: {redirect_url}")

        # Устанавливаем cookie с токеном
        response = RedirectResponse(url=redirect_url, status_code=303)

        # Добавляем отладочные заголовки в режиме разработки
        if settings.ENVIRONMENT == "development":
            response.headers["X-Debug-Token-Received"] = token[:10] + "..."
            response.headers["X-Debug-User"] = user.email
            response.headers["X-Debug-Role"] = user.role

        logger.info(f"Установка cookie access_token для пользователя {user.email}")
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=60 * 60,  # 1 час
            path="/",  # Доступен для всего сайта
        )

        logger.info(f"Перенаправление на {redirect_url}")
        return response

    except (jwt.JWTError, UnauthorizedError) as e:
        logger.error(f"Ошибка при обработке токена: {str(e)}")
        return RedirectResponse(
            url="/login?error=" + urllib.parse.quote(str(e)), status_code=303
        )
