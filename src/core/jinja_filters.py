from datetime import datetime, date
import json
from typing import Any, Dict, List, Union

def configure_jinja_filters(app) -> None:
    """
    Настройка фильтров Jinja2
    
    Args:
        app: Экземпляр FastAPI приложения
    """
    from fastapi.templating import Jinja2Templates
    
    # Получаем экземпляр Jinja2Templates из FastAPI
    templates = app.state.templates
    
    # Регистрация фильтров
    templates.env.filters["datetime"] = format_datetime
    templates.env.filters["date"] = format_date
    templates.env.filters["time"] = format_time
    templates.env.filters["currency"] = format_currency
    templates.env.filters["phone"] = format_phone
    templates.env.filters["tojson"] = to_json
    templates.env.filters["file_size"] = format_file_size


def format_datetime(value: Union[datetime, str], format: str = "%d.%m.%Y %H:%M") -> str:
    """
    Форматирование даты и времени
    
    Args:
        value: Значение даты (строка или объект datetime)
        format: Формат вывода
        
    Returns:
        Отформатированная строка
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    
    return value.strftime(format)


def format_date(value: Union[datetime, date, str], format: str = "%d.%m.%Y") -> str:
    """
    Форматирование даты
    
    Args:
        value: Значение даты (строка, объект datetime или date)
        format: Формат вывода
        
    Returns:
        Отформатированная строка
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    
    return value.strftime(format)


def format_time(value: Union[datetime, str], format: str = "%H:%M") -> str:
    """
    Форматирование времени
    
    Args:
        value: Значение времени (строка или объект datetime)
        format: Формат вывода
        
    Returns:
        Отформатированная строка
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    
    return value.strftime(format)


def format_currency(value: Union[float, int], currency: str = "₽", decimals: int = 2) -> str:
    """
    Форматирование валюты
    
    Args:
        value: Числовое значение
        currency: Символ валюты
        decimals: Количество знаков после запятой
        
    Returns:
        Отформатированная строка
    """
    if value is None:
        return ""
    
    try:
        return f"{float(value):,.{decimals}f} {currency}".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return str(value)


def format_phone(value: str) -> str:
    """
    Форматирование телефонного номера
    
    Args:
        value: Номер телефона
        
    Returns:
        Отформатированная строка
    """
    if not value:
        return ""
    
    # Удаляем все нецифровые символы
    digits = ''.join(filter(str.isdigit, value))
    
    if len(digits) == 11 and digits.startswith(('7', '8')):
        # Форматируем как российский номер
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    
    return value


def to_json(value: Any) -> str:
    """
    Преобразование объекта в JSON строку
    
    Args:
        value: Объект для преобразования
        
    Returns:
        JSON строка
    """
    return json.dumps(value)


def format_file_size(size: int) -> str:
    """
    Форматирование размера файла
    
    Args:
        size: Размер в байтах
        
    Returns:
        Отформатированная строка
    """
    if size is None:
        return ""
    
    # Определяем единицы измерения
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    # Используем 1024 в качестве базы
    size_float = float(size)
    unit_index = 0
    
    while size_float >= 1024 and unit_index < len(units) - 1:
        size_float /= 1024
        unit_index += 1
    
    # Возвращаем форматированную строку
    if unit_index == 0:
        return f"{int(size_float)} {units[unit_index]}"
    else:
        return f"{size_float:.2f} {units[unit_index]}" 