@echo off
echo ========================================
echo  Customer Success FTE - Docker Deploy
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Copy .env.example to .env and add your API keys
    echo.
    copy .env.example .env
    notepad .env
    pause
)

echo Starting Docker containers...
docker compose up -d --build

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Database: localhost:5432
echo.
echo To view logs: docker compose logs -f
echo To stop:      docker compose down
echo.

docker compose ps
