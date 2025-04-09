from datetime import datetime, time
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator, Field

# Схемы для работы с расписанием

class WeeklyScheduleItem(BaseModel):
    """Схема для одного дня недели в расписании"""
    start: str
    end: str
    is_working_day: bool = True

    @validator('start', 'end')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('Время должно быть в формате HH:MM')
        return v

class ExceptionScheduleItem(BaseModel):
    """Схема для исключения (особого дня) в расписании"""
    date: str
    start: Optional[str] = None
    end: Optional[str] = None
    is_working_day: bool = True

    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Дата должна быть в формате YYYY-MM-DD')
        return v

    @validator('start', 'end')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%H:%M')
            except ValueError:
                raise ValueError('Время должно быть в формате HH:MM')
        return v

class RecurringEventItem(BaseModel):
    """Схема для повторяющегося события в расписании"""
    name: str
    start_time: str
    end_time: str
    days: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_working_time: bool = False

    @validator('days')
    def validate_days(cls, v):
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in v:
            if day not in valid_days:
                raise ValueError(f"Некорректный день недели: {day}")
        return v

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError('Время должно быть в формате HH:MM')
        return v

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Дата должна быть в формате YYYY-MM-DD')
        return v

class ScheduleBase(BaseModel):
    """Базовая схема для расписания"""
    company_id: int
    service_id: Optional[int] = None
    schedule_type: str = "service"
    name: str
    weekly_schedule: Dict[str, WeeklyScheduleItem]
    exceptions: Optional[List[ExceptionScheduleItem]] = None
    recurring_events: Optional[List[RecurringEventItem]] = None
    slot_duration: int = 60
    slot_interval: int = 0
    max_concurrent_bookings: int = 1
    is_active: bool = True

class ScheduleCreate(ScheduleBase):
    """Схема для создания расписания"""
    pass

class ScheduleUpdate(BaseModel):
    """Схема для обновления расписания"""
    service_id: Optional[int] = None
    schedule_type: Optional[str] = None
    name: Optional[str] = None
    weekly_schedule: Optional[Dict[str, WeeklyScheduleItem]] = None
    exceptions: Optional[List[ExceptionScheduleItem]] = None
    recurring_events: Optional[List[RecurringEventItem]] = None
    slot_duration: Optional[int] = None
    slot_interval: Optional[int] = None
    max_concurrent_bookings: Optional[int] = None
    is_active: Optional[bool] = None

class ScheduleInDB(ScheduleBase):
    """Схема для расписания из БД"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleResponse(ScheduleInDB):
    """Схема ответа с данными расписания"""
    pass

# Схемы для работы с временными слотами

class TimeSlotBase(BaseModel):
    """Базовая схема для временного слота"""
    schedule_id: int
    start_time: datetime
    end_time: datetime
    max_bookings: int = 1
    is_available: bool = True
    special_conditions: Optional[Dict[str, Any]] = None

class TimeSlotCreate(TimeSlotBase):
    """Схема для создания временного слота"""
    pass

class TimeSlotUpdate(BaseModel):
    """Схема для обновления временного слота"""
    max_bookings: Optional[int] = None
    is_available: Optional[bool] = None
    special_conditions: Optional[Dict[str, Any]] = None

class TimeSlotInDB(TimeSlotBase):
    """Схема для временного слота из БД"""
    id: int
    current_bookings: int = 0

    class Config:
        orm_mode = True

class TimeSlotResponse(TimeSlotInDB):
    """Схема ответа с данными временного слота"""
    available_spots: int = Field(..., description="Количество доступных мест")

    @validator('available_spots', pre=True, always=True)
    def calculate_available_spots(cls, v, values):
        max_bookings = values.get('max_bookings', 0)
        current_bookings = values.get('current_bookings', 0)
        return max(0, max_bookings - current_bookings)

# Схемы для генерации временных слотов

class GenerateSlotsRequest(BaseModel):
    """Схема запроса на генерацию временных слотов"""
    schedule_id: int
    start_date: str
    end_date: str
    override_existing: bool = False

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Дата должна быть в формате YYYY-MM-DD')
        return v

class GenerateSlotsResponse(BaseModel):
    """Схема ответа на генерацию временных слотов"""
    success: bool
    message: str
    slots_created: int
    slots_skipped: int 