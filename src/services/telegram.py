import json
from typing import Optional, Dict, Any, List

import aiohttp
from fastapi import BackgroundTasks

from src.core.config import settings
from src.core.errors import TelegramError
from src.schemas.booking import BookingDetailResponse


class TelegramService:
    """
    Сервис для работы с Telegram API и нейроассистентом Карл
    """
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
    
    async def set_webhook(self) -> Dict[str, Any]:
        """
        Установить вебхук для бота
        """
        if not self.token:
            raise TelegramError("Telegram token not configured")
            
        if not self.webhook_url:
            raise TelegramError("Webhook URL not configured")
        
        url = f"{self.api_url}/setWebhook"
        payload = {
            "url": str(self.webhook_url),
            "allowed_updates": ["message", "callback_query"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise TelegramError(f"Failed to set webhook: {text}")
                
                return await response.json()
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """
        Удалить вебхук для бота
        """
        if not self.token:
            raise TelegramError("Telegram token not configured")
            
        url = f"{self.api_url}/deleteWebhook"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise TelegramError(f"Failed to delete webhook: {text}")
                
                return await response.json()
    
    async def send_message(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Отправить сообщение пользователю
        """
        if not self.token:
            raise TelegramError("Telegram token not configured")
            
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise TelegramError(f"Failed to send message: {text}")
                
                return await response.json()
    
    def schedule_booking_notification(
        self, 
        background_tasks: BackgroundTasks,
        chat_id: int, 
        booking: BookingDetailResponse
    ) -> None:
        """
        Запланировать отправку уведомления о бронировании
        """
        background_tasks.add_task(self.send_booking_notification, chat_id, booking)
    
    async def send_booking_notification(
        self, 
        chat_id: int, 
        booking: BookingDetailResponse
    ) -> Dict[str, Any]:
        """
        Отправить уведомление о бронировании
        """
        text = (
            f"🔔 <b>Новое бронирование #{booking.id}</b>\n\n"
            f"📅 Дата и время: <b>{booking.booking_time.strftime('%d.%m.%Y %H:%M')}</b>\n"
            f"🏢 Компания: <b>{booking.company_name or 'Не указано'}</b>\n"
            f"🔧 Услуга: <b>{booking.service_name or 'Не указано'}</b>\n"
            f"💰 Стоимость: <b>{booking.amount or 0} ₽</b>\n"
            f"💳 Статус оплаты: <b>{booking.payment_status}</b>\n\n"
            f"📝 Примечания: {booking.customer_notes or 'Нет'}"
        )
        
        # Создаем кнопки для управления бронированием
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "✅ Подтвердить",
                        "callback_data": f"confirm_booking:{booking.id}"
                    },
                    {
                        "text": "❌ Отменить",
                        "callback_data": f"cancel_booking:{booking.id}"
                    }
                ],
                [
                    {
                        "text": "📋 Детали",
                        "callback_data": f"booking_details:{booking.id}"
                    }
                ]
            ]
        }
        
        return await self.send_message(chat_id, text, reply_markup=reply_markup)
    
    async def send_booking_confirmation(
        self, 
        chat_id: int, 
        booking_id: int
    ) -> Dict[str, Any]:
        """
        Отправить подтверждение бронирования
        """
        text = (
            f"✅ <b>Бронирование #{booking_id} подтверждено</b>\n\n"
            f"Ваше бронирование подтверждено. Мы будем ждать вас в указанное время!"
        )
        
        return await self.send_message(chat_id, text)
    
    async def send_booking_cancellation(
        self, 
        chat_id: int, 
        booking_id: int, 
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Отправить уведомление об отмене бронирования
        """
        text = (
            f"❌ <b>Бронирование #{booking_id} отменено</b>\n\n"
        )
        
        if reason:
            text += f"Причина: {reason}\n\n"
            
        text += "Вы можете создать новое бронирование в любое время."
        
        return await self.send_message(chat_id, text)
    
    async def send_booking_reminder(
        self, 
        chat_id: int, 
        booking: BookingDetailResponse
    ) -> Dict[str, Any]:
        """
        Отправить напоминание о бронировании
        """
        text = (
            f"⏰ <b>Напоминание о бронировании #{booking.id}</b>\n\n"
            f"Ваше бронирование запланировано на <b>{booking.booking_time.strftime('%d.%m.%Y %H:%M')}</b>\n"
            f"Компания: <b>{booking.company_name or 'Не указано'}</b>\n"
            f"Услуга: <b>{booking.service_name or 'Не указано'}</b>"
        )
        
        # Кнопка для просмотра деталей или отмены
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "📋 Детали",
                        "callback_data": f"booking_details:{booking.id}"
                    },
                    {
                        "text": "❌ Отменить",
                        "callback_data": f"cancel_booking:{booking.id}"
                    }
                ]
            ]
        }
        
        return await self.send_message(chat_id, text, reply_markup=reply_markup)
    
    async def process_update(self, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обработать обновление от Telegram
        
        В реальном проекте здесь была бы логика работы нейроассистента Карл,
        который бы анализировал запросы пользователей и помогал с бронированием услуг
        """
        # Проверяем наличие сообщения
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"]
            
            # Простая логика для демонстрации
            if text.startswith("/start"):
                return await self.send_message(
                    chat_id,
                    "👋 Привет! Я нейроассистент <b>Карл</b>.\n\n"
                    "Я помогу вам найти подходящие услуги и забронировать их. "
                    "Расскажите, что вы ищете, или воспользуйтесь командами ниже.",
                    reply_markup={
                        "keyboard": [
                            [{"text": "🔍 Найти услуги"}, {"text": "📅 Мои бронирования"}],
                            [{"text": "🏢 Популярные компании"}, {"text": "❓ Помощь"}]
                        ],
                        "resize_keyboard": True
                    }
                )
            
            # Пример распознавания простой команды для поиска
            elif "найти" in text.lower() or "поиск" in text.lower():
                return await self.send_message(
                    chat_id,
                    "🔍 <b>Что вы хотите найти?</b>\n\n"
                    "Например, вы можете написать:\n"
                    "- Парикмахерская в центре\n"
                    "- Стрижка недорого\n"
                    "- Маникюр завтра утром\n\n"
                    "Или выберите категорию:",
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {"text": "💇‍♀️ Красота", "callback_data": "search_category:beauty"},
                                {"text": "🍽️ Рестораны", "callback_data": "search_category:restaurant"}
                            ],
                            [
                                {"text": "👨‍⚕️ Медицина", "callback_data": "search_category:medical"},
                                {"text": "🛠️ Ремонт", "callback_data": "search_category:repair"}
                            ]
                        ]
                    }
                )
                
            # В реальном проекте здесь был бы обработчик естественного языка,
            # который определял бы намерения пользователя и предлагал варианты
            # бронирования услуг
            else:
                return await self.send_message(
                    chat_id,
                    "Я пока не умею отвечать на такие сообщения. "
                    "Попробуйте воспользоваться командами или напишите более конкретный запрос."
                )
                
        # Обработка коллбеков от inline-кнопок
        elif "callback_query" in update:
            callback_id = update["callback_query"]["id"]
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            callback_data = update["callback_query"]["data"]
            
            # Простая обработка для демонстрации
            if callback_data.startswith("search_category:"):
                category = callback_data.split(":")[1]
                return await self.send_message(
                    chat_id,
                    f"Вот что я нашел в категории <b>{category}</b>:\n\n"
                    "В данный момент это демо-версия, поэтому список ограничен. "
                    "В полной версии здесь будут результаты поиска."
                )
            
            elif callback_data.startswith("booking_details:"):
                booking_id = callback_data.split(":")[1]
                return await self.send_message(
                    chat_id,
                    f"Детали бронирования #{booking_id}:\n\n"
                    "В данный момент это демо-версия, поэтому детали не доступны. "
                    "В полной версии здесь будет информация о бронировании."
                )
                
        return None 