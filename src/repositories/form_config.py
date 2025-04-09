from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.form_config import FormConfig
from src.schemas.form_config import FormConfigCreate, FormConfigUpdate, EXAMPLE_COMPANY_REGISTRATION_CONFIG

class FormConfigRepository:
    """Репозиторий для работы с конфигурациями форм"""
    
    @staticmethod
    async def create(db: AsyncSession, form_config: FormConfigCreate) -> FormConfig:
        """
        Создать новую конфигурацию формы
        
        Args:
            db: Сессия базы данных
            form_config: Данные для создания
            
        Returns:
            Созданная конфигурация формы
        """
        new_form_config = FormConfig(**form_config.dict())
        db.add(new_form_config)
        await db.flush()
        return new_form_config
    
    @staticmethod
    async def get_by_id(db: AsyncSession, form_config_id: int) -> Optional[FormConfig]:
        """
        Получить конфигурацию формы по ID
        
        Args:
            db: Сессия базы данных
            form_config_id: ID конфигурации формы
            
        Returns:
            Конфигурация формы или None, если не найдена
        """
        query = select(FormConfig).where(FormConfig.id == form_config_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_active_by_types(
        db: AsyncSession, 
        business_type: str, 
        form_type: str
    ) -> Optional[FormConfig]:
        """
        Получить активную конфигурацию формы по типу бизнеса и типу формы
        
        Args:
            db: Сессия базы данных
            business_type: Тип бизнеса
            form_type: Тип формы
            
        Returns:
            Конфигурация формы или None, если не найдена
        """
        query = select(FormConfig).where(
            FormConfig.business_type == business_type,
            FormConfig.form_type == form_type,
            FormConfig.is_active == True
        ).order_by(FormConfig.version.desc())
        
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_by_business_type(
        db: AsyncSession,
        business_type: str,
        active_only: bool = True
    ) -> List[FormConfig]:
        """
        Получить все конфигурации форм для типа бизнеса
        
        Args:
            db: Сессия базы данных
            business_type: Тип бизнеса
            active_only: Только активные конфигурации
            
        Returns:
            Список конфигураций форм
        """
        query = select(FormConfig).where(FormConfig.business_type == business_type)
        
        if active_only:
            query = query.where(FormConfig.is_active == True)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession,
        form_config_id: int,
        form_config_update: FormConfigUpdate
    ) -> Optional[FormConfig]:
        """
        Обновить конфигурацию формы
        
        Args:
            db: Сессия базы данных
            form_config_id: ID конфигурации формы
            form_config_update: Данные для обновления
            
        Returns:
            Обновленная конфигурация формы или None, если не найдена
        """
        form_config = await FormConfigRepository.get_by_id(db, form_config_id)
        
        if not form_config:
            return None
        
        # Обновляем только переданные поля
        update_data = form_config_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(form_config, key, value)
        
        await db.flush()
        return form_config
    
    @staticmethod
    async def delete(db: AsyncSession, form_config_id: int) -> bool:
        """
        Удалить конфигурацию формы
        
        Args:
            db: Сессия базы данных
            form_config_id: ID конфигурации формы
            
        Returns:
            True если конфигурация успешно удалена, иначе False
        """
        form_config = await FormConfigRepository.get_by_id(db, form_config_id)
        
        if not form_config:
            return False
        
        await db.delete(form_config)
        await db.flush()
        return True
    
    @staticmethod
    async def create_default_configs(db: AsyncSession) -> None:
        """
        Создать дефолтные конфигурации форм
        
        Args:
            db: Сессия базы данных
        """
        # Проверяем наличие конфигураций в базе
        query = select(func.count()).select_from(FormConfig)
        result = await db.execute(query)
        count = result.scalar()
        
        if count > 0:
            return  # Конфигурации уже существуют
        
        # Создаем дефолтную конфигурацию для регистрации компании
        default_config = FormConfigCreate(
            business_type="default",
            form_type="company_registration",
            name="Регистрация компании",
            description="Стандартная форма для регистрации компании",
            config=EXAMPLE_COMPANY_REGISTRATION_CONFIG
        )
        
        await FormConfigRepository.create(db, default_config)
        
        # Здесь можно добавить другие дефолтные конфигурации для разных типов бизнеса
        # например для ресторанов, салонов красоты и т.д. 