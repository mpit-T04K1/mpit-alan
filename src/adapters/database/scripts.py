import logging
from sqlalchemy import text

from .session import engine

logger = logging.getLogger(__name__)


async def check_db_connection() -> bool:
    """Проверка соединения с базой данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке соединения с БД: {e}")
        return False

async def create_default_admin():
    """
    Создает администратора по умолчанию, если он не существует
    Email: admin@admin.ru
    Пароль: admin
    """
    from sqlalchemy import text
    from datetime import datetime
    from src.utils.security import get_password_hash
    
    try:
        logger.info("Проверка наличия администратора по умолчанию...")
        
        # Используем прямой SQL запрос для проверки существования администратора
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT COUNT(*) FROM users WHERE email = :email"),
                {"email": "admin@admin.ru"}
            )
            admin_exists = result.scalar()
        
        if admin_exists:
            logger.info("Администратор по умолчанию уже существует")
            return

        # Создаем администратора через прямой SQL запрос с литеральным значением роли
        hashed_password = get_password_hash("admin")
        
        # SQL-запрос с явно указанным литералом 'admin' для поля role
        async with engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO users 
                (email, hashed_password, first_name, last_name, is_active, role, is_superuser, created_at, updated_at)
                VALUES 
                (:email, :password, :first_name, :last_name, :is_active, 'admin', :is_superuser, :created_at, :updated_at)
                """),
                {
                    "email": "admin@admin.ru",
                    "password": hashed_password,
                    "first_name": "Admin",
                    "last_name": "User",
                    "is_active": True,
                    "is_superuser": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
        logger.info("Администратор по умолчанию создан успешно через прямой SQL запрос")
        
    except Exception as e:
        logger.error(f"Ошибка при создании администратора по умолчанию: {e}")
        # Не выбрасываем исключение, чтобы приложение продолжило работу 