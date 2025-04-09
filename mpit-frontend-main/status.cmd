@echo off
echo === Статус контейнеров Kaliningrad ===
echo.

docker compose -f docker/docker-compose.yml ps

echo.
echo Для подробной информации о контейнере используйте: docker inspect [имя_контейнера] 