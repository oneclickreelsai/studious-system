# Fix git lock and push to GitHub
Write-Host "Fixing git lock and pushing to GitHub..." -ForegroundColor Cyan

# Kill any git processes
Write-Host "Stopping git processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*git*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Remove lock file
Write-Host "Removing lock file..." -ForegroundColor Yellow
if (Test-Path ".git/index.lock") {
    Remove-Item ".git/index.lock" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Check git status
Write-Host "Checking git status..." -ForegroundColor Yellow
git status

# Add files
Write-Host "`nAdding files..." -ForegroundColor Yellow
git add .gitignore
git add .github/
git add backend/database/json_db.py
git add backend/api/main.py
git add backend/core/video_engine/voiceover.py
git add deployment/
git add Dockerfile
git add docker-compose.yml
git add requirements.txt
git add README.md
git add render.yaml
git add railway.toml
git add vercel.json

# Commit
Write-Host "`nCommitting..." -ForegroundColor Yellow
git commit -m "feat: add CI/CD pipeline, JSON database, and deployment configuration"

# Check if we have commits
$hasCommits = git rev-parse HEAD 2>$null
if (-not $hasCommits) {
    Write-Host "No commits yet, creating initial commit..." -ForegroundColor Yellow
    git add .
    git commit -m "Initial commit with CI/CD pipeline"
}

# Set branch to main
Write-Host "`nSetting branch to main..." -ForegroundColor Yellow
git branch -M main

# Push
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=================================="
    Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "=================================="
    Write-Host "`nView your CI/CD pipeline at:"
    Write-Host "https://github.com/oneclickreelsai/studious-system/actions" -ForegroundColor Cyan
    Write-Host "`nNext: Add secrets in GitHub Settings -> Secrets and variables -> Actions"
    
    # Open browser
    Start-Process "https://github.com/oneclickreelsai/studious-system"
} else {
    Write-Host "`nPush failed. Try manually:" -ForegroundColor Red
    Write-Host "git push -u origin main --force"
}
