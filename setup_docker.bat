@echo off
echo ========================================
echo JobHunter AI - Docker Setup
echo ========================================
echo.

:: Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

:: Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [OK] .env file created
    echo.
    echo IMPORTANT: Edit .env file and add your API keys!
    pause
)

:: Pull images and start services
echo Starting all services...
echo This may take a few minutes on first run...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] All services started!
echo ========================================
echo.
echo Services running:
docker-compose ps
echo.
echo Access points:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Neo4j:     http://localhost:7474
echo   Qdrant:    http://localhost:6333/dashboard
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.
pause
