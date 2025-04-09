# Документация проекта Kaliningrad

## Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура](#архитектура)
3. [Технологический стек](#технологический-стек)
4. [Структура проекта](#структура-проекта)
5. [Установка и настройка](#установка-и-настройка)
   - [Требования](#требования)
   - [Установка](#установка)
   - [Настройка переменных окружения](#настройка-переменных-окружения)
6. [Запуск проекта](#запуск-проекта)
   - [В Windows](#в-windows)
   - [В Linux/macOS](#в-linuxmacos)
7. [Docker-конфигурация](#docker-конфигурация)
8. [База данных](#база-данных)
   - [Модели](#модели)
   - [Миграции](#миграции)
9. [API](#api)
10. [Интерфейс](#интерфейс)
    - [Модульная архитектура](#модульная-архитектура)
    - [Компоненты интерфейса](#компоненты-интерфейса)
11. [Модули системы](#модули-системы)
    - [Ситуационный центр](#ситуационный-центр)
    - [Демонстрационный модуль "Кафе"](#демонстрационный-модуль-кафе)
12. [Статические файлы](#статические-файлы)
13. [Скрипты для управления проектом](#скрипты-для-управления-проектом)
14. [Логирование](#логирование)
15. [Безопасность](#безопасность)
16. [Разработка и расширение](#разработка-и-расширение)
    - [Добавление новых модулей](#добавление-новых-модулей)
    - [Добавление API-эндпоинтов](#добавление-api-эндпоинтов)
17. [Устранение неполадок](#устранение-неполадок)
18. [FAQ](#faq)
19. [Лицензия](#лицензия)

## Обзор проекта

Kaliningrad - это веб-приложение для управления бизнес-процессами с модульным интерфейсом. Проект предоставляет готовую основу для разработки современных интерфейсов с гибкой архитектурой, которая позволяет легко интегрировать и управлять различными бизнес-процессами через единый интерфейс.

**Ключевые особенности:**
- Модульная архитектура с возможностью расширения
- Современный адаптивный интерфейс
- Реактивная архитектура для динамического обновления данных
- Контейнеризация и легкий деплой с использованием Docker
- Поддержка PostgreSQL для хранения данных
- Интеграция с RabbitMQ для обработки сообщений
- Кэширование с помощью Redis

**Основные сценарии использования:**
- Создание модульных бизнес-приложений
- Разработка ситуационных центров и панелей мониторинга
- Реализация интерфейсов с динамической структурой и возможностью настройки

## Архитектура

Приложение построено на основе современных принципов веб-разработки с использованием микросервисной архитектуры.

### Общая схема архитектуры:

```
+--------------------+      +--------------------+
|                    |      |                    |
|    Web Browser     |<---->|    FastAPI Web     |
|                    |      |   Application      |
+--------------------+      +----------+---------+
                                       |
                                       v
 +----------------+       +------------+-----------+
 |                |       |                        |
 |   RabbitMQ     |<----->|     PostgreSQL        |
 | (Message Bus)  |       |    (Database)         |
 +----------------+       +------------+-----------+
                                       |
                                       v
                           +------------+-----------+
                           |                        |
                           |         Redis          |
                           |    (Cache Server)      |
                           +------------------------+
```

### Компоненты архитектуры:

1. **Веб-интерфейс**: Отвечает за представление данных пользователю. Построен с использованием HTML, CSS, JavaScript и шаблонизатора Jinja2. Обеспечивает реактивное взаимодействие без полной перезагрузки страницы.

2. **Серверное приложение FastAPI**: Обрабатывает HTTP-запросы, обеспечивает маршрутизацию, бизнес-логику и взаимодействие с базой данных.

3. **База данных PostgreSQL**: Хранит все данные приложения, включая информацию о пользователях, бизнес-процессах и настройках.

4. **RabbitMQ**: Обеспечивает асинхронную обработку сообщений и фоновые задачи.

5. **Redis**: Используется для кэширования и хранения временных данных, а также для оптимизации производительности.

## Технологический стек

### Backend:
- **Python 3.8+**: Основной язык программирования
- **FastAPI**: Web-фреймворк для создания API
- **SQLAlchemy**: ORM для работы с базой данных
- **Alembic**: Инструмент миграции базы данных
- **Uvicorn**: ASGI-сервер для запуска FastAPI
- **Pydantic**: Валидация и сериализация данных

### Frontend:
- **HTML5/CSS3**: Структура и стили страниц
- **JavaScript (ES6+)**: Клиентская логика
- **Bootstrap 5**: CSS-фреймворк для стилизации
- **Jinja2**: Шаблонизатор для Python

### База данных:
- **PostgreSQL**: Основная реляционная БД
- **Redis**: Кэширование и очереди задач

### Инфраструктура:
- **Docker**: Контейнеризация приложения
- **Docker Compose**: Оркестрация контейнеров
- **RabbitMQ**: Система очередей сообщений

### Инструменты разработки:
- **Git**: Система контроля версий
- **Pytest**: Фреймворк для тестирования

## Структура проекта

```
kaliningrad/
├── app/                    # Основной код приложения
│   ├── api/                # API endpoints
│   │   └── ...
│   ├── core/               # Основные компоненты
│   │   └── ...
│   ├── models/             # Модели данных
│   │   └── ...
│   ├── routes/             # Маршруты
│   │   └── situation_center.py  # Маршруты ситуационного центра
│   ├── services/           # Бизнес-логика
│   │   └── ...
│   ├── static/             # Статические файлы
│   │   ├── css/            # Стили CSS
│   │   ├── js/             # JavaScript файлы
│   │   ├── images/         # Изображения
│   │   └── fonts/          # Шрифты
│   ├── templates/          # Шаблоны Jinja2
│   │   ├── modular_base.html  # Базовый шаблон модульного интерфейса
│   │   └── cafe_example.html  # Пример модуля кафе
│   └── utils/              # Утилиты
│       └── ...
├── docker/                 # Docker конфигурация
│   ├── Dockerfile          # Dockerfile для приложения
│   ├── docker-compose.yml  # Конфигурация Docker Compose
│   ├── docker-entrypoint.sh # Скрипт для запуска контейнера
│   └── init.sql            # Инициализация БД
├── migrations/             # Миграции базы данных
│   ├── versions/           # Версии миграций
│   ├── env.py              # Окружение для миграций
│   └── script.py.mako      # Шаблон для миграций
├── scripts/                # Скрипты для разработки и деплоя
├── main.py                 # Точка входа в приложение
├── alembic.ini             # Конфигурация Alembic
├── requirements.txt        # Зависимости Python
├── .env                    # Переменные окружения
├── .gitignore              # Исключения для Git
├── README.md               # Readme проекта
├── start.cmd               # Скрипт запуска для Windows
├── stop.cmd                # Скрипт остановки для Windows
├── restart.cmd             # Скрипт перезапуска для Windows
├── logs.cmd                # Просмотр логов для Windows
├── status.cmd              # Проверка статуса для Windows
├── start.sh                # Скрипт запуска для Linux/macOS
└── stop.sh                 # Скрипт остановки для Linux/macOS
```

## Установка и настройка

### Требования

Для запуска проекта необходимо установить:

- Python 3.8 или выше
- PostgreSQL 12 или выше
- Docker 20.10 или выше
- Docker Compose 2.0 или выше

### Установка

1. **Клонировать репозиторий:**

```bash
git clone https://github.com/mpit-T04K1/mpit-frontend.git
cd mpit-frontend
```

2. **Создать виртуальное окружение (опционально при запуске без Docker):**

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Установить зависимости (опционально при запуске без Docker):**

```bash
pip install -r requirements.txt
```

### Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```
# Основные настройки
DEBUG=True
SECRET_KEY=your_secure_secret_key_here
PORT=8080
HOST=0.0.0.0

# Настройки базы данных
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/qwertytown

# Настройки Redis
REDIS_URL=redis://redis:6379/0

# Настройки RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Дополнительные настройки
YANDEX_MAPS_API_KEY=your_yandex_maps_api_key
```

Обратите внимание, что при разработке и отладке используйте `DEBUG=True`, но в продакшене это значение должно быть `False`.

## Запуск проекта

### В Windows

Для удобства запуска и управления проектом предусмотрены командные файлы:

```cmd
# Запуск всех контейнеров проекта
start.cmd

# Остановка проекта
stop.cmd

# Перезапуск проекта
restart.cmd

# Просмотр логов (все контейнеры или указанный)
logs.cmd [имя_контейнера]

# Проверка статуса контейнеров
status.cmd
```

### В Linux/macOS

В Linux и macOS используйте следующие shell-скрипты:

```bash
# Запуск проекта
./start.sh

# Остановка проекта
./stop.sh
```

После запуска приложение будет доступно по адресам:

- Веб-интерфейс: [http://localhost:8080](http://localhost:8080)
- RabbitMQ Management: [http://localhost:15672](http://localhost:15672) (логин: guest, пароль: guest)

## Docker-конфигурация

Проект использует Docker для упрощения развертывания и унификации среды выполнения. Конфигурация включает несколько сервисов:

### Сервисы в docker-compose.yml:

#### app

```yaml
app:
  build:
    context: ..
    dockerfile: docker/Dockerfile
  image: kaliningrad-app:latest
  container_name: kaliningrad-app
  ports:
    - "8080:8080"
  volumes:
    - ..:/app
    - ../app/static/uploads:/app/app/static/uploads
  env_file:
    - ../.env
  depends_on:
    - postgres
    - rabbitmq
    - redis
  command: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
  restart: unless-stopped
```

#### postgres

```yaml
postgres:
  image: postgres:14
  container_name: kaliningrad-postgres
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql
  environment:
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
    - POSTGRES_DB=qwertytown
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 10s
    timeout: 5s
    retries: 3
  restart: unless-stopped
```

#### rabbitmq

```yaml
rabbitmq:
  image: rabbitmq:3.9-management
  container_name: kaliningrad-rabbitmq
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
  environment:
    - RABBITMQ_DEFAULT_USER=guest
    - RABBITMQ_DEFAULT_PASS=guest
  ports:
    - "5672:5672"
    - "15672:15672"
  healthcheck:
    test: ["CMD", "rabbitmqctl", "status"]
    interval: 10s
    timeout: 5s
    retries: 3
  restart: unless-stopped
```

#### redis

```yaml
redis:
  image: redis:6
  container_name: kaliningrad-redis
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 3
  restart: unless-stopped
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директорий для загрузок
RUN mkdir -p app/static/uploads/logos app/static/uploads/generated_logos app/static/uploads/photo

# Права на запуск скрипта
RUN chmod +x docker/docker-entrypoint.sh

# Запуск приложения через entrypoint
ENTRYPOINT ["docker/docker-entrypoint.sh"]
```

## База данных

Проект использует PostgreSQL в качестве основной базы данных. Структура базы данных управляется с помощью SQLAlchemy ORM и миграций Alembic.

### Модели

Модели данных находятся в директории `app/models/` и включают:

- Пользователи и аутентификация
- Бизнес-сущности
- Связи между объектами
- Настройки и конфигурации

### Миграции

Миграции базы данных хранятся в директории `migrations/versions/` и управляются с помощью Alembic. Для управления миграциями используйте следующие команды:

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции на один шаг назад
alembic downgrade -1
```

Файл `alembic.ini` содержит настройки Alembic, включая подключение к базе данных.

## API

API построено на основе FastAPI и предоставляет следующие возможности:

- RESTful эндпоинты для работы с данными
- Автоматическая генерация документации Swagger
- Валидация входных данных с помощью Pydantic
- Аутентификация и авторизация

### Основные API эндпоинты:

#### Ситуационный центр

```python
@router.get("/situation-center/modular-demo", response_class=HTMLResponse)
async def modular_interface_demo(request: Request):
    """
    Демонстрация модульного интерфейса с тремя панелями.
    """
    return templates.TemplateResponse(
        "cafe_example.html", 
        {
            "request": request,
            "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
        }
    )
```

#### API для получения данных

```python
@router.get("/situation-center/api/items", response_class=JSONResponse)
async def get_items():
    """
    API для получения списка элементов для левой панели.
    """
    # Логика получения элементов
    items = [...]
    return {"items": items}
```

#### API для работы с деталями

```python
@router.get("/situation-center/api/items/{item_id}", response_class=JSONResponse)
async def get_item_details(item_id: str):
    """
    API для получения детальной информации об элементе.
    """
    # Логика получения деталей элемента
    item_details = {...}
    return item_details
```

## Интерфейс

### Модульная архитектура

Ключевая особенность проекта - модульный интерфейс, который позволяет:

1. Гибко настраивать расположение и содержимое панелей
2. Динамически загружать данные без перезагрузки страницы
3. Адаптировать интерфейс под различные устройства
4. Легко расширять и добавлять новые компоненты

### Компоненты интерфейса

Основу интерфейса составляют следующие компоненты:

#### Модульный контейнер

```html
<div class="modular-container">
    <!-- Основная панель (левая) -->
    <div class="main-panel">...</div>
    
    <!-- Боковая навигационная панель (правая) -->
    <div class="sidebar-panel">...</div>
    
    <!-- Нижняя информационная панель -->
    <div class="info-panel">...</div>
</div>
```

#### Панели

Каждая панель имеет свою структуру и может содержать различные типы контента:

- **Основная панель**: Отображает основной контент, например, карту, таблицу данных или форму
- **Боковая панель**: Обычно содержит навигацию, фильтры или дополнительные элементы управления
- **Нижняя панель**: Предназначена для отображения детальной информации, статистики или управляющих элементов

#### Секции контента

Внутри каждой панели могут располагаться секции, которые показываются/скрываются в зависимости от выбранной навигации:

```html
<div id="welcome-section" class="section active">
    <!-- Содержимое секции -->
</div>

<div id="menu-section" class="section" style="display: none;">
    <!-- Содержимое секции -->
</div>
```

#### JavaScript для управления интерфейсом

```javascript
class ModularInterface {
    constructor() {
        this.activeSection = null;
        this.activeInfoSection = null;
        
        // Инициализация обработчиков событий
        this.initNavigation();
        this.initSubmenuToggle();
        this.showDefaultSections();
    }
    
    // Методы для работы с навигацией и секциями
    switchToSection(sectionId) {
        // Скрываем все секции
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Показываем выбранную секцию
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            this.activeSection = `${sectionId}-section`;
        }
    }
}
```

## Модули системы

### Ситуационный центр

Модуль "Ситуационный центр" является ключевой частью системы и представляет собой интерфейс для мониторинга и управления информацией в реальном времени.

Маршрут определен в `app/routes/situation_center.py`:

```python
# Создаем роутер для ситуационного центра
router = APIRouter(
    prefix="/situation-center",
    tags=["situation_center"],
    responses={404: {"description": "Not found"}},
)

@router.get("/modular-demo", response_class=HTMLResponse)
async def modular_interface_demo(request: Request):
    """
    Демонстрация модульного интерфейса с тремя панелями.
    """
    return templates.TemplateResponse(
        "cafe_example.html", 
        {
            "request": request,
            "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
        }
    )
```

### Демонстрационный модуль "Кафе"

Модуль "Кафе" служит демонстрационным примером использования модульного интерфейса. Он представляет интерфейс кафе "Неоновый закат" с разделами:

- Главная страница с информацией о кафе
- Меню с категориями и блюдами
- Карта расположения
- Контакты и форма бронирования
- Галерея

Шаблон находится в `app/templates/cafe_example.html` и наследуется от основного модульного шаблона `modular_base.html`.

## Статические файлы

Статические файлы проекта хранятся в директории `app/static/` и структурированы следующим образом:

- **css/**: Стили для интерфейса
  - `main.css`: Основные стили
  - `situation_center.css`: Стили для ситуационного центра
  - `business-module.css`: Стили для бизнес-модуля
  - `business-profile.css`: Стили для профиля бизнеса
  
- **js/**: JavaScript файлы
  - `main.js`: Основные функции
  - `situation_center.js`: Функции для ситуационного центра
  
- **images/**: Изображения проекта
  - `menu/`: Изображения для меню кафе
  - `qwertytown-logo.png`: Логотип проекта
  
- **fonts/**: Шрифты
  - `Futura Pt Font Family/`: Семейство шрифтов Futura PT
  
- **uploads/**: Директория для пользовательских загрузок
  - `logos/`: Логотипы
  - `generated_logos/`: Сгенерированные логотипы
  - `photo/`: Фотографии

## Скрипты для управления проектом

Проект содержит набор скриптов для упрощения управления:

### Для Windows (CMD):

- **start.cmd**: Запуск проекта
  ```cmd
  @echo off
  echo === Запуск Kaliningrad ====
  echo.
  
  rem Остановка предыдущих контейнеров
  docker compose -f docker/docker-compose.yml down
  
  rem Запуск проекта
  docker compose -f docker/docker-compose.yml up -d
  
  echo Ожидание запуска приложения...
  timeout /t 5 /nobreak > nul
  
  rem Проверка доступности приложения
  echo Приложение доступно по адресу:
  echo - Веб-интерфейс: http://localhost:8080
  echo - RabbitMQ Management: http://localhost:15672
  ```

- **stop.cmd**: Остановка проекта
- **restart.cmd**: Перезапуск проекта
- **logs.cmd**: Просмотр логов контейнеров
- **status.cmd**: Проверка статуса контейнеров

### Для Linux/macOS (Bash):

- **start.sh**: Запуск проекта
  ```bash
  #!/bin/bash
  
  echo "=== Запуск Kaliningrad ====" 
  echo 
  
  # Остановка предыдущих контейнеров
  docker compose -f docker/docker-compose.yml down
  
  # Запуск проекта
  docker compose -f docker/docker-compose.yml up -d
  
  echo "Ожидание запуска приложения..."
  sleep 5
  
  echo "Проект успешно запущен"
  echo "Приложение доступно по адресу:"
  echo "- Веб-интерфейс: http://localhost:8080"
  echo "- RabbitMQ Management: http://localhost:15672"
  ```

- **stop.sh**: Остановка проекта

## Логирование

В проекте настроена система логирования с использованием стандартного модуля `logging` Python:

```python
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

Логи доступны:
- В консоли при локальном запуске
- В логах Docker-контейнеров при запуске через Docker

## Безопасность

### Переменные окружения

Чувствительные данные, такие как ключи API и пароли, хранятся в переменных окружения и файле `.env`, который не должен включаться в репозиторий.

### CORS

Настроена защита CORS для API:

```python
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

В продакшен-окружении рекомендуется ограничить `allow_origins` только доверенными доменами.

## Разработка и расширение

### Добавление новых модулей

Для добавления нового модуля необходимо:

1. **Создать шаблон модуля** в директории `app/templates/`
2. **Добавить маршрут** в соответствующий файл роутера
3. **Создать необходимые API эндпоинты** для работы с данными модуля
4. **Добавить статические файлы** (CSS, JS, изображения)
5. **Обновить навигацию** для доступа к новому модулю

Пример нового шаблона:

```html
{% extends "modular_base.html" %}

{% block title %}Название нового модуля{% endblock %}

{% block main_panel %}
<!-- Содержимое основной панели -->
{% endblock %}

{% block sidebar_panel %}
<!-- Содержимое боковой панели -->
{% endblock %}

{% block info_panel %}
<!-- Содержимое нижней панели -->
{% endblock %}

{% block scripts %}
<script>
// JavaScript для модуля
</script>
{% endblock %}
```

### Добавление API-эндпоинтов

Пример добавления нового API-эндпоинта:

```python
@router.get("/api/new-endpoint", response_class=JSONResponse)
async def new_endpoint(param: str = Query(None)):
    """
    Новый API эндпоинт.
    """
    # Логика обработки запроса
    result = {"status": "success", "data": {...}}
    return result
```

## Устранение неполадок

### Типичные проблемы и их решения:

#### 1. Docker-контейнеры не запускаются

**Проверьте:**
- Запущен ли Docker демон
- Нет ли конфликтов портов
- Логи контейнеров:
  ```
  docker logs kaliningrad-app
  ```

#### 2. Проблемы с базой данных

**Решение:**
- Проверить подключение к базе данных
- Выполнить миграции вручную:
  ```
  alembic upgrade head
  ```
- Проверить настройки в `.env`

#### 3. Ошибки при запуске приложения

**Решение:**
- Проверить логи приложения
- Убедиться, что все зависимости установлены
- Проверить совместимость версий

## FAQ

### 1. Как добавить нового пользователя в систему?

На данный момент система не включает полноценный модуль аутентификации и управления пользователями. Для добавления этой функциональности рекомендуется:

1. Создать модель пользователя в `app/models/`
2. Добавить API для регистрации и аутентификации
3. Настроить механизм сессий или JWT-токенов

### 2. Как изменить порт для веб-интерфейса?

Порт настраивается:
- В `.env` файле через переменную `PORT`
- В `docker-compose.yml` в секции `ports` для сервиса `app`
- В команде запуска в `Dockerfile`

### 3. Как добавить новый сервис в Docker?

Для добавления нового сервиса отредактируйте `docker/docker-compose.yml`, добавив новую секцию:

```yaml
new_service:
  image: image_name:tag
  container_name: kaliningrad-new-service
  volumes:
    - volume_name:/path/in/container
  environment:
    - ENV_VAR=value
  ports:
    - "host_port:container_port"
  restart: unless-stopped
```

## Лицензия

Проект распространяется под лицензией MIT. Полный текст лицензии доступен в файле LICENSE проекта. 