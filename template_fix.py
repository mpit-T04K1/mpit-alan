#!/usr/bin/env python3
# Файл для исправления путей к шаблонам в приложении
import os
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_templates_path():
    # Путь к фиксированному Dockerfile, который мы создадим
    dockerfile_path = "Dockerfile.fixed"
    
    # Новое содержимое Dockerfile с исправленным путем к шаблонам
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    libpq-dev \\
    && apt-get clean \\
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

# Определяем переменную окружения для правильного пути к шаблонам
ENV TEMPLATES_DIR=/app/src/templates

# Запуск приложения
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
"""
    
    # Создаем новый Dockerfile
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    logger.info(f"Создан файл {dockerfile_path} с исправленным путем к шаблонам")
    
    # Создаем файл .env.fixed с исправленными настройками
    env_path = ".env.fixed"
    env_content = """# Основные настройки
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
"""
    
    # Создаем новый .env файл
    with open(env_path, "w") as f:
        f.write(env_content)
    
    logger.info(f"Создан файл {env_path} с исправленными настройками")
    
    # Создаем скрипт для перезапуска с исправленными настройками
    restart_script = "restart_fixed.sh"
    restart_content = """#!/bin/bash
echo "Останавливаем текущие контейнеры..."
docker compose down

echo "Копируем исправленные файлы..."
cp .env.fixed .env
cp Dockerfile.fixed Dockerfile

echo "Перезапускаем с исправленными настройками..."
docker compose up -d --build

echo "Ожидаем 20 секунд, пока база данных запускается..."
sleep 20

echo "Применяем миграции..."
docker compose exec app python migrations.py

echo "Готово! Приложение доступно по адресу http://localhost:8080"
echo "Документация API: http://localhost:8080/docs"
echo "Тестовый API: http://localhost:8080/api/test-api"
"""
    
    # Создаем скрипт для перезапуска
    with open(restart_script, "w") as f:
        f.write(restart_content)
    
    # Делаем скрипт исполняемым
    os.chmod(restart_script, 0o755)
    
    logger.info(f"Создан скрипт {restart_script} для перезапуска с исправленными настройками")
    
    # Инструкция для пользователя
    print("\n" + "="*80)
    print("ИНСТРУКЦИЯ ПО ИСПРАВЛЕНИЮ И ЗАПУСКУ:")
    print("="*80)
    print(f"1. Выполните скрипт для перезапуска: ./kaliningrad-master/{restart_script}")
    print("2. После успешного запуска приложение будет доступно по адресу: http://localhost:8080")
    print("3. Документация API: http://localhost:8080/docs")
    print("4. Тестовый API: http://localhost:8080/api/test-api")
    print("5. Бизнес-модуль: http://localhost:8080/business")
    print("="*80)

if __name__ == "__main__":
    fix_templates_path() 