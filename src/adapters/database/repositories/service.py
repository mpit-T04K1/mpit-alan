from typing import Dict, List, Optional, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.adapters.database.models.service import Service
from src.adapters.database.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    """Репозиторий для работы с услугами"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Service)

    async def get_by_company(self, company_id: int) -> List[Service]:
        """Получить все услуги компании"""
        query = (
            select(Service)
            .where(
                and_(
                    Service.company_id == company_id,
                    Service.is_active == True
                )
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_by_id_with_company(self, service_id: int) -> Optional[Service]:
        """Получить услугу по ID с данными о компании"""
        query = (
            select(Service)
            .where(Service.id == service_id)
            .options(joinedload(Service.company))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search_services(self, search_term: str, company_id: Optional[int] = None) -> List[Service]:
        """Поиск услуг по названию и описанию"""
        filters = [
            Service.is_active == True,
            or_(
                Service.name.ilike(f"%{search_term}%"),
                Service.description.ilike(f"%{search_term}%")
            )
        ]
        
        if company_id:
            filters.append(Service.company_id == company_id)
        
        query = select(Service).where(and_(*filters))
        result = await self.session.execute(query)
        return list(result.scalars())

    async def toggle_service_status(self, service_id: int, is_active: bool) -> Service:
        """Включить/выключить услугу"""
        service = await self.find_one(id=service_id)
        service.is_active = is_active
        self.session.add(service)
        return service

    async def get_services_by_price_range(
        self, min_price: float, max_price: float, company_id: Optional[int] = None
    ) -> List[Service]:
        """Получить услуги в заданном диапазоне цен"""
        filters = [
            Service.is_active == True,
            Service.price >= min_price,
            Service.price <= max_price
        ]
        
        if company_id:
            filters.append(Service.company_id == company_id)
        
        query = select(Service).where(and_(*filters))
        result = await self.session.execute(query)
        return list(result.scalars()) 