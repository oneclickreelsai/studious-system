# OneClick Reels AI - Startup Script

Write-Host ""
Write-Host "OneClick Reels AI" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor DarkGray
Write-Host ""

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Python
Write-Host "[*] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "    [X] Python not found!" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "[*] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    [OK] Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "    [X] Node.js not found!" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies if needed
if (-not (Test-Path "$ProjectRoot\frontend\node_modules")) {
    Write-Host ""
    Write-Host "[*] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\frontend"
    npm install
    Set-Location $ProjectRoot
}

Write-Host ""
Write-Host "[*] Starting servers..." -ForegroundColor Green
Write-Host "    Backend:  http://localhost:8002" -ForegroundColor Cyan
Write-Host "    Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "    API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

Set-Location "$ProjectRoot\frontend"
npm start
