from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field, validator

from src.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон пользователя")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия пользователя")
    role: UserRole = Field(UserRole.CLIENT, description="Роль пользователя")
    avatar: Optional[str] = Field(None, description="URL аватара")


class UserCreate(UserBase):
    """Схема создания пользователя"""
    password: str = Field(..., min_length=8, description="Пароль пользователя")
    password_confirm: str = Field(..., min_length=8, description="Подтверждение пароля")
    is_active: Optional[bool] = Field(True, description="Активен ли пользователь")
    is_superuser: Optional[bool] = Field(False, description="Является ли суперпользователем")
    
    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Пароли не совпадают")
        return v


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон пользователя")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия пользователя")
    avatar: Optional[str] = Field(None, description="URL аватара")
    role: Optional[str] = Field(None, description="Роль пользователя")
    is_active: Optional[bool] = Field(None, description="Активен ли пользователь")
    
    @validator("role")
    def validate_role(cls, v):
        if v is not None and v not in [role.value for role in UserRole]:
            raise ValueError(f"Недопустимая роль. Должна быть одна из: {', '.join([role.value for role in UserRole])}")
        return v


class UserInDB(UserBase):
    """Схема пользователя в базе данных"""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Расширенная схема пользователя с дополнительными данными"""
    companies: List[Dict[str, Any]] = []
    bookings: List[Dict[str, Any]] = []
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Схема запроса для входа"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")


class PasswordChange(BaseModel):
    """Схема изменения пароля"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    confirm_password: str = Field(..., description="Подтверждение нового пароля")
    
    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Пароли не совпадают")
        return v


class TokenData(BaseModel):
    """Схема данных токена"""
    user_id: str = Field(..., description="ID пользователя")


class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field("bearer", description="Тип токена") 