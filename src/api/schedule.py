from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from src.db.database import get_db
from src.models.schedule import Schedule, TimeSlot
from src.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleOut, 
    TimeSlotCreate, TimeSlotUpdate, TimeSlotOut,
    WeekSchedule, ScheduleTemplate
)
from src.repositories.schedule_repository import ScheduleRepository, TimeSlotRepository
from src.services.company_service import CompanyService

router = APIRouter(prefix="/schedule", tags=["schedule"])


# API для управления расписанием
@router.post("/company/{company_id}/schedule", response_model=ScheduleOut)
def create_company_schedule(
    company_id: int,
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Создание расписания для компании"""
    # Проверяем, существует ли компания
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Создаем расписание
    schedule_data.company_id = company_id
    db_schedule = ScheduleRepository.create_schedule(db, schedule_data)
    
    return db_schedule


@router.get("/company/{company_id}/schedule", response_model=List[ScheduleOut])
def get_company_schedules(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Получение всех расписаний компании"""
    # Проверяем, существует ли компания
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Получаем расписания
    schedules = ScheduleRepository.get_company_schedules(db, company_id)
    
    return schedules


@router.get("/company/{company_id}/week-schedule", response_model=WeekSchedule)
def get_company_week_schedule(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Получение стандартного расписания компании на неделю"""
    # Проверяем, существует ли компания
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Получаем расписание на неделю
    schedule_dict = ScheduleRepository.get_company_week_schedule(db, company_id)
    
    # Преобразуем словарь в список для вывода
    schedules = list(schedule_dict.values())
    
    return WeekSchedule(company_id=company_id, schedules=schedules)


@router.get("/company/{company_id}/special-days", response_model=List[ScheduleOut])
def get_company_special_days(
    company_id: int,
    start_date: str = Query(..., description="Начальная дата в формате YYYY-MM-DD"),
    end_date: str = Query(..., description="Конечная дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Получение особых дней для компании в заданном диапазоне дат"""
    # Проверяем, существует ли компания
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Преобразуем строки дат в объекты datetime
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Получаем особые дни
    special_days = ScheduleRepository.get_company_special_day_schedules(
        db, company_id, start_datetime, end_datetime
    )
    
    return special_days


@router.get("/company/{company_id}/schedule/date/{date}", response_model=ScheduleOut)
def get_schedule_for_date(
    company_id: int,
    date: str,
    db: Session = Depends(get_db)
):
    """Получение расписания компании на конкретную дату"""
    # Проверяем, существует ли компания
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    
    # Преобразуем строку даты в объект datetime
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Получаем расписание на указанную дату
    schedule = ScheduleRepository.get_schedule_for_date(db, company_id, date_obj)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание на указанную дату не найдено")
    
    return schedule


@router.get("/schedule/{schedule_id}", response_model=ScheduleOut)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Получение расписания по ID"""
    schedule = ScheduleRepository.get_schedule_by_id(db, schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    return schedule


@router.put("/schedule/{schedule_id}", response_model=ScheduleOut)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Обновление расписания"""
    updated_schedule = ScheduleRepository.update_schedule(db, schedule_id, schedule_data)
    
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    return updated_schedule


@router.delete("/schedule/{schedule_id}", response_model=dict)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Удаление расписания"""
    success = ScheduleRepository.delete_schedule(db, schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    return {"message": "Расписание успешно удалено"}


# API для управления временными слотами
@router.post("/service/{service_id}/timeslot", response_model=TimeSlotOut)
def create_time_slot(
    service_id: int,
    slot_data: TimeSlotCreate,
    db: Session = Depends(get_db)
):
    """Создание временного слота для услуги"""
    # Устанавливаем service_id из пути
    slot_data.service_id = service_id
    
    # Создаем временной слот
    db_time_slot = TimeSlotRepository.create_time_slot(db, slot_data)
    
    return db_time_slot


@router.get("/service/{service_id}/timeslots", response_model=List[TimeSlotOut])
def get_service_time_slots(
    service_id: int,
    start_date: Optional[str] = Query(None, description="Начальная дата в формате YYYY-MM-DD HH:MM"),
    end_date: Optional[str] = Query(None, description="Конечная дата в формате YYYY-MM-DD HH:MM"),
    db: Session = Depends(get_db)
):
    """Получение временных слотов для услуги"""
    # Преобразуем строки дат в объекты datetime, если они переданы
    start_datetime = None
    end_datetime = None
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат начальной даты")
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат конечной даты")
    
    # Получаем временные слоты
    time_slots = TimeSlotRepository.get_service_time_slots(
        db, service_id, start_datetime, end_datetime
    )
    
    return time_slots


@router.get("/service/{service_id}/available-timeslots", response_model=List[TimeSlotOut])
def get_available_time_slots(
    service_id: int,
    start_date: str = Query(..., description="Начальная дата в формате YYYY-MM-DD HH:MM"),
    end_date: str = Query(..., description="Конечная дата в формате YYYY-MM-DD HH:MM"),
    db: Session = Depends(get_db)
):
    """Получение доступных для бронирования временных слотов"""
    # Преобразуем строки дат в объекты datetime
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Получаем доступные временные слоты
    time_slots = TimeSlotRepository.get_available_time_slots(
        db, service_id, start_datetime, end_datetime
    )
    
    return time_slots


@router.get("/timeslot/{slot_id}", response_model=TimeSlotOut)
def get_time_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Получение временного слота по ID"""
    time_slot = TimeSlotRepository.get_time_slot_by_id(db, slot_id)
    
    if not time_slot:
        raise HTTPException(status_code=404, detail="Временной слот не найден")
    
    return time_slot


@router.put("/timeslot/{slot_id}", response_model=TimeSlotOut)
def update_time_slot(
    slot_id: int,
    slot_data: TimeSlotUpdate,
    db: Session = Depends(get_db)
):
    """Обновление временного слота"""
    updated_slot = TimeSlotRepository.update_time_slot(db, slot_id, slot_data)
    
    if not updated_slot:
        raise HTTPException(status_code=404, detail="Временной слот не найден")
    
    return updated_slot


@router.delete("/timeslot/{slot_id}", response_model=dict)
def delete_time_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Удаление временного слота"""
    success = TimeSlotRepository.delete_time_slot(db, slot_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Временной слот не найден")
    
    return {"message": "Временной слот успешно удален"}


@router.post("/timeslot/{slot_id}/book", response_model=TimeSlotOut)
def book_time_slot(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Бронирование временного слота"""
    booked_slot = TimeSlotRepository.book_time_slot(db, slot_id)
    
    if not booked_slot:
        raise HTTPException(status_code=400, detail="Невозможно забронировать слот")
    
    return booked_slot


@router.post("/timeslot/{slot_id}/cancel", response_model=TimeSlotOut)
def cancel_booking(
    slot_id: int,
    db: Session = Depends(get_db)
):
    """Отмена бронирования временного слота"""
    cancelled_slot = TimeSlotRepository.cancel_booking(db, slot_id)
    
    if not cancelled_slot:
        raise HTTPException(status_code=400, detail="Невозможно отменить бронирование")
    
    return cancelled_slot


@router.post("/service/{service_id}/generate-timeslots", response_model=List[TimeSlotOut])
def generate_time_slots(
    service_id: int,
    start_date: str = Query(..., description="Начальная дата и время в формате YYYY-MM-DD HH:MM"),
    end_date: str = Query(..., description="Конечная дата и время в формате YYYY-MM-DD HH:MM"),
    duration: int = Query(..., ge=5, le=480, description="Продолжительность слота в минутах"),
    interval: int = Query(..., ge=5, le=480, description="Интервал между слотами в минутах"),
    max_clients: int = Query(1, ge=1, description="Максимальное количество клиентов на слот"),
    db: Session = Depends(get_db)
):
    """Генерация временных слотов для услуги на указанный период"""
    # Преобразуем строки дат в объекты datetime
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Генерируем временные слоты
    time_slots = TimeSlotRepository.generate_time_slots(
        db, service_id, start_datetime, end_datetime, duration, interval, max_clients
    )
    
    return time_slots


@router.post("/service/{service_id}/generate-from-schedule", response_model=List[TimeSlotOut])
def generate_slots_from_schedule(
    service_id: int,
    company_id: int = Query(..., description="ID компании"),
    start_date: str = Query(..., description="Начальная дата в формате YYYY-MM-DD"),
    end_date: str = Query(..., description="Конечная дата в формате YYYY-MM-DD"),
    duration: int = Query(..., ge=5, le=480, description="Продолжительность слота в минутах"),
    interval: int = Query(..., ge=5, le=480, description="Интервал между слотами в минутах"),
    max_clients: int = Query(1, ge=1, description="Максимальное количество клиентов на слот"),
    db: Session = Depends(get_db)
):
    """Генерация временных слотов на основе расписания компании"""
    # Преобразуем строки дат в объекты datetime
    try:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    # Получаем расписание компании на неделю
    schedules = ScheduleRepository.get_company_week_schedule(db, company_id)
    
    # Получаем особые дни в заданном диапазоне дат
    special_days = ScheduleRepository.get_company_special_day_schedules(
        db, company_id, start_datetime, end_datetime
    )
    
    # Генерируем временные слоты на основе расписания
    time_slots = TimeSlotRepository.generate_slots_from_schedule(
        db, service_id, schedules, special_days, 
        start_datetime, end_datetime, duration, interval, max_clients
    )
    
    return time_slots 