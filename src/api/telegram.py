from typing import Dict, Any

from fastapi import APIRouter, Depends, BackgroundTasks, Body, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.core.config import settings
from src.services.telegram import TelegramService
from src.api.auth import get_current_admin_user
from src.schemas.user import UserResponse

router = APIRouter(tags=["Telegram"])

# Защита вебхука
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_telegram_webhook(api_key: str = Depends(API_KEY_HEADER)):
    """
    Проверка API ключа для защиты вебхука
    """
    if api_key != settings.TELEGRAM_WEBHOOK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    update: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_telegram_webhook)
):
    """
    Вебхук для обработки обновлений от Telegram
    
    Args:
        update: Данные обновления от Telegram
        background_tasks: Фоновые задачи
        db: Сессия базы данных
        _: Проверка API ключа
        
    Returns:
        Успешный ответ для Telegram
    """
    # Создаем экземпляр сервиса Telegram
    telegram_service = TelegramService()
    
    # Обрабатываем обновление в фоновом режиме
    if background_tasks:
        background_tasks.add_task(telegram_service.process_update, update)
    else:
        await telegram_service.process_update(update)
    
    # Telegram ожидает пустой ответ со статусом 200
    return {"ok": True}


@router.post("/setup", status_code=status.HTTP_200_OK)
async def setup_telegram_webhook(
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Установить вебхук для Telegram бота
    
    Args:
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Результат установки вебхука
    """
    telegram_service = TelegramService()
    result = await telegram_service.set_webhook()
    
    return {"ok": True, "result": result}


@router.post("/remove", status_code=status.HTTP_200_OK)
async def remove_telegram_webhook(
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Удалить вебхук для Telegram бота
    
    Args:
        current_user: Текущий пользователь (должен быть администратором)
        
    Returns:
        Результат удаления вебхука
    """
    telegram_service = TelegramService()
    result = await telegram_service.delete_webhook()
    
    return {"ok": True, "result": result} 