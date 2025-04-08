from datetime import datetime, timedelta
import enum
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import func

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase

class ScheduleType(str, enum.Enum):
    """Тип расписания"""
    REGULAR = "regular"     # Регулярное расписание
    CUSTOM = "custom"       # Индивидуальное расписание
    HOLIDAY = "holiday"     # Расписание выходных дней
    VACATION = "vacation"   # Расписание отпусков


class TimeSlotStatus(str, enum.Enum):
    """Статус временного слота"""
    AVAILABLE = "available"         # Доступен для бронирования
    PARTIALLY_BOOKED = "partially_booked"  # Частично забронирован
    BOOKED = "booked"               # Полностью забронирован
    BLOCKED = "blocked"             # Заблокирован (недоступен для бронирования)


class Schedule(SrcDbAdapterBase):
    """Модель расписания"""
    __tablename__ = "schedules"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default=ScheduleType.REGULAR.value)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связи
    company = relationship("Company", back_populates="schedules")
    service = relationship("Service", back_populates="schedules")
    time_slots = relationship("TimeSlot", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Schedule {self.name} ({self.id})>"


class TimeSlot(SrcDbAdapterBase):
    """Модель временного слота для бронирования"""
    __tablename__ = "time_slots"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    max_clients = Column(Integer, default=1, nullable=False)  # Максимальное количество клиентов
    booked_clients = Column(Integer, default=0, nullable=False)  # Текущее количество забронированных клиентов
    price = Column(Float, nullable=True)  # Цена в этом временном слоте (может отличаться от цены услуги)
    status = Column(String, default=TimeSlotStatus.AVAILABLE.value, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    # Связи
    schedule = relationship("Schedule", back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TimeSlot {self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')} ({self.status})>"

    @property
    def available_spots(self) -> int:
        """Возвращает количество доступных мест в слоте"""
        return max(0, self.max_clients - self.booked_clients)


# Добавим отношения в существующие модели
from src.models.company import Company
from src.models.service import Service
from src.models.booking import Booking

# Эти отношения должны быть добавлены в соответствующие модели
Company.schedules = relationship("Schedule", back_populates="company", cascade="all, delete-orphan")
Service.schedules = relationship("Schedule", back_populates="service", cascade="all, delete-orphan")
Booking.time_slot = relationship("TimeSlot", back_populates="bookings") 