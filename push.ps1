# OneClick Reels AI - Push to GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OneClick Reels AI - GitHub Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Initialize if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/oneclickreelsai/studious-system.git
}

# Stage all tracked files (respects .gitignore)
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

# Show status
Write-Host ""
Write-Host "Files to commit:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host ""
$commitMsg = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git commit -m "$commitMsg"

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Done! Pushed to GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repo: https://github.com/oneclickreelsai/studious-system" -ForegroundColor Cyan
Write-Host "Actions: https://github.com/oneclickreelsai/studious-system/actions" -ForegroundColor Cyan
