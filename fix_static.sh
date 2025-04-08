#!/bin/bash

echo "Копирование CSS файлов из /app/src/static в /app/static"

# Создаем директорию если ее нет
docker exec kaliningrad-master-app-1 mkdir -p /app/static/css

# Копируем CSS файлы
docker exec kaliningrad-master-app-1 cp -r /app/src/static/css/* /app/static/css/

echo "CSS файлы успешно скопированы!"
echo "Теперь стили должны загружаться правильно." 