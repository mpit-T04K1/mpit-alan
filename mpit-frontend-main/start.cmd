@echo off
echo === Запуск Kaliningrad ====
echo.

rem Остановка предыдущих контейнеров
echo Остановка предыдущих контейнеров...
docker compose down

rem Запуск проекта
echo Запуск проекта...
docker compose up -d

if %ERRORLEVEL% neq 0 (
    echo Ошибка при запуске проекта
    exit /b 1
)

echo Ожидание запуска приложения...
timeout /t 5 /nobreak > nul

rem Проверка доступности приложения
echo Проверка доступности приложения...
powershell -Command "try { $statusCode = (Invoke-WebRequest -Uri 'http://localhost:8006/' -UseBasicParsing).StatusCode; if ($statusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if %ERRORLEVEL% neq 0 (
    echo Ошибка: приложение недоступно
    exit /b 1
)

echo.
echo === Проект успешно запущен ===
echo Приложение доступно по адресу:
echo - Веб-интерфейс: http://localhost:8006 