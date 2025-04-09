@echo off
echo === Перезапуск Kaliningrad ===

rem Перезапуск контейнеров
docker compose -f docker/docker-compose.yml restart

echo Ожидание перезапуска приложения...
timeout /t 5 /nobreak > nul

rem Проверка доступности приложения
echo Проверка доступности приложения...
powershell -Command "try { $statusCode = (Invoke-WebRequest -Uri 'http://localhost:8080/' -UseBasicParsing).StatusCode; if ($statusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if %ERRORLEVEL% neq 0 (
    echo Предупреждение: приложение может быть недоступно
) else (
    echo Приложение успешно перезапущено
)

echo.
echo === Проект перезапущен ===
echo Приложение доступно по адресу:
echo - Веб-интерфейс: http://localhost:8080
echo - RabbitMQ Management: http://localhost:15672 