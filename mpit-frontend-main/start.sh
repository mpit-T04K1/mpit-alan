#!/bin/bash

echo "=== Запуск Kaliningrad ====" 
echo 

# Остановка предыдущих контейнеров
echo "Остановка предыдущих контейнеров..."
docker compose down

# Запуск проекта
echo "Запуск проекта..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "Ошибка при запуске проекта"
    exit 1
fi

echo "Ожидание запуска приложения..."
sleep 5

# Проверка доступности приложения
echo "Проверка доступности приложения..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8006/)

if [ "$RESPONSE" != "200" ]; then
    echo "Ошибка: приложение недоступно, код ответа: $RESPONSE"
    exit 1
fi

echo ""
echo "=== Проект успешно запущен ==="
echo "Приложение доступно по адресу:"
echo "- Веб-интерфейс: http://localhost:8006"
echo "- RabbitMQ Management: http://localhost:15672" 