from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator


class ServiceBase(BaseModel):
    """Базовая схема услуги"""
    name: str = Field(..., min_length=1, max_length=255, description="Название услуги")
    description: Optional[str] = Field(None, description="Описание услуги")
    price: float = Field(0.0, ge=0, description="Стоимость услуги")
    duration: int = Field(60, ge=5, description="Длительность услуги в минутах")
    is_active: bool = Field(True, description="Активна ли услуга")
    category: Optional[str] = Field(None, max_length=100, description="Категория услуги")
    tags: Optional[str] = Field(None, max_length=255, description="Теги услуги")
    
    @validator("price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Цена не может быть отрицательной")
        return v
    
    @validator("duration")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Длительность должна быть положительной")
        return v


class ServiceCreate(ServiceBase):
    """Схема создания услуги"""
    company_id: int = Field(..., gt=0, description="ID компании")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Дополнительные параметры")

    class Config:
        from_attributes = True


class ServiceUpdate(BaseModel):
    """Схема обновления услуги"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название услуги")
    description: Optional[str] = Field(None, description="Описание услуги")
    price: Optional[float] = Field(None, ge=0, description="Стоимость услуги")
    duration: Optional[int] = Field(None, ge=5, description="Длительность услуги в минутах")
    is_active: Optional[bool] = Field(None, description="Активна ли услуга")
    category: Optional[str] = Field(None, max_length=100, description="Категория услуги")
    tags: Optional[str] = Field(None, max_length=255, description="Теги услуги")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Дополнительные параметры")
    
    @validator("price")
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Цена не может быть отрицательной")
        return v
    
    @validator("duration")
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Длительность должна быть положительной")
        return v


class ServiceInDB(ServiceBase):
    """Схема услуги в базе данных"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    additional_params: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ServiceResponse(ServiceInDB):
    """Схема ответа с данными услуги"""
    pass


class ServiceDetailResponse(ServiceResponse):
    """Расширенная схема услуги с дополнительными данными"""
    company_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    """Схема списка услуг с пагинацией"""
    items: List[ServiceResponse]
    total: int
    page: int
    size: int 