from fastapi import APIRouter

from src.api.endpoints import (
    auth,
    users,
    companies,
    services,
    bookings,
    moderation,
    analytics,
    notifications,
    schedule,
)


# Создаем главный роутер API v1
api_router_v1 = APIRouter()

# Регистрируем все маршруты
api_router_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router_v1.include_router(users.router, prefix="/users", tags=["users"])
api_router_v1.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router_v1.include_router(services.router, prefix="/services", tags=["services"])
api_router_v1.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router_v1.include_router(moderation.router, prefix="/moderation", tags=["moderation"])
api_router_v1.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router_v1.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router_v1.include_router(schedule.router, prefix="/schedule", tags=["schedule"]) 