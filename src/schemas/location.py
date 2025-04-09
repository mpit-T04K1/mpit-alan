from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Базовая схема локации"""
    address: str
    city: str
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Россия"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    additional_info: Optional[str] = None


class LocationCreate(LocationBase):
    """Схема создания локации"""
    pass


class LocationUpdate(BaseModel):
    """Схема обновления локации"""
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    additional_info: Optional[str] = None


class LocationInDB(LocationBase):
    """Схема локации из БД"""
    id: int
    company_id: int
    
    class Config:
        orm_mode = True


class LocationResponse(LocationBase):
    """Схема ответа с данными локации"""
    id: int
    company_id: int
    
    class Config:
        orm_mode = True 