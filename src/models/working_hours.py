from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship

from src.db_adapter import Base as SrcDbAdapterBase

class DayOfWeek(str, Enum):
    """Дни недели"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class WorkingHours(SrcDbAdapterBase):
    """Модель рабочих часов"""
    __tablename__ = "working_hours"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    day = Column(String, nullable=False)
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
    is_working_day = Column(Boolean, default=True, nullable=False)
    
    # Отношения
    company = relationship("Company", back_populates="working_hours")
    
    def __repr__(self):
        if not self.is_working_day:
            return f"<WorkingHours {self.day} (выходной)>"
        return f"<WorkingHours {self.day} ({self.open_time}-{self.close_time})>" 