@echo off
echo Starting JobHunter AI Development Environment...

:: Start Backend
start "JobHunter Backend" cmd /k "cd mcp_server && python -m uvicorn app.main:app --reload --port 8000"

:: Start Frontend
echo Starting Frontend...
set "PATH=%~dp0node-v22.12.0-win-x64;%PATH%"
cd frontend
npm run dev
