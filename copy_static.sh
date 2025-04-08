#!/bin/bash

# Скрипт для копирования статических файлов из /app/src/static в /app/static
echo "Копирование статических файлов..."

if [ -d "/app/src/static" ]; then
  # Создаем директорию для статических файлов
  mkdir -p /app/static
  
  # Копируем CSS файлы
  if [ -d "/app/src/static/css" ]; then
    mkdir -p /app/static/css
    cp -r /app/src/static/css/* /app/static/css/
    echo "CSS файлы скопированы"
  fi
  
  # Копируем JS файлы
  if [ -d "/app/src/static/js" ]; then
    mkdir -p /app/static/js
    cp -r /app/src/static/js/* /app/static/js/
    echo "JS файлы скопированы"
  fi
  
  # Копируем изображения
  if [ -d "/app/src/static/images" ]; then
    mkdir -p /app/static/images
    cp -r /app/src/static/images/* /app/static/images/
    echo "Изображения скопированы"
  fi
  
  # Копируем другие файлы если есть
  if [ -d "/app/src/static/fonts" ]; then
    mkdir -p /app/static/fonts
    cp -r /app/src/static/fonts/* /app/static/fonts/
    echo "Шрифты скопированы"
  fi
  
  echo "Все статические файлы успешно скопированы!"
else
  echo "Директория /app/src/static не найдена!"
fi 