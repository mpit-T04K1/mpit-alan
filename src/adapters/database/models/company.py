# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.company import Company
from src.models.moderation import ModerationStatus

# Перечисление бизнес-типов (для обратной совместимости)
from enum import Enum

class BusinessType(str, Enum):
    BEAUTY_SALON = "beauty_salon"
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    MEDICAL = "medical"
    FITNESS = "fitness"
    REPAIR = "repair"
    LEGAL = "legal"
    EDUCATION = "education"
    OTHER = "other"