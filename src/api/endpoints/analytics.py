"""
Эндпоинты для системы аналитики
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.db_adapter import get_db
from src.services.auth_service import get_current_user, get_current_admin_user
from src.repositories.booking import BookingRepository
from src.repositories.company import CompanyRepository
from src.repositories.service import ServiceRepository

router = APIRouter(tags=["Аналитика"])


@router.get("/company-stats/{company_id}")
async def get_company_stats(
    company_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата для статистики"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата для статистики"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить статистику по компании
    
    Args:
        company_id: ID компании
        start_date: Начальная дата фильтрации
        end_date: Конечная дата фильтрации
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Статистика по компании
    """
    company_repo = CompanyRepository(db)
    booking_repo = BookingRepository(db)
    
    # Проверяем существование компании
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    # Проверяем права доступа
    is_admin = current_user.role == "admin"
    is_owner = company.owner_id == current_user.id
    
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр статистики этой компании"
        )
    
    # Если даты не указаны, используем последние 30 дней
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Получаем статистику бронирований
    booking_stats = await booking_repo.get_company_booking_stats(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "company_id": company_id,
        "company_name": company.name,
        "start_date": start_date,
        "end_date": end_date,
        "bookings": booking_stats
    }


@router.get("/service-stats/{service_id}")
async def get_service_stats(
    service_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата для статистики"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата для статистики"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить статистику по услуге
    
    Args:
        service_id: ID услуги
        start_date: Начальная дата фильтрации
        end_date: Конечная дата фильтрации
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Статистика по услуге
    """
    service_repo = ServiceRepository(db)
    booking_repo = BookingRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем существование услуги
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {service_id} не найдена"
        )
    
    # Получаем компанию, которой принадлежит услуга
    company = await company_repo.get_by_id(service.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {service.company_id} не найдена"
        )
    
    # Проверяем права доступа
    is_admin = current_user.role == "admin"
    is_owner = company.owner_id == current_user.id
    
    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр статистики этой услуги"
        )
    
    # Если даты не указаны, используем последние 30 дней
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Получаем статистику бронирований по услуге
    booking_stats = await booking_repo.get_service_booking_stats(
        service_id=service_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "service_id": service_id,
        "service_name": service.name,
        "company_id": company.id,
        "company_name": company.name,
        "start_date": start_date,
        "end_date": end_date,
        "bookings": booking_stats
    }


@router.get("/dashboard")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Получить данные для административной панели
    
    Args:
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Общая статистика системы
    """
    company_repo = CompanyRepository(db)
    booking_repo = BookingRepository(db)
    
    # Получаем статистику
    total_companies = await company_repo.count_all()
    pending_companies = await company_repo.count_pending()
    total_bookings = await booking_repo.count_all()
    recent_bookings = await booking_repo.get_recent(limit=10)
    
    return {
        "total_companies": total_companies,
        "pending_companies": pending_companies,
        "total_bookings": total_bookings,
        "recent_bookings": recent_bookings
    } 