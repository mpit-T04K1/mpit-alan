FROM python:3.9-slim

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование структуры директорий
RUN mkdir -p /app/src/db /app/src/database /app/src/adapters/database /app/alembic/versions

# Копирование необходимых файлов для миграций
COPY alembic.ini migrations.py /app/
COPY alembic/env.py alembic/script.py.mako /app/alembic/
COPY alembic/versions/ /app/alembic/versions/

# Копирование остального кода приложения
COPY . .

# Переменные среды
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "main.py"] 