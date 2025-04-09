#!/bin/bash
echo "Запуск сервиса бронирования..."
docker compose up -d
echo ""
echo "Применение миграций базы данных..."
docker compose exec app alembic upgrade head
echo ""
echo "Сервис запущен и доступен по адресу http://localhost:8080"
echo "Бизнес-модуль доступен по адресу http://localhost:8080/business" 