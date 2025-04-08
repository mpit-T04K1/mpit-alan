from .auth import router as auth_router
from .schedule import router as schedule_router
from .users import router as users_router
from .companies import router as companies_router
from .services import router as services_router
from .bookings import router as bookings_router
from .moderation import router as moderation_router
from .analytics import router as analytics_router
from .notifications import router as notifications_router

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
