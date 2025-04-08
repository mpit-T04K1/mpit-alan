from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import json
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.auth_service import get_current_user
from src.services.company_service import CompanyService
from src.services.moderation_service import ModerationService
from src.services.booking_service import BookingService
from src.models.user import User
from src.utils.permissions import check_company_permission

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")

# Существующие маршруты

@router.get("/dashboard", response_class=HTMLResponse)
async def business_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отображает дашборд для бизнеса"""
    company_service = CompanyService(db)
    
    # Получаем компании пользователя
    user_companies = await company_service.get_user_companies(current_user.id)
    
    return templates.TemplateResponse(
        "business/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "companies": user_companies
        }
    )

@router.get("/companies/{company_id}", response_class=HTMLResponse)
async def company_dashboard(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отображает дашборд для конкретной компании"""
    company_service = CompanyService(db)
    
    # Проверяем права доступа пользователя к компании
    await check_company_permission(db, current_user, company_id)
    
    # Получаем данные о компании
    company = await company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    # Получаем статистику бронирований
    booking_service = BookingService(db)
    recent_bookings = await booking_service.get_recent_bookings(company_id, limit=5)
    bookings_stats = await booking_service.get_bookings_stats(company_id)
    
    return templates.TemplateResponse(
        "business/company_dashboard.html",
        {
            "request": request,
            "user": current_user,
            "company": company,
            "recent_bookings": recent_bookings,
            "bookings_stats": bookings_stats
        }
    )

@router.get("/register", response_class=HTMLResponse)
async def register_company_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Страница регистрации новой компании"""
    return templates.TemplateResponse(
        "business/register_company.html",
        {
            "request": request,
            "user": current_user
        }
    )

@router.get("/moderation/{company_id}", response_class=HTMLResponse)
async def moderation_panel(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Панель модерации для компании"""
    # Проверяем права доступа пользователя к компании
    await check_company_permission(db, current_user, company_id)
    
    # Получаем данные о компании
    company_service = CompanyService(db)
    company = await company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    # Получаем историю модерации
    moderation_service = ModerationService(db)
    moderation_history = await moderation_service.get_moderation_history(company_id)
    
    return templates.TemplateResponse(
        "business/moderation_panel.html",
        {
            "request": request,
            "user": current_user,
            "company": company,
            "moderation_history": moderation_history
        }
    )

# Добавляем новый маршрут для управления расписанием

@router.get("/companies/{company_id}/schedule", response_class=HTMLResponse)
async def company_schedule(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Страница управления расписанием компании"""
    # Проверяем права доступа пользователя к компании
    await check_company_permission(db, current_user, company_id)
    
    # Получаем данные о компании
    company_service = CompanyService(db)
    company = await company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    return templates.TemplateResponse(
        "business/schedule_management.html",
        {
            "request": request,
            "user": current_user,
            "company": company
        }
    ) 