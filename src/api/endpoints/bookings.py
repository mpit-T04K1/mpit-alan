"""
Эндпоинты для работы с бронированиями
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.db_adapter import get_db
from src.services.auth_service import get_current_user, get_current_admin_user
from src.repositories.booking import BookingRepository
from src.repositories.service import ServiceRepository
from src.repositories.company import CompanyRepository
from src.schemas.booking import (
    BookingCreate, 
    BookingUpdate, 
    BookingResponse,
    BookingDetailResponse,
    BookingStatus
)

router = APIRouter(tags=["Бронирования"])


@router.post("", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создать новое бронирование
    
    Args:
        booking_data: Данные для создания бронирования
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Созданное бронирование
    """
    service_repo = ServiceRepository(db)
    booking_repo = BookingRepository(db)
    
    # Проверяем, существует ли услуга
    service = await service_repo.get_by_id(booking_data.service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Услуга с ID {booking_data.service_id} не найдена"
        )
    
    # Проверяем, доступно ли время для бронирования
    existing_bookings = await booking_repo.get_by_service_and_time(
        service_id=booking_data.service_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time
    )
    
    if existing_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Выбранное время уже занято"
        )
    
    # Создаем бронирование с указанием id пользователя
    booking_data_dict = booking_data.dict()
    booking_data_dict['user_id'] = current_user.id
    
    return await booking_repo.create(booking_data_dict)


@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    service_id: Optional[int] = Query(None, description="ID услуги"),
    company_id: Optional[int] = Query(None, description="ID компании"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата фильтрации"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата фильтрации"),
    status: Optional[BookingStatus] = Query(None, description="Статус бронирования"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить список бронирований с фильтрацией и пагинацией
    
    Args:
        service_id: ID услуги для фильтрации
        company_id: ID компании для фильтрации
        start_date: Начальная дата фильтрации
        end_date: Конечная дата фильтрации
        status: Статус бронирования для фильтрации
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Список бронирований
    """
    booking_repo = BookingRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем права доступа
    # Если пользователь не админ и не указан свой ID, то показываем только свои бронирования
    if current_user.role != "admin":
        # Если указана компания, проверяем, является ли пользователь ее владельцем
        if company_id:
            company = await company_repo.get_by_id(company_id)
            if not company or company.owner_id != current_user.id:
                # Ограничиваем выборку только бронированиями текущего пользователя
                return await booking_repo.get_by_user(
                    user_id=current_user.id,
                    service_id=service_id,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    limit=limit,
                    offset=offset
                )
    
    return await booking_repo.get_all(
        user_id=None,  # Для админа или владельца компании показываем все бронирования
        service_id=service_id,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    status: Optional[BookingStatus] = Query(None, description="Статус бронирования"),
    limit: int = Query(20, ge=1, le=100, description="Количество результатов на странице"),
    offset: int = Query(0, ge=0, description="Смещение от начала списка"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить список бронирований текущего пользователя
    
    Args:
        status: Статус бронирования для фильтрации
        limit: Ограничение количества результатов
        offset: Смещение от начала списка
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Список бронирований пользователя
    """
    booking_repo = BookingRepository(db)
    return await booking_repo.get_by_user(
        user_id=current_user.id,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(
    booking_id: int = Path(..., description="ID бронирования"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получить информацию о бронировании по ID
    
    Args:
        booking_id: ID бронирования
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Информация о бронировании
    """
    booking_repo = BookingRepository(db)
    booking = await booking_repo.get_by_id(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )
    
    # Проверяем права доступа
    if booking.user_id != current_user.id and current_user.role != "admin":
        # Проверяем, является ли пользователь владельцем компании
        service_repo = ServiceRepository(db)
        company_repo = CompanyRepository(db)
        
        service = await service_repo.get_by_id(booking.service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Услуга с ID {booking.service_id} не найдена"
            )
        
        company = await company_repo.get_by_id(service.company_id)
        if not company or company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на просмотр этого бронирования"
            )
    
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Обновить информацию о бронировании
    
    Args:
        booking_id: ID бронирования
        booking_data: Данные для обновления бронирования
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Обновленное бронирование
    """
    booking_repo = BookingRepository(db)
    service_repo = ServiceRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем существование бронирования
    booking = await booking_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )
    
    # Проверяем права доступа
    if booking.user_id != current_user.id and current_user.role != "admin":
        # Проверяем, является ли пользователь владельцем компании
        service = await service_repo.get_by_id(booking.service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Услуга с ID {booking.service_id} не найдена"
            )
        
        company = await company_repo.get_by_id(service.company_id)
        if not company or company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на изменение этого бронирования"
            )
    
    # Обновляем бронирование
    update_data = booking_data.dict(exclude_unset=True)
    return await booking_repo.update(booking_id, update_data)


@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Отменить бронирование
    
    Args:
        booking_id: ID бронирования
        db: Сессия базы данных
        current_user: Текущий пользователь
        
    Returns:
        Отмененное бронирование
    """
    booking_repo = BookingRepository(db)
    service_repo = ServiceRepository(db)
    company_repo = CompanyRepository(db)
    
    # Проверяем существование бронирования
    booking = await booking_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )
    
    # Проверяем права доступа
    is_owner = booking.user_id == current_user.id
    is_admin = current_user.role == "admin"
    is_company_owner = False
    
    if not is_owner and not is_admin:
        # Проверяем, является ли пользователь владельцем компании
        service = await service_repo.get_by_id(booking.service_id)
        if service:
            company = await company_repo.get_by_id(service.company_id)
            if company and company.owner_id == current_user.id:
                is_company_owner = True
        
        if not is_company_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на отмену этого бронирования"
            )
    
    # Пользователь может только отменить бронирование, а не удалить его физически
    if is_owner and not is_admin and not is_company_owner:
        # Обновляем статус бронирования на CANCELLED
        return await booking_repo.update(booking_id, {"status": BookingStatus.CANCELLED})
    
    # Админ или владелец компании может удалить бронирование физически
    deleted = await booking_repo.delete(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено"
        )
    
    return booking 