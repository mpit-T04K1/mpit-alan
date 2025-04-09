from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.db_adapter import Base as SrcDbAdapterBase

# Перечисление типов медиа
class MediaType(str, enum.Enum):
    """Типы медиафайлов"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    OTHER = "other"


class Media(SrcDbAdapterBase):
    """Модель медиафайлов"""
    __tablename__ = "media"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default=MediaType.IMAGE.value)
    url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Отношения
    company = relationship("Company", back_populates="media")
    
    def __repr__(self):
        return f"<Media {self.name} ({self.type})>" 