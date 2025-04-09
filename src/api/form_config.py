from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.api.auth import get_current_admin_user
from src.repositories.form_config import FormConfigRepository
from src.schemas.form_config import (
    FormConfigCreate,
    FormConfigUpdate,
    FormConfigResponse
)
from src.schemas.user import UserResponse

router = APIRouter(tags=["Конфигурации форм"])


@router.post("", response_model=FormConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_form_config(
    form_config: FormConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Создать новую конфигурацию формы (только для администраторов)
    
    Args:
        form_config: Данные для создания конфигурации формы
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Созданная конфигурация формы
    """
    return await FormConfigRepository.create(db, form_config)


@router.get("", response_model=List[FormConfigResponse])
async def get_form_configs(
    business_type: str = Query(None, description="Фильтр по типу бизнеса"),
    form_type: str = Query(None, description="Фильтр по типу формы"),
    active_only: bool = Query(True, description="Только активные конфигурации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список конфигураций форм
    
    Args:
        business_type: Фильтр по типу бизнеса
        form_type: Фильтр по типу формы
        active_only: Только активные конфигурации
        db: Сессия базы данных
        
    Returns:
        Список конфигураций форм
    """
    if business_type and form_type:
        # Если указаны оба параметра, возвращаем конкретную конфигурацию
        form_config = await FormConfigRepository.get_active_by_types(db, business_type, form_type)
        return [form_config] if form_config else []
    
    elif business_type:
        # Если указан только тип бизнеса, возвращаем все конфигурации для этого типа
        return await FormConfigRepository.get_by_business_type(db, business_type, active_only)
    
    # Здесь можно добавить дополнительные фильтры по необходимости
    # Пока просто заглушка, возвращающая пустой список
    return []


@router.get("/{form_config_id}", response_model=FormConfigResponse)
async def get_form_config(
    form_config_id: int = Path(..., description="ID конфигурации формы", ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить конфигурацию формы по ID
    
    Args:
        form_config_id: ID конфигурации формы
        db: Сессия базы данных
        
    Returns:
        Конфигурация формы
        
    Raises:
        HTTPException: Если конфигурация не найдена
    """
    form_config = await FormConfigRepository.get_by_id(db, form_config_id)
    
    if not form_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Конфигурация формы с ID {form_config_id} не найдена"
        )
    
    return form_config


@router.put("/{form_config_id}", response_model=FormConfigResponse)
async def update_form_config(
    form_config_update: FormConfigUpdate,
    form_config_id: int = Path(..., description="ID конфигурации формы", ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Обновить конфигурацию формы (только для администраторов)
    
    Args:
        form_config_update: Данные для обновления конфигурации формы
        form_config_id: ID конфигурации формы
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Обновленная конфигурация формы
        
    Raises:
        HTTPException: Если конфигурация не найдена
    """
    updated_form_config = await FormConfigRepository.update(db, form_config_id, form_config_update)
    
    if not updated_form_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Конфигурация формы с ID {form_config_id} не найдена"
        )
    
    return updated_form_config


@router.delete("/{form_config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form_config(
    form_config_id: int = Path(..., description="ID конфигурации формы", ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Удалить конфигурацию формы (только для администраторов)
    
    Args:
        form_config_id: ID конфигурации формы
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Raises:
        HTTPException: Если конфигурация не найдена
    """
    success = await FormConfigRepository.delete(db, form_config_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Конфигурация формы с ID {form_config_id} не найдена"
        )


@router.post("/init", status_code=status.HTTP_200_OK)
async def initialize_form_configs(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Инициализировать дефолтные конфигурации форм (только для администраторов)
    
    Args:
        db: Сессия базы данных
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Сообщение об успешной инициализации
    """
    await FormConfigRepository.create_default_configs(db)
    
    return {"message": "Дефолтные конфигурации форм успешно созданы"} 