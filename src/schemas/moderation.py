from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ModerationStatusEnum:
    """Статусы модерации"""
    PENDING = "на рассмотрении"
    APPROVED = "одобрено"
    REJECTED = "отклонено"
    NEEDS_REVISION = "требует доработки"


class ModerationRecordBase(BaseModel):
    """Базовая схема записи модерации"""
    status: str = Field(default=ModerationStatusEnum.PENDING)
    moderation_notes: Optional[str] = None

    @field_validator("status")
    def validate_status(cls, v):
        if v not in [status for status in vars(ModerationStatusEnum).values() if not status.startswith("_")]:
            raise ValueError(f"Некорректный статус модерации. Допустимые значения: {', '.join([s for s in vars(ModerationStatusEnum).values() if not s.startswith('_')])}")
        return v


class ModerationRecordCreate(BaseModel):
    """Схема создания записи модерации"""
    company_id: int
    auto_check_passed: bool = False


class ModerationUpdate(BaseModel):
    """Схема обновления статуса модерации"""
    status: str
    moderation_notes: Optional[str] = None
    
    @field_validator("status")
    def validate_status(cls, v):
        if v not in [status for status in vars(ModerationStatusEnum).values() if not status.startswith("_")]:
            raise ValueError(f"Некорректный статус модерации. Допустимые значения: {', '.join([s for s in vars(ModerationStatusEnum).values() if not s.startswith('_')])}")
        return v


class ModerationRecordInDB(ModerationRecordBase):
    """Схема записи модерации из БД"""
    id: int
    company_id: int
    moderator_id: Optional[int] = None
    auto_check_passed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ModerationRecordResponse(ModerationRecordBase):
    """Схема ответа с данными записи модерации"""
    id: int
    company_id: int
    moderator_id: Optional[int] = None
    auto_check_passed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AutoCheckResult(BaseModel):
    """Результат автоматической проверки"""
    passed: bool
    checks: dict[str, bool]
    notes: Optional[str] = None 