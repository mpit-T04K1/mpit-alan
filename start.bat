@echo off
echo Starting booking service...
docker compose up -d
echo.

echo Waiting for database to start...
timeout /t 20

echo Applying database migrations...
docker compose exec app python migrations.py
if %ERRORLEVEL% neq 0 (
    echo WARNING: Migrations failed. The service may not work correctly.
    echo Please check the logs for more information.
) else (
    echo Migrations applied successfully.
)

echo.
echo Service is running and available at http://localhost:8080
echo Business module is available at http://localhost:8080/business
echo.
echo Press any key to continue...
