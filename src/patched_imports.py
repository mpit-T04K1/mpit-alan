"""
Патчер для импортов.
Этот модуль содержит функции для автоматического исправления проблем с импортами
при запуске приложения.
"""
import sys
import types
import logging

logger = logging.getLogger(__name__)


def apply_patches():
    """Применяет все патчи для исправления проблем с импортами"""
    patch_database_modules()
    logger.info("Патчи для импортов успешно применены")


def patch_database_modules():
    """
    Патчит модули базы данных для обеспечения единой точки доступа к компонентам.
    """
    try:
        # Создаем базовую структуру для src.database
        if "src.database" not in sys.modules:
            db_module = types.ModuleType("src.database")
            sys.modules["src.database"] = db_module
            
        # Импортируем src.database.py, что создаст настоящий модуль src.database
        import src.database
        
        # Теперь импортируем компоненты после того, как основной модуль создан
        from src.db_adapter import Base, get_db, check_db_connection, engine, async_session_factory
        
        # Создаем патчи для других модулей
        modules_to_patch = {
            "src.db": {
                "Base": Base,
                "get_db": get_db,
                "check_db_connection": check_db_connection,
                "engine": engine,
                "async_session_factory": async_session_factory
            },
            "src.db.database": {
                "Base": Base,
                "get_db": get_db,
                "check_db_connection": check_db_connection,
                "engine": engine,
                "async_session_factory": async_session_factory
            },
            "src.adapters.database.session": {
                "Base": Base,
                "get_db": get_db,
                "check_db_connection": check_db_connection,
                "engine": engine,
                "async_session_maker": async_session_factory,
                "async_session_factory": async_session_factory
            }
        }

        # Применяем патчи
        for module_name, attrs in modules_to_patch.items():
            if module_name not in sys.modules:
                # Создаем модуль, если он еще не загружен
                module = types.ModuleType(module_name)
                sys.modules[module_name] = module

            # Обновляем атрибуты модуля
            module = sys.modules[module_name]
            for attr_name, attr_value in attrs.items():
                setattr(module, attr_name, attr_value)

        logger.info("Модули базы данных успешно пропатчены")
    except Exception as e:
        logger.error(f"Ошибка при патче модулей базы данных: {e}")


# Автоматическое применение патчей при импорте модуля
apply_patches() 