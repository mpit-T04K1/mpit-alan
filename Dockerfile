FROM python:3.12-alpine

WORKDIR /app

# Установка системных зависимостей
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Запуск приложения
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
# uvicorn src.app:app --host 0.0.0.0 --port 8080 --reload