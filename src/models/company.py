from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

# Использую полный путь для импорта Base
from src.db_adapter import Base as SrcDbAdapterBase

class Company(SrcDbAdapterBase):
    """Модель компании"""
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    business_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Владелец компании
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Контактная информация
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON строка
    city = Column(String(100), nullable=True)
    
    # Визуальные элементы
    logo_url = Column(String(255), nullable=True)
    cover_image_url = Column(String(255), nullable=True)
    
    # Статус и время создания/обновления
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Добавляем поле для хранения метаданных (в том числе рабочих часов)
    company_metadata = Column(JSON, nullable=True)
    
    # Статус модерации
    moderation_status = Column(String(20), default="pending")  # pending, approved, rejected
    moderation_comment = Column(Text, nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    moderated_by_id = Column("moderated_by", Integer, ForeignKey("users.id"), nullable=True)
    
    # Рейтинг
    rating = Column(Float, default=0.0)
    ratings_count = Column(Integer, default=0)
    
    # Связи с другими таблицами
    locations = relationship("Location", back_populates="company", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="company", cascade="all, delete-orphan")
    working_hours = relationship("WorkingHours", back_populates="company", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="company", cascade="all, delete-orphan")
    moderation_records = relationship("ModerationRecord", back_populates="company", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="company", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="companies", foreign_keys=[owner_id])
    moderator = relationship("User", foreign_keys=[moderated_by_id])
    schedules = relationship("Schedule", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company {self.name}>" 