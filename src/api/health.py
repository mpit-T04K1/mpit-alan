from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.database.session import check_db_connection
from src.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "app_name": settings.APP_NAME
    }


@router.get("/health/db")
async def db_health_check():
    """Проверка подключения к базе данных"""
    try:
        is_connected = await check_db_connection()
        if is_connected:
            return {"status": "ok", "database_connection": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        ) 