"""
Модель уведомлений
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Использую полный путь для импорта Base с алиасом
from src.db_adapter import Base as SrcDbAdapterBase


class Notification(SrcDbAdapterBase):
    """Модель уведомления для пользователя"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="system")
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>" 