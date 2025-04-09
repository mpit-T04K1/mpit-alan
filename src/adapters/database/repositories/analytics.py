from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.models.analytics import Analytics
from src.adapters.database.models.booking import Booking, BookingStatus
from src.adapters.database.models.service import Service
from src.adapters.database.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[Analytics]):
    """Репозиторий для работы с аналитикой"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Analytics)

    async def get_by_company_and_period(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Optional[Analytics]:
        """Получить аналитику компании за период"""
        query = (
            select(Analytics)
            .where(
                and_(
                    Analytics.company_id == company_id,
                    Analytics.date_range_start == start_date,
                    Analytics.date_range_end == end_date
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def generate_analytics(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Analytics:
        """Сгенерировать аналитику для компании за период"""
        # Проверяем, есть ли уже аналитика за этот период
        existing_analytics = await self.get_by_company_and_period(
            company_id, start_date, end_date
        )
        if existing_analytics:
            return existing_analytics

        # Получаем данные о бронированиях за период
        bookings_data = await self._get_bookings_stats(company_id, start_date, end_date)
        
        # Получаем статистику по услугам
        service_stats = await self._get_service_statistics(company_id, start_date, end_date)
        
        # Получаем статистику по времени
        time_stats = await self._get_time_statistics(company_id, start_date, end_date)
        
        # Получаем статистику по клиентам
        client_stats = await self._get_client_statistics(company_id, start_date, end_date)
        
        # Создаем аналитику
        analytics_data = {
            "company_id": company_id,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "total_revenue": bookings_data["total_revenue"],
            "total_bookings": bookings_data["total_bookings"],
            "average_booking_value": bookings_data["average_booking_value"],
            "completion_rate": bookings_data["completion_rate"],
            "cancellation_rate": bookings_data["cancellation_rate"],
            "most_popular_service_id": bookings_data["most_popular_service_id"],
            "service_statistics": service_stats,
            "time_statistics": time_stats,
            "client_statistics": client_stats,
        }
        
        analytics = await self.create(analytics_data)
        return analytics

    async def _get_bookings_stats(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Получить статистику по бронированиям"""
        # Запрос для получения общей статистики по бронированиям
        query = (
            select(
                func.count().label("total_bookings"),
                func.sum(Booking.amount).label("total_revenue"),
                func.count(
                    case(
                        (Booking.status == BookingStatus.COMPLETED.value, 1),
                        else_=None
                    )
                ).label("completed_bookings"),
                func.count(
                    case(
                        (Booking.status == BookingStatus.CANCELED.value, 1),
                        else_=None
                    )
                ).label("canceled_bookings")
            )
            .select_from(Booking)
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
        )
        result = await self.session.execute(query)
        stats = result.fetchone()
        
        # Запрос для получения самой популярной услуги
        popular_service_query = (
            select(
                Booking.service_id,
                func.count().label("booking_count")
            )
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
            .group_by(Booking.service_id)
            .order_by(desc("booking_count"))
            .limit(1)
        )
        popular_service_result = await self.session.execute(popular_service_query)
        popular_service = popular_service_result.fetchone()
        
        # Вычисляем статистику
        total_bookings = stats.total_bookings if stats.total_bookings else 0
        total_revenue = stats.total_revenue if stats.total_revenue else 0
        completed_bookings = stats.completed_bookings if stats.completed_bookings else 0
        canceled_bookings = stats.canceled_bookings if stats.canceled_bookings else 0
        
        completion_rate = (completed_bookings / total_bookings) * 100 if total_bookings > 0 else 0
        cancellation_rate = (canceled_bookings / total_bookings) * 100 if total_bookings > 0 else 0
        average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
        
        most_popular_service_id = popular_service.service_id if popular_service else None
        
        return {
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "completion_rate": completion_rate,
            "cancellation_rate": cancellation_rate,
            "average_booking_value": average_booking_value,
            "most_popular_service_id": most_popular_service_id,
        }

    async def _get_service_statistics(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Получить статистику по услугам"""
        query = (
            select(
                Service.id,
                Service.name,
                func.count().label("booking_count"),
                func.sum(Booking.amount).label("revenue")
            )
            .join(Booking, Service.id == Booking.service_id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
            .group_by(Service.id, Service.name)
            .order_by(desc("booking_count"))
        )
        result = await self.session.execute(query)
        services = result.fetchall()
        
        return {
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "booking_count": service.booking_count,
                    "revenue": service.revenue if service.revenue else 0,
                    "percentage": 0  # Рассчитывается на клиенте
                }
                for service in services
            ]
        }

    async def _get_time_statistics(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Получить статистику по времени"""
        # Статистика по дням недели
        weekday_query = (
            select(
                func.extract("dow", Booking.booking_time).label("weekday"),
                func.count().label("booking_count")
            )
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
            .group_by("weekday")
            .order_by("weekday")
        )
        weekday_result = await self.session.execute(weekday_query)
        weekdays = weekday_result.fetchall()
        
        # Статистика по часам
        hour_query = (
            select(
                func.extract("hour", Booking.booking_time).label("hour"),
                func.count().label("booking_count")
            )
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
            .group_by("hour")
            .order_by("hour")
        )
        hour_result = await self.session.execute(hour_query)
        hours = hour_result.fetchall()
        
        return {
            "weekdays": [
                {
                    "weekday": day.weekday,
                    "booking_count": day.booking_count
                }
                for day in weekdays
            ],
            "hours": [
                {
                    "hour": hour.hour,
                    "booking_count": hour.booking_count
                }
                for hour in hours
            ]
        }

    async def _get_client_statistics(
        self, company_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Получить статистику по клиентам"""
        # Количество уникальных клиентов
        unique_clients_query = (
            select(func.count(func.distinct(Booking.client_id)))
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
        )
        unique_clients_result = await self.session.execute(unique_clients_query)
        unique_clients_count = unique_clients_result.scalar_one()
        
        # Клиенты с наибольшим количеством бронирований
        top_clients_query = (
            select(
                Booking.client_id,
                func.count().label("booking_count"),
                func.sum(Booking.amount).label("total_spent")
            )
            .join(Service, Booking.service_id == Service.id)
            .where(
                and_(
                    Service.company_id == company_id,
                    Booking.booking_time >= start_date,
                    Booking.booking_time <= end_date
                )
            )
            .group_by(Booking.client_id)
            .order_by(desc("booking_count"))
            .limit(5)
        )
        top_clients_result = await self.session.execute(top_clients_query)
        top_clients = top_clients_result.fetchall()
        
        return {
            "unique_clients_count": unique_clients_count,
            "top_clients": [
                {
                    "client_id": client.client_id,
                    "booking_count": client.booking_count,
                    "total_spent": client.total_spent if client.total_spent else 0
                }
                for client in top_clients
            ]
        } 