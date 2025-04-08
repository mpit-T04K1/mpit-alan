"""
Пакет-обертка для импорта компонентов базы данных из адаптера.
"""
from src.db_adapter import (
    Base, 
    get_db, 
    check_db_connection, 
    engine, 
    async_session_factory
)

__all__ = [
    "Base", 
    "get_db", 
    "check_db_connection", 
    "engine", 
    "async_session_factory"
] 