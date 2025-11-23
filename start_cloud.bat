@echo off
echo ========================================
echo JobHunter AI - Quick Start (Cloud)
echo ========================================
echo.

:: Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please follow these steps:
    echo 1. Read CLOUD_SETUP.md
    echo 2. Sign up for cloud databases
    echo 3. Update .env with your credentials
    echo.
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
cd mcp_server
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [2/3] Testing cloud connections...
python test_cloud_connections.py
if errorlevel 1 (
    echo.
    echo [WARNING] Some connections failed
    echo Check CLOUD_SETUP.md for troubleshooting
    pause
)

echo.
echo [3/3] Starting services...
echo.

:: Start backend in new window
start "JobHunter Backend" cmd /k "cd mcp_server && python -m uvicorn app.main:app --reload --port 8000"

:: Wait a bit for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
echo Starting frontend...
cd frontend
npm install
npm run dev

pause
