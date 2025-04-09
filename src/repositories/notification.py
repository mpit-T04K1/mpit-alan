"""
Репозиторий для работы с уведомлениями
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, or_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification


class NotificationRepository:
    """Репозиторий для работы с уведомлениями пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """
        Получить уведомление по ID
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            Уведомление или None, если не найдено
        """
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user(self, 
                         user_id: int, 
                         read: Optional[bool] = None,
                         limit: int = 20, 
                         offset: int = 0) -> List[Notification]:
        """
        Получить уведомления пользователя
        
        Args:
            user_id: ID пользователя
            read: Фильтр по прочитанности (None - все, True - прочитанные, False - непрочитанные)
            limit: Ограничение количества результатов
            offset: Смещение от начала списка
            
        Returns:
            Список уведомлений
        """
        query = select(Notification).where(Notification.user_id == user_id)
        
        if read is not None:
            query = query.where(Notification.read == read)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars())
    
    async def count_unread(self, user_id: int) -> int:
        """
        Получить количество непрочитанных уведомлений пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество непрочитанных уведомлений
        """
        query = select(func.count()).where(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, notification_data: Dict[str, Any]) -> Notification:
        """
        Создать новое уведомление
        
        Args:
            notification_data: Данные для создания уведомления
            
        Returns:
            Созданное уведомление
        """
        notification = Notification(**notification_data)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
    
    async def update(self, notification_id: int, update_data: Dict[str, Any]) -> Optional[Notification]:
        """
        Обновить уведомление
        
        Args:
            notification_id: ID уведомления
            update_data: Данные для обновления
            
        Returns:
            Обновленное уведомление или None, если не найдено
        """
        query = update(Notification).where(Notification.id == notification_id).values(**update_data)
        await self.session.execute(query)
        await self.session.commit()
        
        # Получаем обновленное уведомление
        return await self.get_by_id(notification_id)
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """
        Отметить все уведомления пользователя как прочитанные
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество обновленных уведомлений
        """
        query = update(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        ).values(read=True)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount
    
    async def delete(self, notification_id: int) -> bool:
        """
        Удалить уведомление
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            True, если уведомление удалено, иначе False
        """
        query = delete(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def delete_by_user(self, user_id: int) -> int:
        """
        Удалить все уведомления пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество удаленных уведомлений
        """
        query = delete(Notification).where(Notification.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount 