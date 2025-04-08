from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import logging
from typing import Optional, List, Set

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase

# Настройка логирования
logger = logging.getLogger(__name__)

class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"             # Администратор системы
    COMPANY_OWNER = "owner"     # Владелец компании
    MANAGER = "manager"         # Менеджер
    EMPLOYEE = "employee"       # Сотрудник
    CLIENT = "client"           # Клиент
    USER = "user"  # Обычный пользователь
    BUSINESS = "business"  # Владелец бизнеса

    def __new__(cls, value):
        # Для поддержки преобразования из строкового значения (из базы данных)
        if isinstance(value, str):
            # Если значение совпадает с одним из определенных значений
            for member in cls:
                if member.value == value:
                    return member
            
            # Проверяем регистронезависимое совпадение
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    logger.info(f"Сопоставлено значение '{value}' с ролью {member} по регистронезависимому совпадению")
                    return member
        
        # Создаем новый объект, если это не строка или не найдено совпадение
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
    
    @classmethod
    def _missing_(cls, value):
        """Обработка отсутствующих значений перечисления"""
        logger.debug(f"Обработка неизвестного значения роли: '{value}' типа {type(value)}")
        
        if isinstance(value, str):
            # Более подробный отладочный вывод
            logger.debug(f"Попытка сопоставить '{value}' с одним из: {[m.value for m in cls]}")
            
            # Проверка точного совпадения без учета регистра
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    logger.info(f"Сопоставлено значение '{value}' с ролью {member} по регистронезависимому совпадению")
                    return member
            
            # Проверка на частичное совпадение
            for member in cls:
                if member.value.lower() in value_lower or value_lower in member.value.lower():
                    logger.info(f"Частичное совпадение: '{value}' с ролью {member}")
                    return member
        
        # Если строковое значение 'admin', возвращаем ADMIN
        if value == 'admin':
            return cls.ADMIN
            
        # Если не найдено, возвращаем значение по умолчанию
        logger.warning(f"Неизвестное значение роли '{value}', используем CLIENT")
        return cls.CLIENT


class User(SrcDbAdapterBase):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    avatar = Column(String, nullable=True, default=None)
    is_active = Column(Boolean, default=True)
    # Используем String с конвертером типов вместо Enum для избежания проблем с регистром
    role = Column(String, default="client", nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Telegram интеграция
    telegram_id = Column(String(50), nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    
    # Отношения
    companies = relationship("Company", back_populates="owner", 
                             foreign_keys="Company.owner_id", 
                             cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", 
                           foreign_keys="Booking.user_id",
                           cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"User(id={self.id}, email={self.email}, role={self.role})"
    
    def __repr__(self):
        return self.__str__() 