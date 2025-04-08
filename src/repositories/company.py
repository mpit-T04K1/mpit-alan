"""
Репозиторий для работы с компаниями
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.models.company import Company


class CompanyRepository:
    """Репозиторий для работы с компаниями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Получить компанию по ID
        
        Args:
            company_id: ID компании
            
        Returns:
            Объект компании или None
        """
        query = select(Company).where(Company.id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_owner_id(self, owner_id: int) -> List[Company]:
        """
        Получить компании по ID владельца
        
        Args:
            owner_id: ID владельца
            
        Returns:
            Список компаний
        """
        query = select(Company).where(Company.owner_id == owner_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, company_data: Dict[str, Any]) -> Company:
        """
        Создать новую компанию
        
        Args:
            company_data: Данные компании
            
        Returns:
            Объект созданной компании
        """
        company = Company(**company_data)
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def update(self, company_id: int, company_data: Dict[str, Any]) -> Optional[Company]:
        """
        Обновить данные компании
        
        Args:
            company_id: ID компании
            company_data: Новые данные компании
            
        Returns:
            Объект обновленной компании или None
        """
        company = await self.get_by_id(company_id)
        if not company:
            return None
        
        for key, value in company_data.items():
            if hasattr(company, key):
                setattr(company, key, value)
        
        company.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def delete(self, company_id: int) -> bool:
        """
        Удалить компанию
        
        Args:
            company_id: ID компании
            
        Returns:
            True если компания удалена, иначе False
        """
        company = await self.get_by_id(company_id)
        if not company:
            return False
        
        await self.db.delete(company)
        await self.db.commit()
        return True
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """
        Получить список всех компаний
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список компаний
        """
        query = select(Company).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """
        Поиск компаний по названию
        
        Args:
            name: Строка поиска
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            Список компаний, соответствующих поисковому запросу
        """
        query = select(Company).where(
            Company.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all() 