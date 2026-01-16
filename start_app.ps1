# Start Backend in background
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Green
Start-Process -FilePath "uvicorn" -ArgumentList "backend.main:app", "--reload" -NoNewWindow
# Note: You might need to activate venv first if not active. 
# This script assumes 'uvicorn' is in path (e.g. inside the active env)

# Start Frontend
Write-Host "Starting Frontend (Port 5173)..." -ForegroundColor Green
Set-Location frontend
npm run dev
