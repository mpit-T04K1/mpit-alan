"""
Эндпоинты для работы с компаниями
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.services.auth_service import get_current_user, get_current_admin_user
from src.repositories.company import CompanyRepository
from src.schemas.company import (
    CompanyCreate, 
    CompanyUpdate, 
    CompanyResponse, 
    CompanyDetailResponse
)

router = APIRouter(tags=["Компании"])


@router.post("", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создать новую компанию
    
    Args:
        company_data: Данные для создания компании
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Созданная компания
    """
    company_repo = CompanyRepository(db)
    return await company_repo.create(company_data, current_user.id)


@router.get("", response_model=List[CompanyResponse])
async def list_companies(
    search: Optional[str] = Query(None, description="Поиск по названию компании"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список компаний с фильтрацией и пагинацией
    
    Args:
        search: Строка поиска по названию
        category: Фильтр по категории
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        
    Returns:
        Список компаний
    """
    company_repo = CompanyRepository(db)
    return await company_repo.get_all(
        search=search, 
        category=category, 
        limit=limit, 
        offset=offset
    )


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию о компании по ID
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        
    Returns:
        Детальная информация о компании
    """
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Обновить информацию о компании
    
    Args:
        company_id: ID компании
        company_data: Данные для обновления компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
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
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на редактирование этой компании"
        )
    
    return await company_repo.update(company_id, company_data.dict(exclude_unset=True))


@router.delete("/{company_id}", response_model=CompanyResponse)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удалить компанию
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
    Returns:
        Удаленная компания
    """
    company_repo = CompanyRepository(db)
    
    # Проверяем существование компании
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление этой компании"
        )
    
    deleted = await company_repo.delete(company_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {company_id} не найдена"
        )
    
    return company 