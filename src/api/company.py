from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.auth import get_current_user, get_current_active_business_user, get_current_admin_user
from src.core.errors import NotFoundError, ForbiddenError
from src.repositories.company import CompanyRepository
from src.repositories.working_hours import WorkingHoursRepository
from src.repositories.location import LocationRepository
from src.schemas.company import (
    CompanyCreate, 
    CompanyUpdate, 
    CompanyResponse, 
    CompanyDetailResponse,
    CompanyModerationUpdate
)
from src.schemas.working_hours import WorkingHoursCreate, WorkingHoursResponse
from src.schemas.location import LocationCreate, LocationResponse
from src.schemas.user import UserResponse

router = APIRouter(tags=["Компании"])


@router.post("", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
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
    return await CompanyRepository.create(db, company_data, current_user.id)


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
    return await CompanyRepository.get_multi(
        db, 
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
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_data: CompanyUpdate,
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Обновить информацию о компании
    
    Args:
        company_data: Данные для обновления компании
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
    Returns:
        Обновленная компания
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если текущий пользователь не имеет прав на обновление
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав на редактирование этой компании")
    
    return await CompanyRepository.update(db, company_id, company_data)


@router.patch("/{company_id}/moderation", response_model=CompanyResponse)
async def update_company_moderation_status(
    moderation_data: CompanyModerationUpdate,
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Обновить статус модерации компании (только для администраторов)
    
    Args:
        moderation_data: Данные для обновления статуса модерации
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Обновленная компания
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    return await CompanyRepository.update_moderation_status(
        db, 
        company_id, 
        moderation_data.moderation_status, 
        moderation_data.moderation_comment
    )


@router.delete("/{company_id}", response_model=CompanyResponse)
async def delete_company(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Удалить компанию
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
    Returns:
        Удаленная компания
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если текущий пользователь не имеет прав на удаление
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав на удаление этой компании")
    
    return await CompanyRepository.delete(db, company_id)


# Маршруты для работы с часами работы компании

@router.post("/{company_id}/working-hours", response_model=List[WorkingHoursResponse])
async def set_company_working_hours(
    working_hours: List[WorkingHoursCreate],
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Установить часы работы для компании
    
    Args:
        working_hours: Список часов работы для разных дней недели
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
    Returns:
        Список созданных часов работы
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если текущий пользователь не имеет прав
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав на редактирование этой компании")
    
    # Удаляем существующие часы работы и создаем новые
    await WorkingHoursRepository.delete_by_company(db, company_id)
    
    result = []
    for hours in working_hours:
        created = await WorkingHoursRepository.create(
            db, 
            WorkingHoursCreate(
                day=hours.day,
                open_time=hours.open_time,
                close_time=hours.close_time,
                is_working_day=hours.is_working_day,
                company_id=company_id
            )
        )
        result.append(created)
    
    return result


@router.get("/{company_id}/working-hours", response_model=List[WorkingHoursResponse])
async def get_company_working_hours(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить часы работы компании
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        
    Returns:
        Список часов работы
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    return await WorkingHoursRepository.get_by_company(db, company_id)


# Маршруты для работы с адресами компании

@router.post("/{company_id}/locations", response_model=LocationResponse)
async def add_company_location(
    location_data: LocationCreate,
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_business_user)
):
    """
    Добавить адрес компании
    
    Args:
        location_data: Данные адреса
        company_id: ID компании
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть владельцем или администратором)
        
    Returns:
        Созданный адрес
        
    Raises:
        NotFoundError: Если компания не найдена
        ForbiddenError: Если текущий пользователь не имеет прав
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    # Проверяем права доступа (владелец или админ)
    if current_user.role != "admin" and company.owner_id != current_user.id:
        raise ForbiddenError("У вас нет прав на редактирование этой компании")
    
    return await LocationRepository.create(
        db, 
        LocationCreate(
            address=location_data.address,
            city=location_data.city,
            postal_code=location_data.postal_code,
            country=location_data.country,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            is_main=location_data.is_main,
            company_id=company_id
        )
    )


@router.get("/{company_id}/locations", response_model=List[LocationResponse])
async def get_company_locations(
    company_id: int = Path(..., description="ID компании"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список адресов компании
    
    Args:
        company_id: ID компании
        db: Сессия базы данных
        
    Returns:
        Список адресов
        
    Raises:
        NotFoundError: Если компания не найдена
    """
    # Проверяем существование компании
    company = await CompanyRepository.get_by_id(db, company_id)
    if not company:
        raise NotFoundError(f"Компания с ID {company_id} не найдена")
    
    return await LocationRepository.get_by_company(db, company_id) 