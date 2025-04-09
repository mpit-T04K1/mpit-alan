from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.auth import get_current_active_business_user
from src.core.errors import NotFoundError, ForbiddenError
from src.repositories.analytics import AnalyticsRepository
from src.repositories.company import CompanyRepository
from src.schemas.analytics import AnalyticsPeriodRequest, AnalyticsResponse
from src.schemas.user import UserResponse

router = APIRouter(tags=["Аналитика"])


@router.post("", response_model=Dict[str, Any])
async def get_analytics_by_period(
    period_data: AnalyticsPeriodRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Получить аналитику за указанный период
    
    Args:
        period_data: Данные периода для анализа
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Данные аналитики
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если пользователь не имеет доступа к компании
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, period_data.company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {period_data.company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав для просмотра аналитики этой компании")
    
    # Получаем аналитику
    return await AnalyticsRepository.get_company_analytics(
        db,
        period_data.company_id,
        period_data.start_date,
        period_data.end_date
    )


@router.get("/company/{company_id}/monthly", response_model=Dict[str, Any])
async def get_monthly_analytics(
    company_id: int = Path(..., description="ID компании"),
    year: Optional[int] = Query(None, description="Год для анализа (по умолчанию текущий)"),
    month: Optional[int] = Query(None, description="Месяц для анализа (по умолчанию текущий)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Получить месячную аналитику для компании
    
    Args:
        company_id: ID компании
        year: Год (по умолчанию текущий)
        month: Месяц (по умолчанию текущий)
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Данные аналитики за месяц
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если пользователь не имеет доступа к компании
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав для просмотра аналитики этой компании")
    
    # Определяем текущий год и месяц, если не указаны
    today = date.today()
    year = year or today.year
    month = month or today.month
    
    # Вычисляем начало и конец месяца
    start_date = date(year, month, 1)
    
    # Определяем последний день месяца
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    end_date = date(next_year, next_month, 1) - timedelta(days=1)
    
    # Получаем аналитику
    result = await AnalyticsRepository.get_company_analytics(
        db,
        company_id,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time())
    )
    
    # Добавляем информацию о периоде
    result["period_type"] = "monthly"
    result["year"] = year
    result["month"] = month
    
    return result


@router.get("/company/{company_id}/weekly", response_model=Dict[str, Any])
async def get_weekly_analytics(
    company_id: int = Path(..., description="ID компании"),
    date_from: Optional[date] = Query(None, description="Начальная дата недели (по умолчанию текущая неделя)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Получить недельную аналитику для компании
    
    Args:
        company_id: ID компании
        date_from: Начальная дата недели (по умолчанию начало текущей недели)
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Данные аналитики за неделю
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если пользователь не имеет доступа к компании
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав для просмотра аналитики этой компании")
    
    # Определяем начало и конец недели
    today = date.today()
    if date_from:
        # Если указана начальная дата, используем её
        start_date = date_from
    else:
        # Иначе берем начало текущей недели (понедельник)
        start_date = today - timedelta(days=today.weekday())
    
    # Конец недели - через 7 дней после начала
    end_date = start_date + timedelta(days=6)
    
    # Получаем аналитику
    result = await AnalyticsRepository.get_company_analytics(
        db,
        company_id,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time())
    )
    
    # Добавляем информацию о периоде
    result["period_type"] = "weekly"
    result["start_date"] = start_date
    result["end_date"] = end_date
    
    return result 