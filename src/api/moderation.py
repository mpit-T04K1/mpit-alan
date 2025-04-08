from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.auth import get_current_admin_user
from src.core.errors import NotFoundError, ForbiddenError
from src.repositories.moderation import ModerationRepository
from src.repositories.company import CompanyRepository
from src.schemas.moderation import (
    ModerationRecordResponse,
    ModerationUpdate,
    AutoCheckResult
)
from src.schemas.user import UserResponse

router = APIRouter(tags=["Модерация"])


@router.get("/pending", response_model=List[ModerationRecordResponse])
async def get_pending_moderation_records(
    limit: int = Query(20, description="Лимит записей на странице"),
    offset: int = Query(0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Получить список записей модерации в статусе "на рассмотрении"
    
    Args:
        limit: Лимит записей на странице
        offset: Смещение от начала списка
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Список записей модерации
    """
    return await ModerationRepository.get_pending_records(db, limit, offset)


@router.get("/company/{company_id}", response_model=List[ModerationRecordResponse])
async def get_company_moderation_records(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Получить историю модерации для компании
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Список записей модерации для компании
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    return await ModerationRepository.get_by_company_id(db, company_id)


@router.get("/{record_id}", response_model=ModerationRecordResponse)
async def get_moderation_record(
    record_id: int = Path(..., description="ID записи модерации"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Получить детали записи модерации
    
    Args:
        record_id: ID записи модерации
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Запись модерации
        
    Raises:
        NotFoundError: Если запись модерации не найдена
    """
    record = await ModerationRepository.get_by_id(db, record_id)
    if not record:
        raise NotFoundError(f"Запись модерации с ID {record_id} не найдена")
    
    return record


@router.post("/auto-check/{company_id}", response_model=AutoCheckResult)
async def auto_check_company(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Запустить автоматическую проверку компании
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Результат автоматической проверки
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Выполняем автоматическую проверку
    result = await ModerationRepository.auto_check_company(company_id)
    
    # Создаем новую запись модерации с результатом проверки
    await ModerationRepository.create(
        db, 
        ModerationRecordCreate(
            company_id=company_id,
            auto_check_passed=result.passed
        )
    )
    
    return result


@router.put("/{record_id}", response_model=ModerationRecordResponse)
async def update_moderation_status(
    data: ModerationUpdate = Body(...),
    record_id: int = Path(..., description="ID записи модерации"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Обновить статус модерации
    
    Args:
        data: Данные для обновления статуса модерации
        record_id: ID записи модерации
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Обновленная запись модерации
        
    Raises:
        NotFoundError: Если запись модерации не найдена
    """
    # Проверяем существование записи модерации
    record = await ModerationRepository.get_by_id(db, record_id)
    if not record:
        raise NotFoundError(f"Запись модерации с ID {record_id} не найдена")
    
    # Обновляем статус модерации
    updated_record = await ModerationRepository.update(
        db, 
        record_id, 
        current_user.id,
        data
    )
    
    return updated_record 