from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy import func, and_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking
from src.models.service import Service
from src.models.user import User
from src.schemas.analytics import (
    AnalyticsServiceStat, 
    AnalyticsServiceStats,
    AnalyticsTimeStatDay,
    AnalyticsTimeStatHour,
    AnalyticsTimeStats,
    AnalyticsClientStat,
    AnalyticsClientStats
)


class AnalyticsRepository:
    """
    Репозиторий для работы с аналитикой
    """
    
    @staticmethod
    async def get_company_revenue(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Получить общую выручку компании за указанный период
        """
        query = select(func.sum(Booking.amount)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date,
                Booking.payment_status == "оплачено"
            )
        )
        
        result = await db.execute(query)
        revenue = result.scalar() or 0.0
        return revenue
        
    @staticmethod
    async def get_company_bookings_count(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Получить общее количество бронирований компании за указанный период
        """
        query = select(func.count(Booking.id)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        )
        
        result = await db.execute(query)
        count = result.scalar() or 0
        return count
        
    @staticmethod
    async def get_company_completion_rate(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Получить процент выполненных бронирований компании за указанный период
        """
        # Получаем общее количество бронирований
        total_query = select(func.count(Booking.id)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        )
        
        # Получаем количество выполненных бронирований
        completed_query = select(func.count(Booking.id)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date,
                Booking.status == "выполнено"
            )
        )
        
        total_result = await db.execute(total_query)
        completed_result = await db.execute(completed_query)
        
        total = total_result.scalar() or 0
        completed = completed_result.scalar() or 0
        
        return (completed / total * 100) if total > 0 else 0.0
        
    @staticmethod
    async def get_company_cancellation_rate(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Получить процент отмененных бронирований компании за указанный период
        """
        # Получаем общее количество бронирований
        total_query = select(func.count(Booking.id)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        )
        
        # Получаем количество отмененных бронирований
        cancelled_query = select(func.count(Booking.id)).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date,
                Booking.status == "отменено"
            )
        )
        
        total_result = await db.execute(total_query)
        cancelled_result = await db.execute(cancelled_query)
        
        total = total_result.scalar() or 0
        cancelled = cancelled_result.scalar() or 0
        
        return (cancelled / total * 100) if total > 0 else 0.0
    
    @staticmethod
    async def get_most_popular_service(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[int]:
        """
        Получить ID самой популярной услуги компании за указанный период
        """
        query = select(
            Booking.service_id,
            func.count(Booking.id).label("booking_count")
        ).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        ).group_by(
            Booking.service_id
        ).order_by(
            text("booking_count DESC")
        ).limit(1)
        
        result = await db.execute(query)
        service_data = result.first()
        
        return service_data.service_id if service_data else None
    
    @staticmethod
    async def get_service_stats(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> AnalyticsServiceStats:
        """
        Получить статистику по услугам компании за указанный период
        """
        # Получаем статистику по каждой услуге
        query = select(
            Service.id,
            Service.name,
            func.count(Booking.id).label("booking_count"),
            func.sum(Booking.amount).label("revenue")
        ).join(
            Booking, 
            and_(
                Service.id == Booking.service_id,
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date,
                Booking.payment_status == "оплачено"
            ),
            isouter=True
        ).where(
            Service.company_id == company_id
        ).group_by(
            Service.id
        ).order_by(
            text("booking_count DESC")
        )
        
        result = await db.execute(query)
        service_stats_data = result.all()
        
        # Вычисляем общую выручку для расчета процентов
        total_revenue = sum(stat.revenue or 0 for stat in service_stats_data)
        
        # Формируем список статистики услуг
        service_stats = []
        for stat in service_stats_data:
            percentage = ((stat.revenue or 0) / total_revenue * 100) if total_revenue > 0 else 0
            service_stats.append(
                AnalyticsServiceStat(
                    id=stat.id,
                    name=stat.name,
                    booking_count=stat.booking_count or 0,
                    revenue=stat.revenue or 0,
                    percentage=round(percentage, 2)
                )
            )
        
        return AnalyticsServiceStats(services=service_stats)

    @staticmethod
    async def get_time_stats(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> AnalyticsTimeStats:
        """
        Получить статистику по времени бронирований компании за указанный период
        """
        # Запрос для подсчета бронирований по дням недели
        day_query = select(
            func.extract('isodow', Booking.booking_time).label("weekday"),
            func.count(Booking.id).label("booking_count")
        ).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        ).group_by(
            text("weekday")
        ).order_by(
            text("weekday")
        )
        
        # Запрос для подсчета бронирований по часам
        hour_query = select(
            func.extract('hour', Booking.booking_time).label("hour"),
            func.count(Booking.id).label("booking_count")
        ).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        ).group_by(
            text("hour")
        ).order_by(
            text("hour")
        )
        
        day_result = await db.execute(day_query)
        hour_result = await db.execute(hour_query)
        
        day_stats_data = day_result.all()
        hour_stats_data = hour_result.all()
        
        # Формируем статистику по дням
        day_stats = [
            AnalyticsTimeStatDay(
                weekday=int(day.weekday),
                booking_count=day.booking_count
            )
            for day in day_stats_data
        ]
        
        # Формируем статистику по часам
        hour_stats = [
            AnalyticsTimeStatHour(
                hour=int(hour.hour),
                booking_count=hour.booking_count
            )
            for hour in hour_stats_data
        ]
        
        return AnalyticsTimeStats(days=day_stats, hours=hour_stats)
    
    @staticmethod
    async def get_client_stats(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> AnalyticsClientStats:
        """
        Получить статистику по клиентам компании за указанный период
        """
        # Получаем количество уникальных клиентов
        unique_clients_query = select(
            func.count(func.distinct(Booking.client_id))
        ).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date
            )
        )
        
        # Получаем топ-5 клиентов по сумме потраченных средств
        top_clients_query = select(
            Booking.client_id,
            func.count(Booking.id).label("booking_count"),
            func.sum(Booking.amount).label("total_spent")
        ).where(
            and_(
                Booking.service_id.in_(
                    select(Service.id).where(Service.company_id == company_id)
                ),
                Booking.booking_time >= start_date,
                Booking.booking_time <= end_date,
                Booking.payment_status == "оплачено"
            )
        ).group_by(
            Booking.client_id
        ).order_by(
            text("total_spent DESC")
        ).limit(5)
        
        unique_clients_result = await db.execute(unique_clients_query)
        top_clients_result = await db.execute(top_clients_query)
        
        unique_clients_count = unique_clients_result.scalar() or 0
        top_clients_data = top_clients_result.all()
        
        # Формируем список топ-клиентов
        top_clients = [
            AnalyticsClientStat(
                client_id=client.client_id,
                booking_count=client.booking_count,
                total_spent=client.total_spent or 0
            )
            for client in top_clients_data
        ]
        
        return AnalyticsClientStats(
            unique_clients_count=unique_clients_count,
            top_clients=top_clients
        )
        
    @staticmethod
    async def get_company_analytics(
        db: AsyncSession, 
        company_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Получить полную аналитику компании за указанный период
        """
        # Получаем основные метрики
        revenue = await AnalyticsRepository.get_company_revenue(db, company_id, start_date, end_date)
        bookings_count = await AnalyticsRepository.get_company_bookings_count(db, company_id, start_date, end_date)
        completion_rate = await AnalyticsRepository.get_company_completion_rate(db, company_id, start_date, end_date)
        cancellation_rate = await AnalyticsRepository.get_company_cancellation_rate(db, company_id, start_date, end_date)
        most_popular_service_id = await AnalyticsRepository.get_most_popular_service(db, company_id, start_date, end_date)
        
        # Получаем детальную статистику
        service_stats = await AnalyticsRepository.get_service_stats(db, company_id, start_date, end_date)
        time_stats = await AnalyticsRepository.get_time_stats(db, company_id, start_date, end_date)
        client_stats = await AnalyticsRepository.get_client_stats(db, company_id, start_date, end_date)
        
        # Вычисляем среднюю стоимость бронирования
        average_booking_value = revenue / bookings_count if bookings_count > 0 else 0
        
        # Формируем итоговый словарь с аналитикой
        analytics = {
            "company_id": company_id,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_revenue": revenue,
            "total_bookings": bookings_count,
            "average_booking_value": round(average_booking_value, 2),
            "completion_rate": round(completion_rate, 2),
            "cancellation_rate": round(cancellation_rate, 2),
            "most_popular_service_id": most_popular_service_id,
            "service_stats": service_stats,
            "time_stats": time_stats,
            "client_stats": client_stats
        }
        
        return analytics 