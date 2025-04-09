from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.adapters.database.models.company import Company, ModerationStatus
from src.adapters.database.models.location import Location
from src.adapters.database.models.working_hours import WorkingHours
from src.adapters.database.models.media import Media
from src.adapters.database.models.user import User
from src.adapters.database.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Репозиторий для работы с компаниями"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)

    async def get_by_id_with_relations(self, company_id: int) -> Optional[Company]:
        """Получить компанию по ID со всеми связанными данными"""
        query = (
            select(Company)
            .where(Company.id == company_id)
            .options(
                selectinload(Company.locations),
                selectinload(Company.services),
                selectinload(Company.working_hours),
                selectinload(Company.media),
                joinedload(Company.owner)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: int) -> List[Company]:
        """Получить все компании пользователя"""
        query = select(Company).where(Company.owner_id == owner_id)
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_by_business_type(self, business_type: str) -> List[Company]:
        """Получить компании по типу бизнеса"""
        query = (
            select(Company)
            .where(
                and_(
                    Company.business_type == business_type,
                    Company.moderation_status == ModerationStatus.APPROVED.value,
                    Company.is_active == True
                )
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars())

    async def search_companies(
        self, search_term: str, business_type: Optional[str] = None
    ) -> List[Company]:
        """Поиск компаний по названию, описанию, и т.д."""
        filters = [
            Company.moderation_status == ModerationStatus.APPROVED.value,
            Company.is_active == True,
            or_(
                Company.name.ilike(f"%{search_term}%"),
                Company.description.ilike(f"%{search_term}%")
            )
        ]
        
        if business_type:
            filters.append(Company.business_type == business_type)
        
        query = select(Company).where(and_(*filters))
        result = await self.session.execute(query)
        return list(result.scalars())

    async def get_pending_moderation(self) -> List[Company]:
        """Получить компании, ожидающие модерации"""
        query = select(Company).where(Company.moderation_status == ModerationStatus.PENDING.value)
        result = await self.session.execute(query)
        return list(result.scalars())

    async def update_moderation_status(
        self, company_id: int, status: str, notes: Optional[str] = None
    ) -> Company:
        """Обновить статус модерации компании"""
        company = await self.find_one(id=company_id)
        
        company.moderation_status = status
        if notes:
            company.moderation_notes = notes
        
        self.session.add(company)
        return company 