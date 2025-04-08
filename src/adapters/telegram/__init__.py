from typing import Dict, List, Optional, Protocol, Any

from src.settings import settings
from src.utils.exceptions import TelegramError


class TelegramGatewayProtocol(Protocol):
    """Протокол для работы с Telegram API"""
    
    async def send_message(self, chat_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """Отправить сообщение в Telegram"""
        ...
    
    async def send_booking_notification(
        self, 
        chat_id: int, 
        booking_id: int, 
        service_name: str, 
        company_name: str, 
        booking_time: str
    ) -> Dict[str, Any]:
        """Отправить уведомление о бронировании"""
        ...
    
    async def send_booking_confirmation(
        self, 
        chat_id: int, 
        booking_id: int
    ) -> Dict[str, Any]:
        """Отправить подтверждение бронирования"""
        ...
    
    async def send_booking_cancellation(
        self, 
        chat_id: int, 
        booking_id: int, 
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Отправить уведомление об отмене бронирования"""
        ...


class TelegramGateway:
    """Шлюз для работы с Telegram API"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN.get_secret_value() if settings.TELEGRAM_BOT_TOKEN else None
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
    
    async def send_message(self, chat_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """Отправить сообщение в Telegram"""
        if not self.bot_token:
            raise TelegramError("Telegram bot token is not configured")
        
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise TelegramError(f"Failed to send Telegram message: {error_text}")
                
                result = await response.json()
                return result
    
    async def send_booking_notification(
        self, 
        chat_id: int, 
        booking_id: int, 
        service_name: str, 
        company_name: str, 
        booking_time: str
    ) -> Dict[str, Any]:
        """Отправить уведомление о бронировании"""
        text = (
            f"<b>🔔 Новое бронирование #{booking_id}</b>\n\n"
            f"Услуга: <b>{service_name}</b>\n"
            f"Компания: <b>{company_name}</b>\n"
            f"Время: <b>{booking_time}</b>"
        )
        
        return await self.send_message(chat_id, text)
    
    async def send_booking_confirmation(
        self, 
        chat_id: int, 
        booking_id: int
    ) -> Dict[str, Any]:
        """Отправить подтверждение бронирования"""
        text = (
            f"<b>✅ Бронирование #{booking_id} подтверждено</b>\n\n"
            f"Ваше бронирование подтверждено. Ждем вас в указанное время."
        )
        
        return await self.send_message(chat_id, text)
    
    async def send_booking_cancellation(
        self, 
        chat_id: int, 
        booking_id: int, 
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Отправить уведомление об отмене бронирования"""
        text = (
            f"<b>❌ Бронирование #{booking_id} отменено</b>\n\n"
        )
        
        if reason:
            text += f"Причина: {reason}"
        
        return await self.send_message(chat_id, text) 