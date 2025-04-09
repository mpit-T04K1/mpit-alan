"""
Эндпоинты для системы модерации
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.services.auth_service import get_current_admin_user
from src.repositories.company import CompanyRepository
from src.schemas.company import (
    CompanyResponse, 
    CompanyDetailResponse,
    CompanyModerationUpdate
)

router = APIRouter(tags=["Модерация"])


@router.get("/pending-companies", response_model=List[CompanyResponse])
async def get_pending_companies(
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user)  # Только админ может модерировать
):
    """
    Получить список компаний, ожидающих модерацию
    
    Args:
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Список компаний на модерации
    """
    company_repo = CompanyRepository(db)
    return await company_repo.get_pending_moderation(limit=limit, offset=offset)


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def moderate_company(
    company_id: int,
    moderation_data: CompanyModerationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user)  # Только админ может модерировать
):
    """
    Модерация компании (одобрение/отклонение)
    
    Args:
        company_id: ID компании
        moderation_data: Данные модерации (статус, комментарий)
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Обновленная компания
    """
    company_repo = CompanyRepository(db)
    
    # Проверяем существование компании
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    update_data = moderation_data.dict(exclude_unset=True)
    updated_company = await company_repo.update(company_id, update_data)
    
    return updated_company 