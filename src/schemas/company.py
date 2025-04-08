from pydantic import BaseModel, Field, EmailStr, validator, HttpUrl
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

# Базовые схемы для локаций

class LocationBase(BaseModel):
    """Базовая схема для локации"""
    name: str = Field(..., min_length=1, max_length=255, description="Название локации")
    address: str = Field(..., min_length=5, max_length=255, description="Адрес локации")
    city: str = Field(..., min_length=2, max_length=100, description="Город")
    postal_code: Optional[str] = Field(None, max_length=20, description="Почтовый индекс")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Контактный телефон")
    contact_email: Optional[EmailStr] = Field(None, description="Контактный email")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")


class LocationCreate(LocationBase):
    """Схема для создания локации"""
    company_id: int = Field(..., gt=0, description="ID компании")
    
    class Config:
        from_attributes = True


class LocationUpdate(BaseModel):
    """Схема для обновления локации"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название локации")
    address: Optional[str] = Field(None, min_length=5, max_length=255, description="Адрес локации")
    city: Optional[str] = Field(None, min_length=2, max_length=100, description="Город")
    postal_code: Optional[str] = Field(None, max_length=20, description="Почтовый индекс")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Контактный телефон")
    contact_email: Optional[EmailStr] = Field(None, description="Контактный email")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")
    is_active: Optional[bool] = Field(None, description="Активна ли локация")


class LocationInDB(LocationBase):
    """Схема для локации в базе данных"""
    id: int
    company_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationResponse(LocationInDB):
    """Схема для ответа с локацией"""
    pass


# Базовые схемы для компаний

class CompanyBase(BaseModel):
    """Базовая схема для компании"""
    name: str = Field(..., min_length=1, max_length=255, description="Название компании")
    business_type: str = Field(..., min_length=1, max_length=50, description="Тип бизнеса")
    description: Optional[str] = Field(None, description="Описание компании")
    contact_name: Optional[str] = Field(None, description="Контактное лицо")
    contact_email: EmailStr = Field(..., description="Контактный email")
    contact_phone: str = Field(..., min_length=5, max_length=20, description="Контактный телефон")
    website: Optional[str] = Field(None, description="Веб-сайт компании")
    social_links: Optional[Union[Dict[str, str], str]] = Field(None, description="Социальные сети")
    city: Optional[str] = Field(None, description="Город")

    @validator('website', pre=True)
    def validate_website(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str) and v.startswith('http'):
            return v
        raise ValueError('Неверный формат URL. Должен начинаться с http:// или https://')


class CompanyCreate(CompanyBase):
    """Схема для создания компании"""
    owner_id: Optional[int] = Field(None, description="ID владельца компании")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    cover_image_url: Optional[str] = Field(None, description="URL обложки")
    company_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные компании")
    is_active: Optional[bool] = Field(True, description="Активна ли компания")

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    """Схема для обновления компании"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название компании")
    business_type: Optional[str] = Field(None, min_length=1, max_length=50, description="Тип бизнеса")
    description: Optional[str] = Field(None, description="Описание компании")
    contact_name: Optional[str] = Field(None, description="Контактное лицо")
    contact_email: Optional[EmailStr] = Field(None, description="Контактный email")
    contact_phone: Optional[str] = Field(None, min_length=5, max_length=20, description="Контактный телефон")
    website: Optional[str] = Field(None, description="Веб-сайт компании")
    social_links: Optional[Union[Dict[str, str], str]] = Field(None, description="Социальные сети")
    city: Optional[str] = Field(None, description="Город")
    logo_url: Optional[str] = Field(None, description="URL логотипа")
    cover_image_url: Optional[str] = Field(None, description="URL обложки")
    company_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные компании")
    is_active: Optional[bool] = Field(None, description="Активна ли компания")


class CompanyInDB(CompanyBase):
    """Схема для компании в базе данных"""
    id: int
    owner_id: Optional[int] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    company_metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True
    moderation_status: str = "pending"
    moderation_comment: Optional[str] = None
    rating: float = 0.0
    ratings_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyResponse(CompanyInDB):
    """Схема для ответа с основной информацией о компании"""
    pass


class CompanyDetailResponse(CompanyResponse):
    """Схема для детального ответа с информацией о компании"""
    locations: List[LocationResponse] = []
    working_hours: List[Dict[str, Any]] = []


class CompanyRegistration(BaseModel):
    """Схема для регистрации компании с учетными данными пользователя"""
    company: CompanyCreate
    location: Optional[LocationCreate] = None


class CompanyModerationUpdate(BaseModel):
    """Схема для обновления статуса модерации компании"""
    moderation_status: str = Field(..., description="Статус модерации: pending, approved, rejected")
    moderation_comment: Optional[str] = Field(None, description="Комментарий модератора") 