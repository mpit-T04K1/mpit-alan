from datetime import datetime, date
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class AnalyticsBase(BaseModel):
    """Базовая схема аналитики"""
    date_range_start: datetime
    date_range_end: datetime


class AnalyticsServiceStat(BaseModel):
    """Статистика по услуге"""
    id: int
    name: str
    booking_count: int
    revenue: float
    percentage: float


class AnalyticsTimeStatDay(BaseModel):
    """Статистика по дню недели"""
    weekday: int
    booking_count: int


class AnalyticsTimeStatHour(BaseModel):
    """Статистика по часу"""
    hour: int
    booking_count: int


class AnalyticsClientStat(BaseModel):
    """Статистика по клиенту"""
    client_id: int
    booking_count: int
    total_spent: float


class AnalyticsServiceStats(BaseModel):
    """Общая статистика по услугам"""
    services: List[AnalyticsServiceStat]


class AnalyticsTimeStats(BaseModel):
    """Общая статистика по времени"""
    weekdays: List[AnalyticsTimeStatDay]
    hours: List[AnalyticsTimeStatHour]


class AnalyticsClientStats(BaseModel):
    """Общая статистика по клиентам"""
    unique_clients_count: int
    top_clients: List[AnalyticsClientStat]


class AnalyticsResponse(AnalyticsBase):
    """Схема ответа с данными аналитики"""
    id: int
    company_id: int
    total_revenue: float
    total_bookings: int
    average_booking_value: float
    completion_rate: float
    cancellation_rate: float
    most_popular_service_id: Optional[int] = None
    service_statistics: AnalyticsServiceStats
    time_statistics: AnalyticsTimeStats
    client_statistics: AnalyticsClientStats
    created_at: datetime
    
    class Config:
        orm_mode = True


class AnalyticsCreate(AnalyticsBase):
    """Схема запроса на создание аналитики"""
    company_id: int


class AnalyticsPeriodRequest(BaseModel):
    """Схема запроса на получение аналитики за период"""
    company_id: int
    start_date: date
    end_date: date 