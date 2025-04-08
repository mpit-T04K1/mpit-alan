from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timedelta

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase

class BookingStatus(str, enum.Enum):
    """Статусы бронирования"""
    PENDING = "pending"       # Ожидает подтверждения
    CONFIRMED = "confirmed"   # Подтверждено
    COMPLETED = "completed"   # Завершено (услуга оказана)
    CANCELLED = "cancelled"   # Отменено
    RESCHEDULED = "rescheduled" # Перенесено на другое время

class PaymentStatus(str, enum.Enum):
    """Статусы оплаты"""
    PENDING = "pending"       # Ожидает оплаты
    COMPLETED = "completed"   # Оплачено
    CANCELLED = "cancelled"   # Отменено
    REFUNDED = "refunded"     # Возвращено
    FAILED = "failed"         # Ошибка оплаты

class Booking(SrcDbAdapterBase):
    """Модель бронирования"""
    __tablename__ = "bookings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с компанией, пользователем и услугой
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # Может быть null, если это кастомная услуга
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Связь с пользователем системы
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Сотрудник, оказывающий услугу
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=True)  # Связь с временным слотом
    
    # Информация о клиенте (для гостевых бронирований)
    client_name = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    
    # Информация о бронировании
    start_time = Column(DateTime, nullable=False)  # Время начала
    end_time = Column(DateTime, nullable=True)  # Время окончания
    duration = Column(Integer, nullable=True)  # Продолжительность в минутах
    
    # Информация о стоимости
    price = Column(Float, nullable=True)  # Цена услуги
    is_paid = Column(Boolean, default=False)  # Статус оплаты
    payment_id = Column(String, nullable=True)  # ID платежа в платежной системе
    payment_status = Column(String, default=PaymentStatus.PENDING.value)  # Статус оплаты
    
    # Дополнительная информация
    notes = Column(Text, nullable=True)  # Примечания к бронированию
    
    # Статус и метаданные
    status = Column(String, nullable=False, default=BookingStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими моделями
    company = relationship("Company", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    time_slot = relationship("TimeSlot", back_populates="bookings", foreign_keys=[time_slot_id])
    
    def __repr__(self):
        return f"<Booking {self.id}: {self.start_time}>" 