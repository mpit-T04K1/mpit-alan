# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.user import User, UserRole

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship

from src.db_adapter import Base


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    BUSINESS = "business"
    CLIENT = "client"
    MODERATOR = "moderator"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    profile_picture = Column(String, nullable=True)
    
    # Отношения
    companies = relationship("Company", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>" 