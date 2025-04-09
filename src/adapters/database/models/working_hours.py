# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.working_hours import WorkingHours, DayOfWeek

# Классы WorkingHours и DayOfWeek теперь импортируются напрямую из src/models/working_hours.py
# и переэкспортируются здесь для обратной совместимости