from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from src.db_adapter import Base as SrcDbAdapterBase

class Analytics(SrcDbAdapterBase):
    """Модель аналитики"""
    __tablename__ = "analytics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    total_revenue = Column(Float, default=0.0, nullable=False)
    total_bookings = Column(Integer, default=0, nullable=False)
    average_booking_value = Column(Float, default=0.0, nullable=False)
    completion_rate = Column(Float, default=0.0, nullable=False)  # процент завершенных бронирований
    cancellation_rate = Column(Float, default=0.0, nullable=False)  # процент отмененных бронирований
    most_popular_service_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Детальная статистика по услугам, времени и т.д.
    service_statistics = Column(JSON, nullable=True)
    time_statistics = Column(JSON, nullable=True)
    client_statistics = Column(JSON, nullable=True)
    
    def __repr__(self):
        period = f"{self.date_range_start.date()} to {self.date_range_end.date()}"
        return f"<Analytics {period} ({self.company_id})>" 