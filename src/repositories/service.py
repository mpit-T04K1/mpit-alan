from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.service import Service
from src.models.booking import Booking
from src.schemas.service import ServiceCreate, ServiceUpdate
from src.core.errors import NotFoundError

class ServiceRepository:
    @staticmethod
    async def create(db: AsyncSession, service_data: ServiceCreate):
        """
        Создание новой услуги
        
        Args:
            db: Сессия базы данных
            service_data: Данные для создания услуги
            
        Returns:
            Созданная услуга
        """
        service = Service(**service_data.model_dump())
        db.add(service)
        await db.commit()
        await db.refresh(service)
        return service
    
    @staticmethod
    async def get_by_id(db: AsyncSession, service_id: int):
        """
        Получение услуги по ID
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            
        Returns:
            Услуга или None, если не найдена
        """
        query = select(Service).options(
            joinedload(Service.company)
        ).where(Service.id == service_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        """
        Получение всех услуг с пагинацией
        
        Args:
            db: Сессия базы данных
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список услуг
        """
        query = select(Service).options(
            joinedload(Service.company)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, service_id: int, service_data: ServiceUpdate):
        """
        Обновление услуги
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            service_data: Данные для обновления
            
        Returns:
            Обновленная услуга
        
        Raises:
            NotFoundError: Если услуга не найдена
        """
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise NotFoundError(f"Услуга с ID {service_id} не найдена")
        
        for key, value in service_data.model_dump(exclude_unset=True).items():
            setattr(service, key, value)
        
        await db.commit()
        await db.refresh(service)
        return service
    
    @staticmethod
    async def delete(db: AsyncSession, service_id: int):
        """
        Удаление услуги
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            
        Returns:
            True, если услуга успешно удалена
            
        Raises:
            NotFoundError: Если услуга не найдена
        """
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise NotFoundError(f"Услуга с ID {service_id} не найдена")
        
        await db.delete(service)
        await db.commit()
        return True
    
    @staticmethod
    async def get_by_company(db: AsyncSession, company_id: int, skip: int = 0, limit: int = 100):
        """
        Получение услуг компании
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список услуг компании
        """
        query = select(Service).where(
            Service.company_id == company_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def search(db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100):
        """
        Поиск услуг по названию или описанию
        
        Args:
            db: Сессия базы данных
            search_term: Поисковый запрос
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список найденных услуг
        """
        search_pattern = f"%{search_term}%"
        query = select(Service).options(
            joinedload(Service.company)
        ).where(
            (Service.name.ilike(search_pattern)) | 
            (Service.description.ilike(search_pattern))
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_category(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100):
        """
        Получение услуг по категории
        
        Args:
            db: Сессия базы данных
            category_id: ID категории
            skip: Сколько записей пропустить
            limit: Сколько записей вернуть
            
        Returns:
            Список услуг в категории
        """
        query = select(Service).options(
            joinedload(Service.company)
        ).where(
            Service.category_id == category_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_company(db: AsyncSession, company_id: int):
        """
        Подсчет количества услуг компании
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            
        Returns:
            Количество услуг
        """
        query = select(func.count(Service.id)).where(
            Service.company_id == company_id
        )
        
        result = await db.execute(query)
        return result.scalar_one() or 0
    
    @staticmethod
    async def get_popular_by_company(db: AsyncSession, company_id: int, limit: int = 5):
        """
        Получение самых популярных услуг компании по количеству бронирований
        
        Args:
            db: Сессия базы данных
            company_id: ID компании
            limit: Сколько услуг вернуть
            
        Returns:
            Список популярных услуг с количеством бронирований
        """
        query = select(
            Service,
            func.count(Booking.id).label('booking_count')
        ).join(
            Booking, Service.id == Booking.service_id, isouter=True
        ).where(
            Service.company_id == company_id
        ).group_by(
            Service.id
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(limit)
        
        result = await db.execute(query)
        return result.all()
    
    @staticmethod
    async def toggle_active(db: AsyncSession, service_id: int, is_active: bool):
        """
        Изменение статуса активности услуги
        
        Args:
            db: Сессия базы данных
            service_id: ID услуги
            is_active: Новый статус активности
            
        Returns:
            Обновленная услуга
            
        Raises:
            NotFoundError: Если услуга не найдена
        """
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise NotFoundError(f"Услуга с ID {service_id} не найдена")
        
        service.is_active = is_active
        
        await db.commit()
        await db.refresh(service)
        return service 