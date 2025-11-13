# TrendKe Project Startup Script (PowerShell)
# Starts both backend and frontend servers

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TrendKe Project Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Redis is running
Write-Host "[1/3] Checking Redis..." -ForegroundColor Yellow
$redisRunning = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue

if ($redisRunning) {
    Write-Host "[OK] Redis is running on port 6379`n" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Redis is NOT running on port 6379" -ForegroundColor Red
    Write-Host "`nPlease start Redis first:" -ForegroundColor Yellow
    Write-Host "  - If using Docker: docker start redis-trendke" -ForegroundColor Gray
    Write-Host "  - If using WSL: wsl redis-server" -ForegroundColor Gray
    Write-Host "  - If installed natively: redis-server`n" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Start Backend
Write-Host "[2/3] Starting Python Backend (Port 8001)..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Write-Host "Opening new terminal for backend...`n" -ForegroundColor Gray
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[3/3] Starting React Frontend (Port 5174)..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Write-Host "Opening new terminal for frontend...`n" -ForegroundColor Gray
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   All Services Started!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5174" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor Cyan

Write-Host "`nTwo new terminal windows have opened." -ForegroundColor Yellow
Write-Host "Close those windows to stop the servers.`n" -ForegroundColor Yellow

Read-Host "Press Enter to close this window"
