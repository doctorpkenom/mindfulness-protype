# Development startup script for Mindfulness Prototype
# Starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Development Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend\main.py")) {
    Write-Host "Error: backend\main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend\package.json")) {
    Write-Host "Error: frontend\package.json not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Start Backend in a new window
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Green
$backendScript = @"
cd `"$PWD`"
Write-Host 'Backend Server Starting...' -ForegroundColor Green
uvicorn backend.main:app --reload --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend (Port 5173)..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the frontend server" -ForegroundColor Gray
Write-Host ""

Set-Location frontend
npm run dev
