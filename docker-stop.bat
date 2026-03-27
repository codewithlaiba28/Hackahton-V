@echo off
echo ========================================
echo  Customer Success FTE - Docker Stop
echo ========================================
echo.

echo Stopping Docker containers...
docker compose down

echo.
echo Containers stopped!
echo.
echo To start again: docker-start.bat
echo.
