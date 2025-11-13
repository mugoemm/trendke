@echo off
REM TrendKe Project Startup Script
REM This script starts both backend and frontend servers

echo ========================================
echo    TrendKe Project Startup
echo ========================================
echo.

REM Check if Redis is running
echo [1/3] Checking Redis...
netstat -an | findstr ":6379" >nul
if %errorlevel% equ 0 (
    echo [OK] Redis is running on port 6379
) else (
    echo [WARNING] Redis is NOT running on port 6379
    echo.
    echo Please start Redis first:
    echo   - If using Docker: docker start redis-trendke
    echo   - If using WSL: wsl redis-server
    echo   - If installed natively: redis-server
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting Python Backend (Port 8001)...
echo Opening new terminal for backend...
start "TrendKe Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Starting React Frontend (Port 5174)...
echo Opening new terminal for frontend...
start "TrendKe Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo    All Services Started!
echo ========================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:5174
echo API Docs: http://localhost:8001/docs
echo.
echo Two new terminal windows have opened.
echo Close those windows to stop the servers.
echo.
pause
