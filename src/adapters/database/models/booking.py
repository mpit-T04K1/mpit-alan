# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.booking import Booking, BookingStatus, PaymentStatus

# Класс Booking и другие теперь импортируются напрямую из src/models/booking.py
# и переэкспортируются здесь для обратной совместимости

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from src.db_adapter import Base


class BookingStatus(str, Enum):
    """Статусы бронирования"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Статусы оплаты"""
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class Booking(Base):
    """Модель бронирования"""
    __tablename__ = "bookings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    booking_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default=BookingStatus.PENDING.value, nullable=False)
    payment_status = Column(String, default=PaymentStatus.PENDING.value, nullable=False)
    amount = Column(Float, nullable=True)
    customer_notes = Column(Text, nullable=True)
    business_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Отношения
    client = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking {self.id} ({self.status})>" 