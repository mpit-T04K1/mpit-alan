from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.repositories.company import CompanyRepository
from src.adapters.database.repositories.user import UserRepository
from src.adapters.database.repositories.service import ServiceRepository
from src.adapters.database.repositories.booking import BookingRepository
from src.adapters.database.repositories.analytics import AnalyticsRepository


class RepositoriesGatewayProtocol(Protocol):
    """Протокол Gateway для всех репозиториев"""
    
    user: UserRepository
    company: CompanyRepository
    service: ServiceRepository
    booking: BookingRepository
    analytics: AnalyticsRepository


class RepositoriesGateway:
    """Gateway для доступа ко всем репозиториям"""
    
    def __init__(self, session: AsyncSession):
        self.user = UserRepository(session)
        self.company = CompanyRepository(session)
        self.service = ServiceRepository(session)
        self.booking = BookingRepository(session)
        self.analytics = AnalyticsRepository(session) 