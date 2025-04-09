from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.auth import get_current_active_business_user
from src.core.config import settings
from src.repositories.company import CompanyRepository
from src.repositories.service import ServiceRepository
from src.repositories.booking import BookingRepository
from src.repositories.analytics import AnalyticsRepository
from src.repositories.form_config import FormConfigRepository
from src.schemas.user import UserResponse

router = APIRouter()
# Шаблоны будут получены из state приложения

# Вспомогательная функция для получения шаблонов из state приложения
def get_templates(request: Request) -> Jinja2Templates:
    """
    Получает экземпляр шаблонов из state приложения
    
    Args:
        request: Запрос
        
    Returns:
        Экземпляр Jinja2Templates
    """
    return request.app.state.templates

@router.get("/", response_class=HTMLResponse)
async def business_module_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Главная страница бизнес-модуля
    
    Args:
        request: Запрос
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с панелью управления
    """
    # Получаем компании пользователя
    company_repo = CompanyRepository(db)
    companies = await company_repo.get_by_owner_id(current_user.id)
    
    templates = get_templates(request)
    
    return templates.TemplateResponse(
        "business/dashboard.html",
        {
            "request": request, 
            "user": current_user,
            "companies": companies
        }
    )


@router.get("/company/{company_id}", response_class=HTMLResponse)
async def company_dashboard(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Панель управления компанией
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с панелью управления компанией
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        # Получаем количество активных бронирований
        booking_repo = BookingRepository(db)
        active_bookings_count = await booking_repo.count_active_by_company(company_id)
        
        # Получаем количество услуг
        service_repo = ServiceRepository(db)
        services_count = await service_repo.count_by_company(company_id)
        
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "business/company_dashboard.html",
            {
                "request": request, 
                "user": current_user,
                "company": company,
                "active_bookings_count": active_bookings_count,
                "services_count": services_count
            }
        )
    
    # Если нет прав доступа, перенаправляем на главную
    templates = get_templates(request)
    return templates.TemplateResponse(
        "business/access_denied.html",
        {"request": request, "user": current_user}
    )


@router.get("/company/{company_id}/services", response_class=HTMLResponse)
async def company_services(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Страница управления услугами компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с управлением услугами
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        # Получаем услуги компании
        service_repo = ServiceRepository(db)
        services = await service_repo.get_by_company(company_id)
        
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "business/services.html",
            {
                "request": request, 
                "user": current_user,
                "company": company,
                "services": services
            }
        )
    
    # Если нет прав доступа, перенаправляем на главную
    templates = get_templates(request)
    return templates.TemplateResponse(
        "business/access_denied.html",
        {"request": request, "user": current_user}
    )


@router.get("/company/{company_id}/bookings", response_class=HTMLResponse)
async def company_bookings(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Страница управления бронированиями компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с управлением бронированиями
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        # Получаем бронирования компании
        booking_repo = BookingRepository(db)
        bookings = await booking_repo.get_by_company(company_id)
        
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "business/bookings.html",
            {
                "request": request, 
                "user": current_user,
                "company": company,
                "bookings": bookings
            }
        )
    
    # Если нет прав доступа, перенаправляем на главную
    templates = get_templates(request)
    return templates.TemplateResponse(
        "business/access_denied.html",
        {"request": request, "user": current_user}
    )


@router.get("/company/{company_id}/analytics", response_class=HTMLResponse)
async def company_analytics(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Страница аналитики компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с аналитикой
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        # Получаем аналитику за последний месяц
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        analytics_repo = AnalyticsRepository(db)
        analytics = await analytics_repo.get_company_analytics(
            company_id, start_date, end_date
        )
        
        templates = get_templates(request)
        
        return templates.TemplateResponse(
            "business/analytics.html",
            {
                "request": request, 
                "user": current_user,
                "company": company,
                "analytics": analytics,
                "period": {"start": start_date, "end": end_date}
            }
        )
    
    # Если нет прав доступа, перенаправляем на главную
    templates = get_templates(request)
    return templates.TemplateResponse(
        "business/access_denied.html",
        {"request": request, "user": current_user}
    )


@router.get("/company/{company_id}/settings", response_class=HTMLResponse)
async def company_settings(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Страница настроек компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с настройками компании
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        templates = get_templates(request)
        return templates.TemplateResponse(
            "business/settings.html",
            {
                "request": request, 
                "user": current_user,
                "company": company
            }
        )
    
    # Если нет прав доступа, перенаправляем на главную
    templates = get_templates(request)
    return templates.TemplateResponse(
        "business/access_denied.html",
        {"request": request, "user": current_user}
    )


@router.get("/register-company", response_class=HTMLResponse)
async def register_company_page(
    request: Request,
    business_type: str = Query(None, description="Тип бизнеса для динамической формы"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Страница динамической регистрации компании
    
    Args:
        request: Запрос
        business_type: Тип бизнеса для загрузки соответствующей конфигурации формы
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        HTML страница с формой регистрации компании
    """
    # Если тип бизнеса указан, получаем конфигурацию формы для этого типа
    form_config = None
    form_config_repo = FormConfigRepository(db)
    
    if business_type:
        form_config = await form_config_repo.get_active_by_types(
            business_type, "company_registration"
        )
    
    # Если конфигурация не найдена, получаем дефолтную
    if not form_config:
        form_config = await form_config_repo.get_active_by_types(
            "default", "company_registration"
        )
    
    # Если нет даже дефолтной конфигурации, создаем ее
    if not form_config:
        await form_config_repo.create_default_configs()
        form_config = await form_config_repo.get_active_by_types(
            "default", "company_registration"
        )
    
    # Получаем список доступных типов бизнеса
    business_types = [
        {"value": "restaurant", "label": "Ресторан/Кафе"},
        {"value": "beauty", "label": "Салон красоты"},
        {"value": "clinic", "label": "Медицинская клиника"},
        {"value": "service", "label": "Сервисный центр"},
        {"value": "other", "label": "Другое"}
    ]
    
    templates = get_templates(request)
    
    return templates.TemplateResponse(
        "business/register_company.html",
        {
            "request": request, 
            "user": current_user,
            "form_config": form_config,
            "business_type": business_type,
            "business_types": business_types
        }
    )


