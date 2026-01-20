# Development Environment Startup Script
# This script starts both the backend API and frontend dev server

Write-Host "🚀 Starting Mindfulness Prototype Development Environment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "`n📦 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node is installed
Write-Host "`n📦 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Found Node: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Install Python dependencies if needed
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✅ Python dependencies ready" -ForegroundColor Green

# Install Node dependencies if needed
Write-Host "`n📦 Installing Node dependencies..." -ForegroundColor Yellow
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install
} else {
    Write-Host "✅ Node modules already installed" -ForegroundColor Green
}
Set-Location ..

Write-Host "`n🎨 Theme System Information:" -ForegroundColor Magenta
Write-Host "   🌙 Dark Mode: AMOLED Black with Purple/Pink accents" -ForegroundColor DarkMagenta
Write-Host "   ☀️  Light Mode: Clean White with Green/Lilac accents" -ForegroundColor DarkYellow
Write-Host "   Toggle available in the sidebar!" -ForegroundColor Gray

Write-Host "`n🚀 Starting services..." -ForegroundColor Cyan

# Start backend in a new window
Write-Host "`n[1/2] Starting Backend API on http://localhost:8000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🔧 Backend API Server' -ForegroundColor Blue; uvicorn backend.main:app --reload --port 8000"

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend in a new window
Write-Host "[2/2] Starting Frontend Dev Server on http://localhost:5173" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🎨 Frontend Dev Server' -ForegroundColor Blue; npm run dev"

Write-Host "`n✨ Development environment is starting!" -ForegroundColor Green
Write-Host "`n📱 Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "   • Frontend and backend are running in separate windows" -ForegroundColor Gray
Write-Host "   • Close those windows to stop the servers" -ForegroundColor Gray
Write-Host "   • Check frontend/THEME_SYSTEM.md for theme documentation" -ForegroundColor Gray

Write-Host "`n✅ All services started successfully!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

# Keep this window open to show the status
Write-Host "`nPress any key to exit this status window (servers will keep running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
