from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.booking import Booking
from src.models.service import Service
from src.models.user import User
from src.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate, BookingPaymentUpdate
from src.core.errors import NotFoundError

class BookingRepository:
    @staticmethod
    async def create(db: AsyncSession, booking_data: BookingCreate):
        """
        Создание нового бронирования
        
        Args:
            db: Сессия базы данных
            booking_data: Данные для создания бронирования
            
        Returns:
            Созданное бронирование
        """
        booking = Booking(**booking_data.model_dump())
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking
    
    @staticmethod
    async def get_by_id(db: AsyncSession, booking_id: int):
        """
        Получение бронирования по ID
        
        Args:
            db: Сессия базы данных
            booking_id: ID бронирования
            
        Returns:
            Бронирование или None, если не найдено
        """
        query = select(Booking).options(
            joinedload(Booking.service),
            joinedload(Booking.user)
        ).where(Booking.id == booking_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        """
        Получение всех бронирований с пагинацией
        
        Args:
            db: Сессия базы данных
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список бронирований
        """
        query = select(Booking).options(
            joinedload(Booking.service),
            joinedload(Booking.user)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, booking_id: int, booking_data: BookingUpdate):
        """
        Обновление бронирования
        
        Args:
            db: Сессия базы данных
            booking_id: ID бронирования
            booking_data: Данные для обновления
            
        Returns:
            Обновленное бронирование
        
        Raises:
            NotFoundError: Если бронирование не найдено
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        
        for key, value in booking_data.model_dump(exclude_unset=True).items():
            setattr(booking, key, value)
        
        await db.commit()
        await db.refresh(booking)
        return booking
    
    @staticmethod
    async def delete(db: AsyncSession, booking_id: int):
        """
        Удаление бронирования
        
        Args:
            db: Сессия базы данных
            booking_id: ID бронирования
            
        Returns:
            True, если бронирование успешно удалено
            
        Raises:
            NotFoundError: Если бронирование не найдено
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        
        await db.delete(booking)
        await db.commit()
        return True
    
    @staticmethod
    async def update_status(db: AsyncSession, booking_id: int, status_data: BookingStatusUpdate):
        """
        Обновление статуса бронирования
        
        Args:
            db: Сессия базы данных
            booking_id: ID бронирования
            status_data: Данные для обновления статуса
            
        Returns:
            Обновленное бронирование
            
        Raises:
            NotFoundError: Если бронирование не найдено
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        
        booking.status = status_data.status
        
        await db.commit()
        await db.refresh(booking)
        return booking
    
    @staticmethod
    async def update_payment(db: AsyncSession, booking_id: int, payment_data: BookingPaymentUpdate):
        """
        Обновление информации об оплате бронирования
        
        Args:
            db: Сессия базы данных
            booking_id: ID бронирования
            payment_data: Данные для обновления информации об оплате
            
        Returns:
            Обновленное бронирование
            
        Raises:
            NotFoundError: Если бронирование не найдено
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise NotFoundError(f"Бронирование с ID {booking_id} не найдено")
        
        booking.is_paid = payment_data.is_paid
        booking.payment_id = payment_data.payment_id
        
        await db.commit()
        await db.refresh(booking)
        return booking
    
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
        """
        Получение бронирований пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список бронирований пользователя
        """
        query = select(Booking).options(
            joinedload(Booking.service)
        ).where(Booking.user_id == user_id).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_company(db: AsyncSession, company_id: int, skip: int = 0, limit: int = 100):
        """
        Получение бронирований для компании
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список бронирований для услуг компании
        """
        query = select(Booking).join(
            Service, Booking.service_id == Service.id
        ).options(
            joinedload(Booking.service),
            joinedload(Booking.user)
        ).where(Service.company_id == company_id).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_service(db: AsyncSession, service_id: int, skip: int = 0, limit: int = 100):
        """
        Получение бронирований для услуги
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список бронирований для услуги
        """
        query = select(Booking).options(
            joinedload(Booking.user)
        ).where(Booking.service_id == service_id).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_active_by_company(db: AsyncSession, company_id: int):
        """
        Подсчет активных бронирований для компании
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            
        Returns:
            Количество активных бронирований
        """
        query = select(func.count(Booking.id)).join(
            Service, Booking.service_id == Service.id
        ).where(
            Service.company_id == company_id,
            Booking.status.in_(["pending", "confirmed"])
        )
        
        result = await db.execute(query)
        return result.scalar_one() or 0
    
    @staticmethod
    async def get_recent_by_company(db: AsyncSession, company_id: int, limit: int = 5):
        """
        Получение последних бронирований для компании
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            limit: Сколько записей вернуть
            
        Returns:
            Список последних бронирований
        """
        query = select(Booking).join(
            Service, Booking.service_id == Service.id
        ).options(
            joinedload(Booking.service),
            joinedload(Booking.user)
        ).where(
            Service.company_id == company_id
        ).order_by(Booking.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_date_range(db: AsyncSession, service_id: int, start_date, end_date):
        """
        Получение бронирований в указанном диапазоне дат
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список бронирований в указанном диапазоне
        """
        query = select(Booking).where(
            Booking.service_id == service_id,
            Booking.start_time >= start_date,
            Booking.end_time <= end_date
        )
        
        result = await db.execute(query)
        return result.scalars().all() 