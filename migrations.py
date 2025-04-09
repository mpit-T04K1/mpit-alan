"""
Скрипт для запуска миграций базы данных.
"""
import asyncio
import os
import sys
from pathlib import Path
import logging

from alembic.config import Config
from alembic import command

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к файлу конфигурации alembic.ini
BASE_DIR = Path(__file__).parent
alembic_cfg = Config(BASE_DIR / "alembic.ini")

# Устанавливаем URL базы данных из переменной окружения
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/qwertytown")
# Для Alembic нужен синхронный URL
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg")
alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations():
    """Запускает миграции базы данных."""
    try:
        logger.info("Применяем миграции базы данных...")
        
        # Сначала сбрасываем миграции, если они не работают
        try:
            # Удаляем таблицу alembic_version
            from sqlalchemy import create_engine, text
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                logger.info("Сброшены данные о миграциях")
        except Exception as e:
            logger.warning(f"Не удалось сбросить данные о миграциях: {e}")
        
        # Применяем миграции последовательно
        try:
            # Применяем initial_migration
            logger.info("Применяем initial_migration...")
            command.upgrade(alembic_cfg, "2023_initial_migration")
        except Exception as e:
            logger.error(f"Ошибка при применении initial_migration: {e}")
            
        try:
            # Применяем schedule_tables
            logger.info("Применяем schedule_tables...")
            command.upgrade(alembic_cfg, "2023_schedule_tables")
        except Exception as e:
            logger.error(f"Ошибка при применении schedule_tables: {e}")
            
        try:
            # Применяем moderation_tables
            logger.info("Применяем moderation_tables...")
            command.upgrade(alembic_cfg, "2023_moderation_tables")
        except Exception as e:
            logger.error(f"Ошибка при применении moderation_tables: {e}")
            
        try:
            # Применяем initial_tables (если он ещё не применён)
            logger.info("Применяем initial_tables...")
            command.upgrade(alembic_cfg, "2023_initial_tables")
        except Exception as e:
            logger.error(f"Ошибка при применении initial_tables: {e}")
            
        # Проверяем, что наиболее важные таблицы созданы
        from sqlalchemy import create_engine, text, inspect
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        required_tables = ['users', 'companies', 'services', 'bookings']
        missing_tables = [table for table in required_tables if table not in inspector.get_table_names()]
        
        if missing_tables:
            logger.error(f"Отсутствуют необходимые таблицы: {missing_tables}")
            # Если таблицы users нет, создаем её напрямую
            if 'users' in missing_tables:
                try:
                    logger.info("Создаем таблицу users напрямую...")
                    with engine.connect() as conn:
                        conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR NOT NULL UNIQUE,
                            hashed_password VARCHAR NOT NULL,
                            first_name VARCHAR,
                            last_name VARCHAR,
                            phone VARCHAR UNIQUE,
                            avatar VARCHAR,
                            is_active BOOLEAN NOT NULL DEFAULT TRUE,
                            role VARCHAR NOT NULL DEFAULT 'client',
                            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                            telegram_id VARCHAR(50),
                            telegram_username VARCHAR(100)
                        )
                        """))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)"))
                        logger.info("Таблица users создана успешно")
                except Exception as e:
                    logger.error(f"Ошибка при создании таблицы users: {e}")
            
            return False
        
        logger.info("Миграции успешно применены.")
        return True
    except Exception as e:
        logger.error(f"Ошибка при применении миграций: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    if not success:
        sys.exit(1) 