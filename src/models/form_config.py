from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase

class FormConfig(SrcDbAdapterBase):
    """Модель для хранения конфигураций динамических форм"""
    __tablename__ = "form_configs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    business_type = Column(String(50), nullable=False, index=True)
    form_type = Column(String(50), nullable=False, index=True)  # registration, services, booking
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # JSON-конфигурация формы
    config = Column(JSON, nullable=False)
    
    # Флаг активности конфигурации
    is_active = Column(Boolean, default=True)
    
    # Версионирование конфигурации
    version = Column(Integer, default=1, nullable=False)
    
    # Даты создания и обновления
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FormConfig {self.id}: {self.business_type}/{self.form_type} v{self.version}>" 