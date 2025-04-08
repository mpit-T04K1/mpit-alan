from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase

class Service(SrcDbAdapterBase):
    """Модель для хранения услуг компаний"""
    __tablename__ = "services"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0.0)
    duration = Column(Integer, default=60)  # продолжительность в минутах
    is_active = Column(Boolean, default=True)
    
    # Доп. информация (может быть использована для расширения)
    category = Column(String(100), nullable=True)
    tags = Column(String(255), nullable=True)
    
    # Даты создания и обновления
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими таблицами
    company = relationship("Company", back_populates="services")
    bookings = relationship("Booking", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Service {self.id}: {self.name}>" 