@router.get("/api/companies", response_class=HTMLResponse)
async def get_companies_list_api(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    API для получения списка компаний текущего пользователя
    
    Args:
        request: Запрос
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        JSON с компаниями пользователя
    """
    # Получаем компании пользователя
    company_repo = CompanyRepository(db)
    companies = await company_repo.get_by_owner_id(current_user.id)
    
    # Возвращаем в формате JSON
    from fastapi.responses import JSONResponse
    return JSONResponse(content=[company.dict() for company in companies])


@router.get("/api/companies/{company_id}", response_class=HTMLResponse)
async def get_company_details_api(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    API для получения детальной информации о компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        JSON с информацией о компании
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        from fastapi.responses import JSONResponse
        return JSONResponse(content=company.dict())
    
    # Если нет прав доступа, возвращаем ошибку
    from fastapi.responses import JSONResponse
    from fastapi import status
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "У вас нет доступа к этой компании"}
    )


@router.get("/api/companies/{company_id}/services", response_class=HTMLResponse)
async def get_company_services_api(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    API для получения услуг компании
    
    Args:
        request: Запрос
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        JSON со списком услуг компании
    """
    # Получаем данные компании
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    # Проверяем права доступа
    if company and (company.owner_id == current_user.id or current_user.role == "admin"):
        # Получаем услуги компании
        service_repo = ServiceRepository(db)
        services = await service_repo.get_by_company(company_id)
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content=[service.dict() for service in services])
    
    # Если нет прав доступа, возвращаем ошибку
    from fastapi.responses import JSONResponse
    from fastapi import status
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "У вас нет доступа к услугам этой компании"}
    ) 