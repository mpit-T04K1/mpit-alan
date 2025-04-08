#!/bin/bash
echo "Перезапуск сервиса бронирования..."
docker compose down
docker compose up -d
echo ""
echo "Сервис перезапущен и доступен по адресу http://localhost:8080"
echo "Бизнес-модуль доступен по адресу http://localhost:8080/business" 