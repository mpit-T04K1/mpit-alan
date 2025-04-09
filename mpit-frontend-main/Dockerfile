FROM python:3.10-slim

WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir requests

# Копирование кода приложения
COPY . .

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Порт, на котором будет запущено приложение
EXPOSE 8080

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 