from logging.config import fileConfig
import os
from pathlib import Path
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Добавляем корневую директорию проекта в sys.path
base_dir = Path(__file__).parent.parent
sys.path.append(str(base_dir))

# Импортируем модели и базу из адаптера
from src.db_adapter import Base

# Явно импортируем все модели, чтобы они были в метаданных
from src.models.user import User, UserRole
from src.models.company import Company
from src.models.booking import Booking
from src.models.location import Location
from src.models.working_hours import WorkingHours
from src.models.service import Service
from src.models.media import Media
from src.models.analytics import Analytics
from src.models.schedule import Schedule, TimeSlot
from src.models.moderation import ModerationStatus, ModerationAction, ModerationRecord

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/qwertytown")
# Для Alembic нужен синхронный URL, заменяем asyncpg на psycopg
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg")
# Обновляем URL в конфигурации
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Включаем сравнение типов данных
        compare_type=True,
        # Включаем сравнение ограничений
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Включаем сравнение типов данных
            compare_type=True,
            # Включаем сравнение ограничений
            compare_server_default=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 