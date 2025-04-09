# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.service import Service

# Класс Service теперь импортируется напрямую из src/models/service.py
# и переэкспортируется здесь для обратной совместимости

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship

from src.db_adapter import Base


class Service(Base):
    """Модель услуги"""
    __tablename__ = "services"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # в минутах
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Дополнительные параметры услуги (зависит от типа бизнеса)
    additional_params = Column(JSON, nullable=True)
    
    # Отношения
    company = relationship("Company", back_populates="services")
    bookings = relationship("Booking", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Service {self.name} ({self.company_id})>" 