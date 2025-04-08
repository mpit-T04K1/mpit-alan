#!/bin/bash
# fix_container.sh - Скрипт для исправления путей к шаблонам в запущенном контейнере

echo "Останавливаем текущие контейнеры..."
docker compose down

echo "======================================================"
echo "Создаём временный Dockerfile для исправления проблемы..."
echo "======================================================"

cat > Dockerfile.fixed << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание необходимых директорий
RUN mkdir -p /app/src/db /app/src/database /app/src/adapters/database /app/alembic/versions

# Копирование файлов миграций
COPY alembic.ini migrations.py /app/
COPY alembic/env.py alembic/script.py.mako /app/alembic/
COPY alembic/versions/ /app/alembic/versions/

# Копирование кода приложения
COPY . .

# Исправляем пути к шаблонам
RUN sed -i 's/TEMPLATES_DIR: str = "templates"/TEMPLATES_DIR: str = "\/app\/src\/templates"/' /app/src/core/config.py

# Запуск приложения
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
EOF

echo "======================================================"
echo "Создаём временный .env файл с исправленными настройками..."
echo "======================================================"

cat > .env.fixed << 'EOF'
# Основные настройки
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
DEBUG=true
ENVIRONMENT=development

# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/qwertytown

# Пути к файлам
TEMPLATES_DIR=/app/src/templates

# Сервер
HOST=0.0.0.0
PORT=8080
EOF

echo "Копируем исправленные файлы..."
cp .env.fixed .env
cp Dockerfile.fixed Dockerfile

echo "Перезапускаем с исправленными настройками..."
docker compose up -d --build

echo "Ожидаем 20 секунд, пока база данных запускается..."
sleep 20

echo "Применяем миграции..."
docker compose exec app python migrations.py

echo "Исправляем проблему с типом enum в коде..."
docker compose exec app bash -c "cat > /app/src/fix_enum.py << EOF
#!/usr/bin/env python3
from sqlalchemy import text
from src.database import get_session
import asyncio

async def fix_enum_issue():
    async with get_session() as session:
        # Создаем временную роль для админа 
        query = text(\"\"\"
        INSERT INTO users (email, hashed_password, first_name, last_name, is_active, role, is_superuser, created_at, updated_at)
        VALUES ('admin@example.com', '\$2b\$12\$NJNBnnbYFvuyZu.KnJqAN.e7IpYdfJSyyu0fYr5WokU8a.EeA6uaW', 'Admin', 'User', true, 'admin'::userrole, true, now(), now())
        ON CONFLICT (email) DO NOTHING;
        \"\"\")
        await session.execute(query)
        await session.commit()
        print('Admin user created/updated successfully')

if __name__ == '__main__':
    asyncio.run(fix_enum_issue())
EOF"

echo "Запускаем скрипт для исправления проблемы с enum..."
docker compose exec app python /app/src/fix_enum.py

echo "========================================================================"
echo "Готово! Приложение доступно по следующим адресам:"
echo "========================================================================"
echo "Главная страница: http://localhost:8080/"
echo "Документация API: http://localhost:8080/docs"
echo "Тестовый API: http://localhost:8080/api/test-api"
echo "Бизнес-модуль: http://localhost:8080/business"
echo "Панель администратора: http://localhost:8080/admin"
echo "Аналитика: http://localhost:8080/admin/analytics"
echo "========================================================================"
echo "Для входа используйте:"
echo "Email: admin@example.com"
echo "Password: password123"
echo "========================================================================" 