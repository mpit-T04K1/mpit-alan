# Kaliningrad - Модульный интерфейс

Веб-приложение для управления бизнес-процессами с модульным интерфейсом. Проект представляет собой готовую основу для разработки современных интерфейсов с гибкой архитектурой.

## Структура проекта

```
.
├── app/                # Основной код приложения
│   ├── api/            # API endpoints
│   ├── core/           # Основные компоненты
│   ├── models/         # Модели данных
│   ├── routes/         # Маршруты
│   ├── services/       # Бизнес-логика
│   ├── static/         # Статические файлы
│   ├── templates/      # Шаблоны
│   └── utils/          # Утилиты
├── docker/             # Docker конфигурация
└── scripts/            # Скрипты для разработки и деплоя
```

## Требования

- Python 3.8+
- PostgreSQL
- Docker
- Docker Compose

## Быстрый старт

### Windows

Для запуска проекта в Windows используйте следующие команды:

```cmd
# Запуск проекта
start.cmd

# Остановка проекта
stop.cmd

# Перезапуск проекта
restart.cmd

# Просмотр логов
logs.cmd [имя_контейнера]  # Опционально укажите имя контейнера

# Просмотр статуса контейнеров
status.cmd
```

### Linux/macOS

Для запуска проекта в Linux/macOS используйте следующие команды:

```bash
# Запуск проекта
./start.sh

# Остановка проекта
./stop.sh
```

## Доступы после запуска

После запуска приложение будет доступно по адресам:
- Веб-интерфейс: [http://localhost:8080](http://localhost:8080)
- RabbitMQ Management: [http://localhost:15672](http://localhost:15672) (логин: guest, пароль: guest)

## Порты

- 8080: Веб-приложение
- 5432: PostgreSQL
- 5672, 15672: RabbitMQ
- 6379: Redis

## Развертывание вручную

1. Клонировать репозиторий:
```bash
git clone https://github.com/mpit-T04K1/mpit-frontend.git
cd mpit-frontend
```

2. Создать и настроить файл .env:
```bash
# Пример содержимого .env файла
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/qwertytown
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/0
```

3. Запустить проект через Docker:
```bash
docker compose -f docker/docker-compose.yml up -d
```

## Технологии

- **Backend**: FastAPI, PostgreSQL, RabbitMQ, Redis
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Инфраструктура**: Docker, Docker Compose

## Пример использования

Проект содержит демонстрационный модуль для кафе "Неоновый закат", показывающий возможности модульного интерфейса с динамическими панелями и интерактивными элементами.

## Инструкция по обновлению репозитория

Если вы хотите полностью заменить содержимое этого репозитория текущим проектом:

1. Клонируйте текущий репозиторий:
```bash
git clone https://github.com/mpit-T04K1/mpit-frontend.git
cd mpit-frontend
```

2. Удалите все файлы (кроме .git):
```bash
# В Linux/macOS
find . -path ./.git -prune -o -delete

# В Windows (PowerShell)
Get-ChildItem -Path . -Exclude .git -Recurse | Remove-Item -Recurse -Force
```

3. Скопируйте все файлы из проекта Kaliningrad в директорию репозитория

4. Добавьте все файлы в индекс Git:
```bash
git add .
```

5. Создайте коммит:
```bash
git commit -m "Полная замена содержимого на проект Kaliningrad"
```

6. Отправьте изменения в репозиторий:
```bash
git push origin main
```

## Лицензия

MIT 