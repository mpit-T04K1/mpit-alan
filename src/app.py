from fastapi import FastAPI, Depends, Request, HTTPException, status, Form, Path
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse, HTMLResponse
from jose import jwt, JWTError
from src.core.errors import UnauthorizedError
import urllib.parse
import logging

from src.core.config import settings
from src.db.database import get_db, engine, Base
from src.api.health import router as health_router
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.companies import router as companies_router
from src.api.endpoints.services import router as services_router
from src.api.endpoints.bookings import router as bookings_router
from src.api.endpoints.schedule import router as schedule_router
from src.api.endpoints.analytics import router as analytics_router
from src.api.endpoints.users import router as users_router
from src.api.endpoints.notifications import router as notifications_router
from src.api.endpoints.moderation import router as moderation_router
from src.api.form_config import router as form_config_router
from src.api.business_module import router as business_module_router
from src.core.jinja_filters import configure_jinja_filters
from src.db_adapter import create_default_admin
from src.api.endpoints.auth import register_user, login_for_access_token, OAuth2PasswordRequestForm
from src.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from src.repositories.user import UserRepository
from src.models.user import UserRole
from src.utils.security import get_password_hash, verify_password
from src.services.auth_service import create_access_token, get_current_user

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
app.mount("/css", StaticFiles(directory=f"{settings.STATIC_DIR}/css"), name="css")
app.mount("/js", StaticFiles(directory=f"{settings.STATIC_DIR}/js"), name="js")
app.mount("/img", StaticFiles(directory=f"{settings.STATIC_DIR}/img"), name="img")
app.mount("/images", StaticFiles(directory=f"{settings.STATIC_DIR}/images"), name="images")
app.mount("/fonts", StaticFiles(directory=f"{settings.STATIC_DIR}/fonts"), name="fonts")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
app.state.templates = templates

# Настройка Jinja2 фильтров
configure_jinja_filters(app)

# Подключение API роутеров
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}")
app.include_router(companies_router, prefix=f"{settings.API_PREFIX}/companies", tags=["Companies"])
app.include_router(services_router, prefix=f"{settings.API_PREFIX}/services", tags=["Services"])
app.include_router(bookings_router, prefix=f"{settings.API_PREFIX}/bookings", tags=["Bookings"])
app.include_router(schedule_router, prefix=f"{settings.API_PREFIX}/schedule", tags=["Schedule"])
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(form_config_router, prefix=f"{settings.API_PREFIX}/form-configs", tags=["FormConfigs"])

# Подключение бизнес-модуля
app.include_router(business_module_router, prefix=f"{settings.ADMIN_PATH}", tags=["BusinessModule"])

# Событие запуска приложения
@app.on_event("startup")
async def startup_event():
    """Выполняется при запуске приложения"""
    try:
        # Таблицы уже должны быть созданы через миграции или другие механизмы
        # Просто создаем администратора по умолчанию, если его нет
        await create_default_admin()
        
        print("Приложение успешно запущено")
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")

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
        client_secret=None
    )
    
    # Используем функцию из auth.py для унификации логики
    return await login_for_access_token(form_data=form_data, db=db)

# Маршруты для новых шаблонов из mpit-frontend-main
@app.get("/business", response_class=HTMLResponse)
def business_page(request: Request):
    """
    Страница бизнеса
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон страницы бизнеса
    """
    return templates.TemplateResponse("business.html", {"request": request})

@app.get("/business/{business_id}", response_class=HTMLResponse)
def business_detail_page(request: Request, business_id: int):
    """
    Страница детальной информации о бизнесе
    
    Args:
        request: Запрос
        business_id: ID бизнеса
        
    Returns:
        HTML шаблон страницы детальной информации о бизнесе
    """
    return templates.TemplateResponse("business_page.html", {"request": request, "business_id": business_id})

@app.get("/business-registration", response_class=HTMLResponse)
def business_registration_page(request: Request):
    """
    Страница регистрации бизнеса
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон страницы регистрации бизнеса
    """
    return templates.TemplateResponse("business_registration.html", {"request": request})

@app.get("/business-registration-success", response_class=HTMLResponse)
def business_registration_success_page(request: Request):
    """
    Страница успешной регистрации бизнеса
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон страницы успешной регистрации бизнеса
    """
    return templates.TemplateResponse("business_registration_success.html", {"request": request})

@app.get("/cafe-example", response_class=HTMLResponse)
def cafe_example_page(request: Request):
    """
    Страница примера кафе
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон страницы примера кафе
    """
    return templates.TemplateResponse("cafe_example.html", {"request": request})

@app.get("/constructor", response_class=HTMLResponse)
def constructor_page(request: Request):
    """
    Страница конструктора
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон страницы конструктора
    """
    return templates.TemplateResponse("constructor.html", {"request": request})

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
        routes_info.append({
            "path": getattr(route, "path", None),
            "name": getattr(route, "name", None),
            "methods": getattr(route, "methods", None),
        })
    
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
    db: AsyncSession = Depends(get_db)
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
        if token.count('.') != 2:
            logger.error(f"Токен не соответствует формату JWT: {token[:15]}...")
            raise UnauthorizedError("Невалидный формат токена")
        
        # Декодируем токен
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
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
        response = RedirectResponse(
            url=redirect_url,
            status_code=303
        )
        
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
            path="/",         # Доступен для всего сайта
        )
        
        logger.info(f"Перенаправление на {redirect_url}")
        return response
        
    except (jwt.JWTError, UnauthorizedError) as e:
        logger.error(f"Ошибка при обработке токена: {str(e)}")
        return RedirectResponse(
            url="/login?error=" + urllib.parse.quote(str(e)),
            status_code=303
        )

# Маршрут для административной панели Джинсы
@app.get("/admin/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """
    Административная панель Джинсы
    
    Args:
        request: Запрос
        
    Returns:
        HTML шаблон административной панели
    """
    return templates.TemplateResponse("admin/index.html", {"request": request})

@app.get("/admin/{path:path}", response_class=HTMLResponse)
async def admin_panel_path(request: Request, path: str):
    """
    Маршруты административной панели Джинсы
    
    Args:
        request: Запрос
        path: Путь запроса
        
    Returns:
        HTML шаблон административной панели для указанного пути
    """
    # Проверяем существование шаблона
    template_path = f"admin/{path}.html"
    try:
        templates.get_template(template_path)
        return templates.TemplateResponse(template_path, {"request": request})
    except Exception as e:
        # Если шаблон не найден, возвращаем главную страницу админки
        print(f"Ошибка загрузки шаблона {template_path}: {e}")
        return templates.TemplateResponse("admin/index.html", {"request": request}) 