from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.schedule import router as schedule_router
from src.api.endpoints.users import router as users_router
from src.api.endpoints.companies import router as companies_router
from src.api.endpoints.services import router as services_router
from src.api.endpoints.bookings import router as bookings_router
from src.api.endpoints.moderation import router as moderation_router
from src.api.endpoints.analytics import router as analytics_router
from src.api.endpoints.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "schedule_router",
    "users_router",
    "companies_router",
    "services_router",
    "bookings_router",
    "moderation_router",
    "analytics_router",
    "notifications_router",
] 