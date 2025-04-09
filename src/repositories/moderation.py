from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.moderation import ModerationRecord, ModerationStatus
from src.schemas.moderation import ModerationRecordCreate, ModerationUpdate, AutoCheckResult


class ModerationRepository:
    """
    Репозиторий для работы с модерацией
    """
    
    @staticmethod
    async def create(
        db: AsyncSession, 
        data: ModerationRecordCreate
    ) -> ModerationRecord:
        """
        Создать новую запись модерации
        """
        db_record = ModerationRecord(
            company_id=data.company_id,
            auto_check_passed=data.auto_check_passed,
            status=ModerationStatus.PENDING.value
        )
        
        db.add(db_record)
        await db.commit()
        await db.refresh(db_record)
        
        return db_record
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, 
        record_id: int
    ) -> Optional[ModerationRecord]:
        """
        Получить запись модерации по ID
        """
        query = select(ModerationRecord).where(ModerationRecord.id == record_id)
        result = await db.execute(query)
        
        return result.scalars().first()
    
    @staticmethod
    async def get_by_company_id(
        db: AsyncSession, 
        company_id: int
    ) -> List[ModerationRecord]:
        """
        Получить все записи модерации для компании
        """
        query = (
            select(ModerationRecord)
            .where(ModerationRecord.company_id == company_id)
            .order_by(ModerationRecord.created_at.desc())
        )
        result = await db.execute(query)
        
        return list(result.scalars().all())
    
    @staticmethod
    async def get_latest_by_company_id(
        db: AsyncSession, 
        company_id: int
    ) -> Optional[ModerationRecord]:
        """
        Получить последнюю запись модерации для компании
        """
        query = (
            select(ModerationRecord)
            .where(ModerationRecord.company_id == company_id)
            .order_by(ModerationRecord.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        
        return result.scalars().first()
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        record_id: int, 
        moderator_id: int,
        data: ModerationUpdate
    ) -> Optional[ModerationRecord]:
        """
        Обновить запись модерации
        """
        query = (
            update(ModerationRecord)
            .where(ModerationRecord.id == record_id)
            .values(
                status=data.status,
                moderation_notes=data.moderation_notes,
                moderator_id=moderator_id
            )
            .returning(ModerationRecord)
        )
        
        result = await db.execute(query)
        await db.commit()
        
        return result.scalars().first()
    
    @staticmethod
    async def get_pending_records(
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0
    ) -> List[ModerationRecord]:
        """
        Получить записи модерации в статусе "на рассмотрении"
        """
        query = (
            select(ModerationRecord)
            .where(ModerationRecord.status == ModerationStatus.PENDING.value)
            .order_by(ModerationRecord.created_at)
            .offset(offset)
            .limit(limit)
        )
        
        result = await db.execute(query)
        
        return list(result.scalars().all())
    
    @staticmethod
    async def count_pending_records(
        db: AsyncSession
    ) -> int:
        """
        Получить количество записей модерации в статусе "на рассмотрении"
        """
        query = (
            select([db.func.count()])
            .select_from(ModerationRecord)
            .where(ModerationRecord.status == ModerationStatus.PENDING.value)
        )
        
        result = await db.execute(query)
        
        return result.scalar_one()
    
    @staticmethod
    async def auto_check_company(
        company_id: int
    ) -> AutoCheckResult:
        """
        Выполнить автоматическую проверку компании
        
        В реальном проекте здесь может быть более сложная логика,
        например:
        - Проверка на наличие запрещенных слов
        - Верификация адреса через API геокодирования
        - Проверка юридической информации через API ФНС
        - и т.д.
        """
        # Упрощенная логика для демонстрации
        checks = {
            "has_required_fields": True,
            "website_valid": True,
            "banned_words_check": True,
            "duplicate_check": True
        }
        
        passed = all(checks.values())
        notes = "Автоматическая проверка пройдена успешно." if passed else "Автоматическая проверка не пройдена."
        
        return AutoCheckResult(
            passed=passed,
            checks=checks,
            notes=notes
        ) 