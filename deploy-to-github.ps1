# OneClick Reels AI - Deploy to GitHub Script
# This script pushes your code to GitHub and triggers CI/CD

Write-Host "=================================="
Write-Host "OneClick Reels AI - GitHub Deploy"
Write-Host "=================================="
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "Git initialized!" -ForegroundColor Green
} else {
    Write-Host "Git repository already initialized" -ForegroundColor Green
}

# Check if remote exists
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host ""
    Write-Host "Setting up GitHub remote..." -ForegroundColor Yellow
    $repoUrl = "https://github.com/oneclickreelsai/studious-system.git"
    git remote add origin $repoUrl
    Write-Host "Remote added: $repoUrl" -ForegroundColor Green
} else {
    Write-Host "Remote already configured: $remoteUrl" -ForegroundColor Green
}

# Create .gitignore if it doesn't exist
if (-not (Test-Path ".gitignore")) {
    Write-Host ""
    Write-Host "Creating .gitignore..." -ForegroundColor Yellow
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
.cache/

# Environment
.env
config.env
*.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
output/
logs/
cache/
temp/
*.log
*.db
*.sqlite
data/database.json

# Credentials
*_token.json
credentials.json
service_account.json
oneclickreelsai-*.json

# Archives
*.zip
*.tar.gz
2026-*/

# Test files
test_*.py
*_test.py
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host ".gitignore created!" -ForegroundColor Green
}

# Stage all files
Write-Host ""
Write-Host "Staging files..." -ForegroundColor Yellow
git add .

# Show status
Write-Host ""
Write-Host "Git Status:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host ""
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "feat: add CI/CD pipeline and deployment configuration"
}

Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "$commitMessage"

# Check if commit was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Commit successful!" -ForegroundColor Green
} else {
    Write-Host "Nothing to commit or commit failed" -ForegroundColor Yellow
}

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "This will trigger the CI/CD pipeline!" -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Push to GitHub now? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    # Try to push
    git push -u origin main 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=================================="
        Write-Host "SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
        Write-Host "=================================="
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Go to: https://github.com/oneclickreelsai/studious-system/actions"
        Write-Host "2. Watch your CI/CD pipeline run"
        Write-Host "3. Add secrets in: Settings -> Secrets and variables -> Actions"
        Write-Host ""
        Write-Host "Required secrets:" -ForegroundColor Yellow
        Write-Host "  - RAILWAY_TOKEN"
        Write-Host "  - RENDER_DEPLOY_HOOK"
        Write-Host "  - OPENAI_API_KEY"
        Write-Host "  - PERPLEXITY_API_KEY"
        Write-Host "  - YOUTUBE_CLIENT_ID"
        Write-Host "  - YOUTUBE_CLIENT_SECRET"
        Write-Host "  - YOUTUBE_REFRESH_TOKEN"
        Write-Host "  - FB_PAGE_ID"
        Write-Host "  - FB_ACCESS_TOKEN"
        Write-Host "  - PEXELS_API_KEY"
        Write-Host "  - PIXABAY_API_KEY"
        Write-Host ""
        Write-Host "Opening GitHub Actions page..." -ForegroundColor Cyan
        Start-Process "https://github.com/oneclickreelsai/studious-system/actions"
    } else {
        Write-Host ""
        Write-Host "Push failed. This might be because:" -ForegroundColor Red
        Write-Host "1. You need to authenticate with GitHub"
        Write-Host "2. The branch already exists"
        Write-Host "3. You don't have push permissions"
        Write-Host ""
        Write-Host "Try these commands manually:" -ForegroundColor Yellow
        Write-Host "  git push -u origin main"
        Write-Host "  or"
        Write-Host "  git push -u origin main --force  (if you're sure)"
    }
} else {
    Write-Host ""
    Write-Host "Push cancelled. You can push manually later with:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main"
}

Write-Host ""
Write-Host "=================================="
Write-Host "Script completed!"
Write-Host "=================================="
