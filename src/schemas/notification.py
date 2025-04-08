"""
Схемы данных для уведомлений
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    """Базовая схема уведомления"""
    title: str = Field(..., description="Заголовок уведомления")
    content: str = Field(..., description="Содержание уведомления")
    notification_type: str = Field(default="system", description="Тип уведомления")


class NotificationCreate(NotificationBase):
    """Схема для создания уведомления"""
    user_id: int = Field(..., description="ID пользователя, которому предназначено уведомление")


class NotificationUpdate(BaseModel):
    """Схема для обновления уведомления"""
    title: Optional[str] = Field(None, description="Заголовок уведомления")
    content: Optional[str] = Field(None, description="Содержание уведомления")
    read: Optional[bool] = Field(None, description="Статус прочтения")


class NotificationResponse(NotificationBase):
    """Схема для ответа с уведомлением"""
    id: int = Field(..., description="ID уведомления")
    user_id: int = Field(..., description="ID пользователя")
    read: bool = Field(..., description="Прочитано ли уведомление")
    created_at: datetime = Field(..., description="Дата и время создания")
    
    class Config:
        from_attributes = True 