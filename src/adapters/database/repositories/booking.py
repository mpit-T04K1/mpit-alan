from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, and_, or_, func, between
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.adapters.database.models.booking import Booking, BookingStatus
from src.adapters.database.models.service import Service
from src.adapters.database.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Репозиторий для работы с бронированиями"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Booking)

    async def get_by_id_with_relations(self, booking_id: int) -> Optional[Booking]:
        """Получить бронирование по ID со всеми связанными данными"""
        query = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                joinedload(Booking.client),
                joinedload(Booking.service).joinedload(Service.company)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_client(self, client_id: int) -> List[Booking]:
        """Получить все бронирования клиента"""
        query = (
            select(Booking)
            .where(Booking.client_id == client_id)
            .options(joinedload(Booking.service))
            .order_by(Booking.booking_time.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_by_service(self, service_id: int) -> List[Booking]:
        """Получить все бронирования для услуги"""
        query = (
            select(Booking)
            .where(Booking.service_id == service_id)
            .options(joinedload(Booking.client))
            .order_by(Booking.booking_time)
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_company_bookings(self, company_id: int) -> List[Booking]:
        """Получить все бронирования для компании"""
        query = (
            select(Booking)
            .join(Service, Booking.service_id == Service.id)
            .where(Service.company_id == company_id)
            .options(
                joinedload(Booking.client),
                joinedload(Booking.service)
            )
            .order_by(Booking.booking_time)
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_active_bookings_by_service(self, service_id: int) -> List[Booking]:
        """Получить активные бронирования для услуги"""
        now = datetime.utcnow()
        query = (
            select(Booking)
            .where(
                and_(
                    Booking.service_id == service_id,
                    Booking.status == BookingStatus.CONFIRMED.value,
                    Booking.booking_time >= now
                )
            )
            .order_by(Booking.booking_time)
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def check_time_slot_availability(
        self, service_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        """Проверить доступность временного слота для бронирования"""
        # Ищем пересекающиеся бронирования
        query = (
            select(func.count())
            .where(
                and_(
                    Booking.service_id == service_id,
                    Booking.status == BookingStatus.CONFIRMED.value,
                    or_(
                        # Начало нового бронирования внутри существующего
                        and_(
                            Booking.booking_time <= start_time,
                            Booking.end_time > start_time
                        ),
                        # Конец нового бронирования внутри существующего
                        and_(
                            Booking.booking_time < end_time,
                            Booking.end_time >= end_time
                        ),
                        # Новое бронирование полностью покрывает существующее
                        and_(
                            Booking.booking_time >= start_time,
                            Booking.end_time <= end_time
                        )
                    )
                )
            )
        )
        result = await self.session.execute(query)
        count = result.scalar_one()
        
        # Если нет пересекающихся бронирований, слот доступен
        return count == 0

    async def update_booking_status(
        self, booking_id: int, status: str, notes: Optional[str] = None
    ) -> Booking:
        """Обновить статус бронирования"""
        booking = await self.find_one(id=booking_id)
        
        booking.status = status
        if notes:
            booking.business_notes = notes
        
        self.session.add(booking)
        return booking 