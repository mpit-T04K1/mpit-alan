@echo off
echo === Просмотр логов Kaliningrad ===

if "%~1"=="" (
    echo Просмотр логов всех контейнеров...
    docker compose -f docker/docker-compose.yml logs
) else (
    echo Просмотр логов контейнера %~1...
    docker compose -f docker/docker-compose.yml logs %~1
)

echo.
echo Для просмотра логов конкретного контейнера используйте: logs.cmd [имя_контейнера]
echo Доступные контейнеры: app, postgres, rabbitmq, redis 