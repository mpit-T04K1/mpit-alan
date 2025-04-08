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
