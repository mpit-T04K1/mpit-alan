from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from src.database import get_db
from src.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, 
    TimeSlotCreate, TimeSlotUpdate, TimeSlotResponse,
    GenerateSlotsRequest, GenerateSlotsResponse
)
from src.services.schedule_service import ScheduleService
from src.services.auth_service import get_current_user
from src.models.user import User
from src.utils.permissions import check_company_permission

router = APIRouter()

# Эндпоинты для управления расписанием

@router.post("/schedules/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новое расписание для компании или услуги"""
    await check_company_permission(db, current_user, schedule.company_id)
    
    schedule_service = ScheduleService(db)
    return await schedule_service.create_schedule(schedule)

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить расписание по ID"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    return schedule

@router.get("/schedules/", response_model=List[ScheduleResponse])
async def list_schedules(
    company_id: int = Query(..., description="ID компании"),
    service_id: Optional[int] = Query(None, description="ID услуги (опционально)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список расписаний для компании или услуги"""
    await check_company_permission(db, current_user, company_id)
    
    schedule_service = ScheduleService(db)
    schedules = await schedule_service.list_schedules(company_id, service_id)
    return schedules

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить существующее расписание"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    return await schedule_service.update_schedule(schedule_id, schedule_update)

@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить расписание"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    await schedule_service.delete_schedule(schedule_id)
    return None

# Эндпоинты для управления временными слотами

@router.post("/slots/", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
async def create_timeslot(
    timeslot: TimeSlotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый временной слот в расписании"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(timeslot.schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    return await schedule_service.create_timeslot(timeslot)

@router.get("/slots/{slot_id}", response_model=TimeSlotResponse)
async def get_timeslot(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить временной слот по ID"""
    schedule_service = ScheduleService(db)
    timeslot = await schedule_service.get_timeslot(slot_id)
    
    if not timeslot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Временной слот не найден"
        )
    
    schedule = await schedule_service.get_schedule(timeslot.schedule_id)
    await check_company_permission(db, current_user, schedule.company_id)
    return timeslot

@router.get("/slots/", response_model=List[TimeSlotResponse])
async def list_timeslots(
    schedule_id: int = Query(..., description="ID расписания"),
    start_date: Optional[str] = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    is_available: Optional[bool] = Query(None, description="Фильтр по доступности"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список временных слотов для расписания"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    
    # Обработка параметров фильтрации дат
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат начальной даты. Ожидается YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            # Устанавливаем конец дня
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат конечной даты. Ожидается YYYY-MM-DD"
            )
    
    return await schedule_service.list_timeslots(
        schedule_id, 
        start_time=start_datetime, 
        end_time=end_datetime,
        is_available=is_available
    )

@router.put("/slots/{slot_id}", response_model=TimeSlotResponse)
async def update_timeslot(
    slot_id: int,
    timeslot_update: TimeSlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить существующий временной слот"""
    schedule_service = ScheduleService(db)
    timeslot = await schedule_service.get_timeslot(slot_id)
    
    if not timeslot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Временной слот не найден"
        )
    
    schedule = await schedule_service.get_schedule(timeslot.schedule_id)
    await check_company_permission(db, current_user, schedule.company_id)
    return await schedule_service.update_timeslot(slot_id, timeslot_update)

@router.delete("/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeslot(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить временной слот"""
    schedule_service = ScheduleService(db)
    timeslot = await schedule_service.get_timeslot(slot_id)
    
    if not timeslot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Временной слот не найден"
        )
    
    schedule = await schedule_service.get_schedule(timeslot.schedule_id)
    await check_company_permission(db, current_user, schedule.company_id)
    await schedule_service.delete_timeslot(slot_id)
    return None

# Эндпоинты для генерации временных слотов

@router.post("/slots/generate/", response_model=GenerateSlotsResponse)
async def generate_timeslots(
    request: GenerateSlotsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сгенерировать временные слоты на основе расписания"""
    schedule_service = ScheduleService(db)
    schedule = await schedule_service.get_schedule(request.schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Расписание не найдено"
        )
    
    await check_company_permission(db, current_user, schedule.company_id)
    
    try:
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD"
        )
    
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальная дата должна быть раньше или равна конечной дате"
        )
    
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Период генерации не может превышать 90 дней"
        )
    
    result = await schedule_service.generate_timeslots(
        request.schedule_id,
        start_date,
        end_date,
        request.override_existing
    )
    
    return GenerateSlotsResponse(
        success=True,
        message=f"Слоты успешно сгенерированы с {request.start_date} по {request.end_date}",
        slots_created=result["created"],
        slots_skipped=result["skipped"]
    ) 