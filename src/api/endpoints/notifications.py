"""
Эндпоинты для системы уведомлений
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.services.auth_service import get_current_user
from src.repositories.notification import NotificationRepository
from src.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate
)

router = APIRouter(tags=["Уведомления"])


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    read: Optional[bool] = Query(None, description="Фильтр по статусу прочтения"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить уведомления текущего пользователя
    
    Args:
        read: Фильтр по статусу прочтения
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Список уведомлений
    """
    notification_repo = NotificationRepository(db)
    return await notification_repo.get_by_user(
        user_id=current_user.id,
        read=read,
        limit=limit,
        offset=offset
    )


@router.get("/count", response_model=int)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить количество непрочитанных уведомлений
    
    Args:
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Количество непрочитанных уведомлений
    """
    notification_repo = NotificationRepository(db)
    return await notification_repo.count_unread(user_id=current_user.id)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить уведомление по ID
    
    Args:
        notification_id: ID уведомления
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Информация об уведомлении
    """
    notification_repo = NotificationRepository(db)
    notification = await notification_repo.get_by_id(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Уведомление с ID {notification_id} не найдено"
        )
    
    # Проверяем, что уведомление принадлежит текущему пользователю
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на просмотр этого уведомления"
        )
    
    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Отметить уведомление как прочитанное
    
    Args:
        notification_id: ID уведомления
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Обновленное уведомление
    """
    notification_repo = NotificationRepository(db)
    notification = await notification_repo.get_by_id(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Уведомление с ID {notification_id} не найдено"
        )
    
    # Проверяем, что уведомление принадлежит текущему пользователю
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на изменение этого уведомления"
        )
    
    return await notification_repo.update(notification_id, {"read": True})


@router.put("/read-all", response_model=int)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Отметить все уведомления пользователя как прочитанные
    
    Args:
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Количество обновленных уведомлений
    """
    notification_repo = NotificationRepository(db)
    count = await notification_repo.mark_all_as_read(user_id=current_user.id)
    return count


@router.delete("/{notification_id}", response_model=NotificationResponse)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удалить уведомление
    
    Args:
        notification_id: ID уведомления
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Удаленное уведомление
    """
    notification_repo = NotificationRepository(db)
    notification = await notification_repo.get_by_id(notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Уведомление с ID {notification_id} не найдено"
        )
    
    # Проверяем, что уведомление принадлежит текущему пользователю
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление этого уведомления"
        )
    
    deleted = await notification_repo.delete(notification_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Уведомление с ID {notification_id} не найдено"
        )
    
    return notification 