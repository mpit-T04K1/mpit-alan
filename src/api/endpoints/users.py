"""
Эндпоинты для работы с пользователями
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.db_adapter import get_db
from src.services.auth_service import get_current_user, get_current_admin_user
from src.models.user import UserRole
from src.repositories.user import UserRepository
from src.schemas.user import (
    UserResponse, 
    UserCreate, 
    UserUpdate,
    UserDetailResponse
)
from src.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserDetailResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о текущем пользователе
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        Информация о текущем пользователе
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию о текущем пользователе
    
    Args:
        user_data: Новые данные пользователя
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        Обновленная информация о пользователе
    """
    user_repo = UserRepository(db)
    
    # Проверка на дублирование email
    if user_data.email and user_data.email != current_user.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
    
    # Проверка на дублирование телефона
    if user_data.phone and user_data.phone != current_user.phone:
        existing_phone = await user_repo.get_by_phone(user_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким телефоном уже существует"
            )
    
    # Обычный пользователь не может сменить себе роль
    update_data = user_data.dict(exclude_unset=True)
    if "role" in update_data and update_data["role"] != current_user.role:
        if current_user.role != UserRole.ADMIN:
            # Только админ может менять роли
            update_data.pop("role")
    
    updated_user = await user_repo.update(current_user.id, update_data)
    return updated_user


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Получить список пользователей (только для админа)
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество записей
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Список пользователей
    """
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Получить информацию о пользователе по ID (только для админа)
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Информация о пользователе
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Обновить информацию о пользователе (только для админа)
    
    Args:
        user_id: ID пользователя
        user_data: Новые данные пользователя
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
        
    Returns:
        Обновленная информация о пользователе
    """
    user_repo = UserRepository(db)
    
    # Проверяем существование пользователя
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Проверка на дублирование email
    if user_data.email and user_data.email != user.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует"
            )
    
    # Проверка на дублирование телефона
    if user_data.phone and user_data.phone != user.phone:
        existing_phone = await user_repo.get_by_phone(user_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким телефоном уже существует"
            )
    
    update_data = user_data.dict(exclude_unset=True)
    updated_user = await user_repo.update(user_id, update_data)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Удалить пользователя (только для админа)
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        current_user: Текущий пользователь (администратор)
    """
    # Нельзя удалить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить собственный аккаунт"
        )
    
    user_repo = UserRepository(db)
    deleted = await user_repo.delete(user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        ) 