from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import Schedule, TimeSlot
from src.schemas.schedule import ScheduleCreate, ScheduleUpdate, TimeSlotCreate, TimeSlotUpdate

class ScheduleService:
    """Сервис для работы с расписаниями и временными слотами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Методы для работы с расписаниями
    
    async def create_schedule(self, schedule_data: ScheduleCreate) -> Schedule:
        """Создать новое расписание"""
        new_schedule = Schedule(
            company_id=schedule_data.company_id,
            service_id=schedule_data.service_id,
            schedule_type=schedule_data.schedule_type,
            name=schedule_data.name,
            weekly_schedule=schedule_data.weekly_schedule,
            exceptions=schedule_data.exceptions,
            recurring_events=schedule_data.recurring_events,
            slot_duration=schedule_data.slot_duration,
            slot_interval=schedule_data.slot_interval,
            max_concurrent_bookings=schedule_data.max_concurrent_bookings,
            is_active=schedule_data.is_active
        )
        
        self.db.add(new_schedule)
        await self.db.commit()
        await self.db.refresh(new_schedule)
        return new_schedule
    
    async def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """Получить расписание по ID"""
        query = select(Schedule).where(Schedule.id == schedule_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_schedules(
        self, 
        company_id: int, 
        service_id: Optional[int] = None
    ) -> List[Schedule]:
        """Получить список расписаний для компании или услуги"""
        query = select(Schedule).where(Schedule.company_id == company_id)
        
        if service_id is not None:
            query = query.where(Schedule.service_id == service_id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_schedule(
        self, 
        schedule_id: int, 
        schedule_update: ScheduleUpdate
    ) -> Optional[Schedule]:
        """Обновить существующее расписание"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        update_data = schedule_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(schedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def delete_schedule(self, schedule_id: int) -> bool:
        """Удалить расписание"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        # Удаляем связанные временные слоты
        query = select(TimeSlot).where(TimeSlot.schedule_id == schedule_id)
        result = await self.db.execute(query)
        timeslots = result.scalars().all()
        
        for timeslot in timeslots:
            await self.db.delete(timeslot)
        
        await self.db.delete(schedule)
        await self.db.commit()
        return True
    
    # Методы для работы с временными слотами
    
    async def create_timeslot(self, timeslot_data: TimeSlotCreate) -> TimeSlot:
        """Создать новый временной слот"""
        new_timeslot = TimeSlot(
            schedule_id=timeslot_data.schedule_id,
            start_time=timeslot_data.start_time,
            end_time=timeslot_data.end_time,
            max_bookings=timeslot_data.max_bookings,
            is_available=timeslot_data.is_available,
            special_conditions=timeslot_data.special_conditions
        )
        
        self.db.add(new_timeslot)
        await self.db.commit()
        await self.db.refresh(new_timeslot)
        return new_timeslot
    
    async def get_timeslot(self, timeslot_id: int) -> Optional[TimeSlot]:
        """Получить временной слот по ID"""
        query = select(TimeSlot).where(TimeSlot.id == timeslot_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_timeslots(
        self, 
        schedule_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_available: Optional[bool] = None
    ) -> List[TimeSlot]:
        """Получить список временных слотов для расписания с фильтрацией"""
        query = select(TimeSlot).where(TimeSlot.schedule_id == schedule_id)
        
        if start_time:
            query = query.where(TimeSlot.start_time >= start_time)
        
        if end_time:
            query = query.where(TimeSlot.start_time <= end_time)
        
        if is_available is not None:
            query = query.where(TimeSlot.is_available == is_available)
        
        # Сортировка по времени начала
        query = query.order_by(TimeSlot.start_time)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_timeslot(
        self, 
        timeslot_id: int, 
        timeslot_update: TimeSlotUpdate
    ) -> Optional[TimeSlot]:
        """Обновить существующий временной слот"""
        timeslot = await self.get_timeslot(timeslot_id)
        if not timeslot:
            return None
        
        update_data = timeslot_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(timeslot, key, value)
        
        await self.db.commit()
        await self.db.refresh(timeslot)
        return timeslot
    
    async def delete_timeslot(self, timeslot_id: int) -> bool:
        """Удалить временной слот"""
        timeslot = await self.get_timeslot(timeslot_id)
        if not timeslot:
            return False
        
        await self.db.delete(timeslot)
        await self.db.commit()
        return True
    
    # Методы для генерации временных слотов
    
    async def generate_timeslots(
        self,
        schedule_id: int,
        start_date: datetime,
        end_date: datetime,
        override_existing: bool = False
    ) -> Dict[str, int]:
        """Сгенерировать временные слоты на основе расписания"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return {"created": 0, "skipped": 0}
        
        # Если нужно удалить существующие слоты в указанном диапазоне
        if override_existing:
            await self._delete_existing_slots(schedule_id, start_date, end_date)
        
        # Инициализация счетчиков для результата
        created_count = 0
        skipped_count = 0
        
        # Проходим по каждому дню в указанном диапазоне
        current_date = start_date
        while current_date <= end_date:
            # Получаем день недели (0 - понедельник, 6 - воскресенье)
            weekday = current_date.weekday()
            weekday_name = self._get_weekday_name(weekday)
            
            # Проверяем, есть ли этот день в еженедельном расписании
            if weekday_name in schedule.weekly_schedule:
                day_schedule = schedule.weekly_schedule[weekday_name]
                
                # Проверяем, является ли день рабочим
                if day_schedule.get("is_working_day", True):
                    # Проверяем наличие исключений для этой даты
                    exception = self._find_exception_for_date(schedule, current_date)
                    
                    if exception and not exception.get("is_working_day", True):
                        # Если это исключение и день не рабочий, пропускаем
                        current_date += timedelta(days=1)
                        continue
                    
                    # Определяем время начала и окончания работы
                    start_time_str = exception.get("start", day_schedule.get("start")) if exception else day_schedule.get("start")
                    end_time_str = exception.get("end", day_schedule.get("end")) if exception else day_schedule.get("end")
                    
                    if start_time_str and end_time_str:
                        # Создаем временные слоты для этого дня
                        day_slots_result = await self._create_day_slots(
                            schedule,
                            current_date,
                            start_time_str,
                            end_time_str,
                            override_existing
                        )
                        
                        created_count += day_slots_result["created"]
                        skipped_count += day_slots_result["skipped"]
            
            # Переходим к следующему дню
            current_date += timedelta(days=1)
        
        # Добавляем слоты для повторяющихся событий
        if schedule.recurring_events:
            events_result = await self._create_recurring_event_slots(
                schedule,
                start_date,
                end_date,
                override_existing
            )
            
            created_count += events_result["created"]
            skipped_count += events_result["skipped"]
        
        return {"created": created_count, "skipped": skipped_count}
    
    # Вспомогательные методы
    
    def _get_weekday_name(self, weekday: int) -> str:
        """Получить название дня недели по его номеру"""
        weekday_names = [
            "monday", "tuesday", "wednesday", "thursday", 
            "friday", "saturday", "sunday"
        ]
        return weekday_names[weekday]
    
    def _find_exception_for_date(
        self, 
        schedule: Schedule, 
        date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Найти исключение для указанной даты в расписании"""
        if not schedule.exceptions:
            return None
        
        date_str = date.strftime("%Y-%m-%d")
        
        for exception in schedule.exceptions:
            if exception.get("date") == date_str:
                return exception
        
        return None
    
    async def _delete_existing_slots(
        self, 
        schedule_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """Удалить существующие временные слоты в указанном диапазоне дат"""
        # Подготовим запрос для удаления
        query = select(TimeSlot).where(
            and_(
                TimeSlot.schedule_id == schedule_id,
                TimeSlot.start_time >= start_date,
                TimeSlot.start_time <= end_date.replace(hour=23, minute=59, second=59)
            )
        )
        
        result = await self.db.execute(query)
        slots_to_delete = result.scalars().all()
        count = len(slots_to_delete)
        
        for slot in slots_to_delete:
            await self.db.delete(slot)
        
        await self.db.commit()
        return count
    
    async def _create_day_slots(
        self,
        schedule: Schedule,
        day: datetime,
        start_time_str: str,
        end_time_str: str,
        check_existing: bool = True
    ) -> Dict[str, int]:
        """Создать временные слоты для одного дня"""
        created_count = 0
        skipped_count = 0
        
        # Парсим строки времени
        start_hour, start_minute = map(int, start_time_str.split(":"))
        end_hour, end_minute = map(int, end_time_str.split(":"))
        
        # Создаем datetime объекты для начала и конца рабочего дня
        day_start = day.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        day_end = day.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # Длительность и интервал слотов (в минутах)
        slot_duration = schedule.slot_duration
        slot_interval = schedule.slot_interval
        
        # Общая длительность слота с учетом интервала
        total_slot_duration = slot_duration + slot_interval
        
        # Генерируем временные слоты
        current_slot_start = day_start
        while current_slot_start + timedelta(minutes=slot_duration) <= day_end:
            # Конец текущего слота
            current_slot_end = current_slot_start + timedelta(minutes=slot_duration)
            
            # Проверяем, существует ли уже слот с таким временем
            if check_existing:
                existing_slot = await self._check_slot_exists(
                    schedule.id, 
                    current_slot_start, 
                    current_slot_end
                )
                
                if existing_slot:
                    skipped_count += 1
                else:
                    # Создаем новый слот
                    await self._create_slot(schedule, current_slot_start, current_slot_end)
                    created_count += 1
            else:
                # Создаем новый слот без проверки
                await self._create_slot(schedule, current_slot_start, current_slot_end)
                created_count += 1
            
            # Переходим к следующему слоту
            current_slot_start += timedelta(minutes=total_slot_duration)
        
        return {"created": created_count, "skipped": skipped_count}
    
    async def _create_recurring_event_slots(
        self,
        schedule: Schedule,
        start_date: datetime,
        end_date: datetime,
        check_existing: bool = True
    ) -> Dict[str, int]:
        """Создать временные слоты для повторяющихся событий"""
        if not schedule.recurring_events:
            return {"created": 0, "skipped": 0}
        
        created_count = 0
        skipped_count = 0
        
        # Проходим по каждому повторяющемуся событию
        for event in schedule.recurring_events:
            # Получаем информацию о событии
            event_name = event.get("name", "Recurring Event")
            event_days = event.get("days", [])
            event_start_time = event.get("start_time")
            event_end_time = event.get("end_time")
            event_start_date = event.get("start_date")
            event_end_date = event.get("end_date")
            
            # Если не указано время, пропускаем событие
            if not event_start_time or not event_end_time:
                continue
            
            # Парсим строки времени
            start_hour, start_minute = map(int, event_start_time.split(":"))
            end_hour, end_minute = map(int, event_end_time.split(":"))
            
            # Ограничиваем период события нашим диапазоном дат
            event_period_start = start_date
            event_period_end = end_date
            
            # Если указана начальная дата события и она позже нашей начальной даты
            if event_start_date:
                event_start_date_obj = datetime.strptime(event_start_date, "%Y-%m-%d")
                if event_start_date_obj > event_period_start:
                    event_period_start = event_start_date_obj
            
            # Если указана конечная дата события и она раньше нашей конечной даты
            if event_end_date:
                event_end_date_obj = datetime.strptime(event_end_date, "%Y-%m-%d")
                if event_end_date_obj < event_period_end:
                    event_period_end = event_end_date_obj
            
            # Получаем числовые значения дней недели
            weekday_numbers = []
            for day_name in event_days:
                weekday_numbers.append(self._get_weekday_number(day_name))
            
            # Проходим по каждому дню в нашем диапазоне
            current_date = event_period_start
            while current_date <= event_period_end:
                # Если текущий день входит в список дней для события
                if current_date.weekday() in weekday_numbers:
                    # Создаем datetime объекты для начала и конца события
                    event_slot_start = current_date.replace(
                        hour=start_hour, 
                        minute=start_minute, 
                        second=0, 
                        microsecond=0
                    )
                    event_slot_end = current_date.replace(
                        hour=end_hour, 
                        minute=end_minute, 
                        second=0, 
                        microsecond=0
                    )
                    
                    # Проверяем, существует ли уже слот с таким временем
                    if check_existing:
                        existing_slot = await self._check_slot_exists(
                            schedule.id, 
                            event_slot_start, 
                            event_slot_end
                        )
                        
                        if existing_slot:
                            skipped_count += 1
                        else:
                            # Создаем новый слот для события
                            special_conditions = {"event_name": event_name}
                            await self._create_slot(
                                schedule, 
                                event_slot_start, 
                                event_slot_end,
                                special_conditions
                            )
                            created_count += 1
                    else:
                        # Создаем новый слот без проверки
                        special_conditions = {"event_name": event_name}
                        await self._create_slot(
                            schedule, 
                            event_slot_start, 
                            event_slot_end,
                            special_conditions
                        )
                        created_count += 1
                
                # Переходим к следующему дню
                current_date += timedelta(days=1)
        
        return {"created": created_count, "skipped": skipped_count}
    
    def _get_weekday_number(self, weekday_name: str) -> int:
        """Получить номер дня недели по его названию"""
        weekday_dict = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        return weekday_dict.get(weekday_name.lower(), -1)
    
    async def _check_slot_exists(
        self, 
        schedule_id: int, 
        start_time: datetime, 
        end_time: datetime
    ) -> bool:
        """Проверить, существует ли уже временной слот с указанным временем"""
        query = select(TimeSlot).where(
            and_(
                TimeSlot.schedule_id == schedule_id,
                TimeSlot.start_time == start_time,
                TimeSlot.end_time == end_time
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().first() is not None
    
    async def _create_slot(
        self, 
        schedule: Schedule, 
        start_time: datetime, 
        end_time: datetime,
        special_conditions: Optional[Dict[str, Any]] = None
    ) -> TimeSlot:
        """Создать новый временной слот"""
        new_slot = TimeSlot(
            schedule_id=schedule.id,
            start_time=start_time,
            end_time=end_time,
            max_bookings=schedule.max_concurrent_bookings,
            is_available=True,
            special_conditions=special_conditions
        )
        
        self.db.add(new_slot)
        return new_slot 