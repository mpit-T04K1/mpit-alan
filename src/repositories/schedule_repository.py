from typing import List, Optional, Dict, Any
from datetime import datetime, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract

from src.models.schedule import Schedule, TimeSlot
from src.schemas.schedule import ScheduleCreate, ScheduleUpdate, TimeSlotCreate, TimeSlotUpdate


class ScheduleRepository:
    """Репозиторий для работы с расписанием"""
    
    @staticmethod
    def create_schedule(db: Session, schedule_data: ScheduleCreate) -> Schedule:
        """Создание нового расписания"""
        # Преобразование строковых представлений времени в объекты time
        opening_time = datetime.strptime(schedule_data.opening_time, "%H:%M").time() if schedule_data.opening_time else None
        closing_time = datetime.strptime(schedule_data.closing_time, "%H:%M").time() if schedule_data.closing_time else None
        break_start_time = datetime.strptime(schedule_data.break_start_time, "%H:%M").time() if schedule_data.break_start_time else None
        break_end_time = datetime.strptime(schedule_data.break_end_time, "%H:%M").time() if schedule_data.break_end_time else None
        
        # Преобразование даты для особого дня
        specific_date = datetime.strptime(schedule_data.specific_date, "%Y-%m-%d") if schedule_data.specific_date else None
        
        # Создание объекта расписания
        db_schedule = Schedule(
            company_id=schedule_data.company_id,
            day_of_week=schedule_data.day_of_week,
            is_working_day=schedule_data.is_working_day,
            opening_time=opening_time,
            closing_time=closing_time,
            break_start_time=break_start_time,
            break_end_time=break_end_time,
            additional_info=schedule_data.additional_info,
            is_special_day=schedule_data.is_special_day,
            specific_date=specific_date,
            note=schedule_data.note
        )
        
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        
        return db_schedule
    
    @staticmethod
    def update_schedule(db: Session, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[Schedule]:
        """Обновление расписания"""
        db_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not db_schedule:
            return None
        
        # Обновляем только те поля, которые переданы и не None
        update_data = schedule_data.dict(exclude_unset=True)
        
        # Преобразование времени из строки в объекты time
        for field in ['opening_time', 'closing_time', 'break_start_time', 'break_end_time']:
            if field in update_data and update_data[field]:
                update_data[field] = datetime.strptime(update_data[field], "%H:%M").time()
        
        # Преобразование даты из строки
        if 'specific_date' in update_data and update_data['specific_date']:
            update_data['specific_date'] = datetime.strptime(update_data['specific_date'], "%Y-%m-%d")
        
        for key, value in update_data.items():
            setattr(db_schedule, key, value)
        
        db.commit()
        db.refresh(db_schedule)
        
        return db_schedule
    
    @staticmethod
    def delete_schedule(db: Session, schedule_id: int) -> bool:
        """Удаление расписания"""
        db_schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not db_schedule:
            return False
        
        db.delete(db_schedule)
        db.commit()
        
        return True
    
    @staticmethod
    def get_schedule_by_id(db: Session, schedule_id: int) -> Optional[Schedule]:
        """Получение расписания по ID"""
        return db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    @staticmethod
    def get_company_schedules(db: Session, company_id: int) -> List[Schedule]:
        """Получение всех расписаний компании"""
        return db.query(Schedule).filter(Schedule.company_id == company_id).all()
    
    @staticmethod
    def get_company_week_schedule(db: Session, company_id: int) -> Dict[int, Schedule]:
        """Получение расписания компании на неделю"""
        # Получаем стандартное расписание на неделю
        week_schedules = db.query(Schedule).filter(
            Schedule.company_id == company_id,
            Schedule.is_special_day == False
        ).all()
        
        # Преобразуем в словарь для удобного доступа
        schedule_by_day = {schedule.day_of_week: schedule for schedule in week_schedules}
        
        return schedule_by_day
    
    @staticmethod
    def get_company_special_day_schedules(db: Session, company_id: int, 
                                         start_date: datetime, end_date: datetime) -> List[Schedule]:
        """Получение особых дней для компании в заданном диапазоне дат"""
        return db.query(Schedule).filter(
            Schedule.company_id == company_id,
            Schedule.is_special_day == True,
            Schedule.specific_date >= start_date,
            Schedule.specific_date <= end_date
        ).all()
    
    @staticmethod
    def get_schedule_for_date(db: Session, company_id: int, date: datetime) -> Optional[Schedule]:
        """
        Получение расписания на конкретную дату.
        Сначала проверяет, есть ли особый день на эту дату, 
        если нет - возвращает стандартное расписание для дня недели.
        """
        # Проверяем, есть ли особый день на эту дату
        special_day = db.query(Schedule).filter(
            Schedule.company_id == company_id,
            Schedule.is_special_day == True,
            Schedule.specific_date == date.date()  # Сравниваем только дату
        ).first()
        
        if special_day:
            return special_day
        
        # Если особого дня нет, возвращаем стандартное расписание для этого дня недели
        day_of_week = date.weekday()  # 0 - понедельник, 6 - воскресенье
        
        return db.query(Schedule).filter(
            Schedule.company_id == company_id,
            Schedule.is_special_day == False,
            Schedule.day_of_week == day_of_week
        ).first()


class TimeSlotRepository:
    """Репозиторий для работы с временными слотами"""
    
    @staticmethod
    def create_time_slot(db: Session, slot_data: TimeSlotCreate) -> TimeSlot:
        """Создание нового временного слота"""
        # Преобразуем строковое представление времени в datetime
        start_time = datetime.strptime(slot_data.start_time, "%Y-%m-%d %H:%M")
        
        db_time_slot = TimeSlot(
            service_id=slot_data.service_id,
            start_time=start_time,
            duration=slot_data.duration,
            max_clients=slot_data.max_clients,
            is_blocked=slot_data.is_blocked,
            block_reason=slot_data.block_reason,
            status="available" if not slot_data.is_blocked else "blocked"
        )
        
        db.add(db_time_slot)
        db.commit()
        db.refresh(db_time_slot)
        
        return db_time_slot
    
    @staticmethod
    def update_time_slot(db: Session, slot_id: int, slot_data: TimeSlotUpdate) -> Optional[TimeSlot]:
        """Обновление временного слота"""
        db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
        
        if not db_time_slot:
            return None
        
        # Обновляем только те поля, которые переданы и не None
        update_data = slot_data.dict(exclude_unset=True, exclude_none=True)
        
        # Преобразуем строковое представление времени в datetime
        if 'start_time' in update_data and update_data['start_time']:
            update_data['start_time'] = datetime.strptime(update_data['start_time'], "%Y-%m-%d %H:%M")
        
        # Если изменился статус блокировки, обновляем также статус слота
        if 'is_blocked' in update_data:
            if update_data['is_blocked']:
                update_data['status'] = "blocked"
            elif db_time_slot.status == "blocked":
                # Если слот был заблокирован, а теперь разблокирован
                update_data['status'] = "available" if db_time_slot.booked_clients == 0 else (
                    "booked" if db_time_slot.booked_clients >= db_time_slot.max_clients else "partially_booked"
                )
        
        for key, value in update_data.items():
            setattr(db_time_slot, key, value)
        
        db.commit()
        db.refresh(db_time_slot)
        
        return db_time_slot
    
    @staticmethod
    def delete_time_slot(db: Session, slot_id: int) -> bool:
        """Удаление временного слота"""
        db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
        
        if not db_time_slot:
            return False
        
        db.delete(db_time_slot)
        db.commit()
        
        return True
    
    @staticmethod
    def get_time_slot_by_id(db: Session, slot_id: int) -> Optional[TimeSlot]:
        """Получение временного слота по ID"""
        return db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    
    @staticmethod
    def get_service_time_slots(db: Session, service_id: int, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[TimeSlot]:
        """Получение временных слотов для услуги"""
        query = db.query(TimeSlot).filter(TimeSlot.service_id == service_id)
        
        if start_date:
            query = query.filter(TimeSlot.start_time >= start_date)
        
        if end_date:
            query = query.filter(TimeSlot.start_time <= end_date)
        
        return query.order_by(TimeSlot.start_time).all()
    
    @staticmethod
    def get_available_time_slots(db: Session, service_id: int, 
                                start_date: datetime, end_date: datetime) -> List[TimeSlot]:
        """Получение доступных для бронирования временных слотов"""
        return db.query(TimeSlot).filter(
            TimeSlot.service_id == service_id,
            TimeSlot.start_time >= start_date,
            TimeSlot.start_time <= end_date,
            TimeSlot.is_blocked == False,
            TimeSlot.status.in_(["available", "partially_booked"])
        ).order_by(TimeSlot.start_time).all()
    
    @staticmethod
    def book_time_slot(db: Session, slot_id: int) -> Optional[TimeSlot]:
        """Бронирование слота (увеличение счетчика клиентов и обновление статуса)"""
        db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
        
        if not db_time_slot or db_time_slot.is_blocked or db_time_slot.status == "booked":
            return None
        
        # Увеличиваем счетчик клиентов
        db_time_slot.booked_clients += 1
        
        # Обновляем статус
        if db_time_slot.booked_clients >= db_time_slot.max_clients:
            db_time_slot.status = "booked"
        else:
            db_time_slot.status = "partially_booked"
        
        db.commit()
        db.refresh(db_time_slot)
        
        return db_time_slot
    
    @staticmethod
    def cancel_booking(db: Session, slot_id: int) -> Optional[TimeSlot]:
        """Отмена бронирования (уменьшение счетчика клиентов и обновление статуса)"""
        db_time_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
        
        if not db_time_slot or db_time_slot.booked_clients == 0:
            return None
        
        # Уменьшаем счетчик клиентов
        db_time_slot.booked_clients -= 1
        
        # Обновляем статус
        if db_time_slot.booked_clients == 0:
            db_time_slot.status = "available"
        else:
            db_time_slot.status = "partially_booked"
        
        db.commit()
        db.refresh(db_time_slot)
        
        return db_time_slot
    
    @staticmethod
    def generate_time_slots(db: Session, service_id: int, 
                          start_date: datetime, end_date: datetime,
                          duration: int, interval: int,
                          max_clients: int = 1) -> List[TimeSlot]:
        """
        Генерация временных слотов для услуги на указанный период
        
        Args:
            service_id: ID услуги
            start_date: Начальная дата и время
            end_date: Конечная дата и время
            duration: Продолжительность слота в минутах
            interval: Интервал между началом слотов в минутах
            max_clients: Максимальное количество клиентов на слот
        
        Returns:
            Список созданных временных слотов
        """
        created_slots = []
        current_time = start_date
        
        while current_time <= end_date:
            # Создаем новый слот
            slot_data = TimeSlotCreate(
                service_id=service_id,
                start_time=current_time.strftime("%Y-%m-%d %H:%M"),
                duration=duration,
                max_clients=max_clients,
                is_blocked=False
            )
            
            db_slot = TimeSlotRepository.create_time_slot(db, slot_data)
            created_slots.append(db_slot)
            
            # Переходим к следующему временному интервалу
            current_time += timedelta(minutes=interval)
        
        return created_slots
    
    @staticmethod
    def generate_slots_from_schedule(db: Session, service_id: int, 
                                    schedules: Dict[int, Schedule],
                                    special_days: List[Schedule],
                                    start_date: datetime, end_date: datetime,
                                    duration: int, interval: int,
                                    max_clients: int = 1) -> List[TimeSlot]:
        """
        Генерация временных слотов на основе расписания компании
        
        Args:
            service_id: ID услуги
            schedules: Словарь с расписанием на неделю по дням недели
            special_days: Список особых дней с особым расписанием
            start_date: Начальная дата
            end_date: Конечная дата
            duration: Продолжительность слота в минутах
            interval: Интервал между началом слотов в минутах
            max_clients: Максимальное количество клиентов на слот
        
        Returns:
            Список созданных временных слотов
        """
        created_slots = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Словарь особых дней для быстрого доступа
        special_days_dict = {
            special_day.specific_date.strftime("%Y-%m-%d"): special_day 
            for special_day in special_days if special_day.specific_date
        }
        
        # Перебираем все дни в указанном диапазоне
        while current_date.date() <= end_date.date():
            day_of_week = current_date.weekday()
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Проверяем, есть ли особый день на эту дату
            if date_str in special_days_dict:
                schedule = special_days_dict[date_str]
            else:
                # Иначе берем стандартное расписание для этого дня недели
                schedule = schedules.get(day_of_week)
            
            # Если есть расписание и это рабочий день
            if schedule and schedule.is_working_day and schedule.opening_time and schedule.closing_time:
                # Создаем datetime объекты для начала и конца рабочего дня
                day_start = datetime.combine(current_date.date(), schedule.opening_time)
                day_end = datetime.combine(current_date.date(), schedule.closing_time)
                
                # Если есть перерыв, учитываем его
                break_start = None
                break_end = None
                
                if schedule.break_start_time and schedule.break_end_time:
                    break_start = datetime.combine(current_date.date(), schedule.break_start_time)
                    break_end = datetime.combine(current_date.date(), schedule.break_end_time)
                
                # Генерируем слоты для этого дня
                time_pointer = day_start
                
                while time_pointer < day_end:
                    # Проверка, не попадает ли слот на перерыв
                    slot_end = time_pointer + timedelta(minutes=duration)
                    
                    # Если слот пересекается с перерывом, пропускаем его
                    if break_start and break_end and (
                        (time_pointer < break_end and slot_end > break_start) or
                        (time_pointer >= break_start and time_pointer < break_end)
                    ):
                        # Переходим через перерыв, если мы в начале перерыва
                        if time_pointer < break_start:
                            time_pointer = break_end
                        else:
                            time_pointer += timedelta(minutes=interval)
                        continue
                    
                    # Проверяем, что слот полностью помещается в рабочий день
                    if slot_end <= day_end:
                        # Создаем новый слот
                        slot_data = TimeSlotCreate(
                            service_id=service_id,
                            start_time=time_pointer.strftime("%Y-%m-%d %H:%M"),
                            duration=duration,
                            max_clients=max_clients,
                            is_blocked=False
                        )
                        
                        db_slot = TimeSlotRepository.create_time_slot(db, slot_data)
                        created_slots.append(db_slot)
                    
                    # Переходим к следующему временному интервалу
                    time_pointer += timedelta(minutes=interval)
            
            # Переходим к следующему дню
            current_date += timedelta(days=1)
        
        return created_slots 