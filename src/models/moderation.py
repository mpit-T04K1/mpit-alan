from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
import enum

from src.db_adapter import Base as SrcDbAdapterBase


class ModerationStatus(str, enum.Enum):
    """Статусы модерации"""
    PENDING = "pending"       # Ожидает модерации
    APPROVED = "approved"     # Одобрено
    REJECTED = "rejected"     # Отклонено
    REVOKED = "revoked"       # Отозвано (после одобрения)
    MODIFIED = "modified"     # Изменено (требует повторной модерации)


class ModerationAction(str, enum.Enum):
    """Действия модерации"""
    SUBMIT = "submit"       # Отправить на модерацию
    APPROVE = "approve"     # Одобрить
    REJECT = "reject"       # Отклонить
    REVOKE = "revoke"       # Отозвать одобрение
    MODIFY = "modify"       # Изменить


class ModerationRecord(SrcDbAdapterBase):
    """Модель записи модерации"""
    __tablename__ = "moderation_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    status = Column(String(50), nullable=False, default=ModerationStatus.PENDING.value)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    auto_check_passed = Column(Boolean, default=False)
    moderation_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    company = relationship("Company", back_populates="moderation_records")
    moderator = relationship("User")

    def __init__(
        self, 
        entity_type: str, 
        entity_id: int, 
        action: ModerationAction,
        comments: str = None,
        moderator_id: int = None
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.comments = comments
        self.moderator_id = moderator_id 