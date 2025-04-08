"""
Эндпоинты для работы с услугами
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.services.auth_service import get_current_user, get_current_admin_user
from src.repositories.service import ServiceRepository
from src.repositories.company import CompanyRepository
from src.schemas.service import (
    ServiceCreate, 
    ServiceUpdate, 
    ServiceResponse
)

router = APIRouter(tags=["Услуги"])


@router.post("", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создать новую услугу
    
    Args:
        service_data: Данные для создания услуги
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Созданная услуга
    """
    service_repo = ServiceRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем, существует ли компания
    company = await company_repo.get_by_id(service_data.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {service_data.company_id} не найдена"
        )
    
    # Проверяем, имеет ли пользователь права на добавление услуги
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на добавление услуг для этой компании"
        )
    
    return await service_repo.create(service_data)


@router.get("", response_model=List[ServiceResponse])
async def list_services(
    company_id: Optional[int] = Query(None, description="ID компании"),
    category: Optional[str] = Query(None, description="Категория услуги"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список услуг с фильтрацией и пагинацией
    
    Args:
        company_id: ID компании для фильтрации
        category: Категория услуги для фильтрации
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        
    Returns:
        Список услуг
    """
    service_repo = ServiceRepository(db)
    return await service_repo.get_all(
        company_id=company_id,
        category=category,
        limit=limit,
        offset=offset
    )


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int = Path(..., description="ID услуги"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию об услуге по ID
    
    Args:
        service_id: ID услуги
        db: Сессия базы данных
        
    Returns:
        Информация об услуге
    """
    service_repo = ServiceRepository(db)
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {service_id} не найдена"
        )
    
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Обновить информацию об услуге
    
    Args:
        service_id: ID услуги
        service_data: Данные для обновления услуги
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Обновленная услуга
    """
    service_repo = ServiceRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем существование услуги
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {service_id} не найдена"
        )
    
    # Получаем компанию
    company = await company_repo.get_by_id(service.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {service.company_id} не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на редактирование услуг этой компании"
        )
    
    return await service_repo.update(service_id, service_data.dict(exclude_unset=True))


@router.delete("/{service_id}", response_model=ServiceResponse)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удалить услугу
    
    Args:
        service_id: ID услуги
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Удаленная услуга
    """
    service_repo = ServiceRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем существование услуги
    service = await service_repo.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {service_id} не найдена"
        )
    
    # Получаем компанию
    company = await company_repo.get_by_id(service.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Компания с ID {service.company_id} не найдена"
        )
    
    # Проверяем права доступа
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление услуг этой компании"
        )
    
    deleted = await service_repo.delete(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {service_id} не найдена"
        )
    
    return service 