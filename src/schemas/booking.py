from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator

from src.models.booking import BookingStatus


class BookingBase(BaseModel):
    """Базовая схема бронирования"""
    start_time: datetime = Field(..., description="Время начала")
    notes: Optional[str] = Field(None, description="Примечания к бронированию")


class BookingCreate(BookingBase):
    """Схема создания бронирования"""
    company_id: int = Field(..., gt=0, description="ID компании")
    service_id: Optional[int] = Field(None, description="ID услуги")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    staff_id: Optional[int] = Field(None, description="ID сотрудника")
    
    # Необязательные поля для гостевого бронирования
    client_name: Optional[str] = Field(None, description="Имя клиента")
    client_phone: Optional[str] = Field(None, description="Телефон клиента")
    client_email: Optional[str] = Field(None, description="Email клиента")
    
    # Поля для определения длительности и стоимости
    duration: Optional[int] = Field(None, gt=0, description="Длительность в минутах")
    price: Optional[float] = Field(None, ge=0, description="Цена услуги")


class BookingUpdate(BaseModel):
    """Схема обновления бронирования"""
    start_time: Optional[datetime] = Field(None, description="Время начала")
    end_time: Optional[datetime] = Field(None, description="Время окончания")
    duration: Optional[int] = Field(None, gt=0, description="Длительность в минутах")
    staff_id: Optional[int] = Field(None, description="ID сотрудника")
    status: Optional[str] = Field(None, description="Статус бронирования")
    is_paid: Optional[bool] = Field(None, description="Статус оплаты")
    payment_id: Optional[str] = Field(None, description="ID платежа")
    notes: Optional[str] = Field(None, description="Примечания к бронированию")
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in BookingStatus]:
            raise ValueError(f"Недопустимый статус. Должен быть одним из: {', '.join([status.value for status in BookingStatus])}")
        return v


class BookingStatusUpdate(BaseModel):
    """Схема обновления статуса бронирования"""
    status: str = Field(..., description="Статус бронирования")
    
    @validator("status")
    def validate_status(cls, v):
        if v not in [status.value for status in BookingStatus]:
            raise ValueError(f"Недопустимый статус. Должен быть одним из: {', '.join([status.value for status in BookingStatus])}")
        return v


class BookingPaymentUpdate(BaseModel):
    """Схема обновления статуса оплаты бронирования"""
    is_paid: bool = Field(..., description="Статус оплаты")
    payment_id: Optional[str] = Field(None, description="ID платежа")


class BookingInDB(BookingBase):
    """Схема бронирования из БД"""
    id: int
    company_id: int
    service_id: Optional[int] = None
    user_id: Optional[int] = None
    staff_id: Optional[int] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    price: Optional[float] = None
    is_paid: bool = False
    payment_id: Optional[str] = None
    status: str = BookingStatus.PENDING.value
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingResponse(BookingBase):
    """Схема ответа с данными бронирования"""
    id: int
    company_id: int
    service_id: Optional[int] = None
    user_id: Optional[int] = None
    staff_id: Optional[int] = None
    end_time: Optional[datetime] = None
    status: str
    is_paid: bool
    price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingDetailResponse(BookingResponse):
    """Расширенная схема бронирования с дополнительными данными"""
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    service_name: Optional[str] = None
    company_name: Optional[str] = None
    duration: Optional[int] = None
    payment_id: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingTimeSlot(BaseModel):
    """Схема временного слота для бронирования"""
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    staff_id: Optional[int] = None
    staff_name: Optional[str] = None


class BookingFilterParams(BaseModel):
    """Параметры фильтрации для поиска бронирований"""
    start_date: Optional[datetime] = Field(None, description="Начальная дата для поиска")
    end_date: Optional[datetime] = Field(None, description="Конечная дата для поиска")
    status: Optional[str] = Field(None, description="Статус бронирования")
    company_id: Optional[int] = Field(None, description="ID компании")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    staff_id: Optional[int] = Field(None, description="ID сотрудника")
    is_paid: Optional[bool] = Field(None, description="Статус оплаты") 