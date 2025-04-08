from typing import Protocol


class UnitOfWorkProtocol(Protocol):
    """Протокол Unit of Work для работы с репозиториями и внешними сервисами"""

    async def __aenter__(self):
        """Вход в контекстный менеджер"""
        ...

    async def __aexit__(self, *args):
        """Выход из контекстного менеджера"""
        ...

    async def commit(self):
        """Сохранение изменений в БД"""
        ...

    async def rollback(self):
        """Откат изменений в БД"""
        ... 