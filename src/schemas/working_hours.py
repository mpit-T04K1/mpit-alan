from datetime import time
from typing import Optional

from pydantic import BaseModel, field_validator

from src.adapters.database.models.working_hours import DayOfWeek


class WorkingHoursBase(BaseModel):
    """Базовая схема рабочих часов"""
    day: str
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_working_day: bool = True
    
    @field_validator("day")
    def validate_day(cls, v):
        if v not in [day.value for day in DayOfWeek]:
            raise ValueError(f"Invalid day. Must be one of: {', '.join([day.value for day in DayOfWeek])}")
        return v
    
    @field_validator("open_time", "close_time")
    def validate_time(cls, v, values):
        # Если это рабочий день, время должно быть указано
        if "is_working_day" in values and values["is_working_day"] and v is None:
            raise ValueError("Time must be specified for working days")
        return v


class WorkingHoursCreate(WorkingHoursBase):
    """Схема создания рабочих часов"""
    pass


class WorkingHoursUpdate(BaseModel):
    """Схема обновления рабочих часов"""
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_working_day: Optional[bool] = None


class WorkingHoursInDB(WorkingHoursBase):
    """Схема рабочих часов из БД"""
    id: int
    company_id: int
    
    class Config:
        orm_mode = True


class WorkingHoursResponse(WorkingHoursBase):
    """Схема ответа с данными рабочих часов"""
    id: int
    company_id: int
    
    class Config:
        orm_mode = True 