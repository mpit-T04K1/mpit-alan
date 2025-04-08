#!/bin/bash

echo "Останавливаем текущие контейнеры..."
docker compose down

echo "Копируем новый Dockerfile..."
cp Dockerfile.new Dockerfile

echo "Пересобираем и запускаем контейнеры..."
docker compose up -d --build

echo "Применяем миграции..."
docker compose exec app alembic current

echo "Проверяем, что копирование статических файлов сработало..."
docker compose exec app ls -la /app/static/css/

echo "Готово! Теперь стили должны корректно отображаться."
echo "Приложение доступно по адресу: http://localhost:8080"
echo "Админка доступна по адресу: http://localhost:8080/admin/" 