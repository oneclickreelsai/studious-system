# Quick push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan

# Initialize if needed
if (-not (Test-Path ".git")) {
    git init
    git remote add origin https://github.com/oneclickreelsai/studious-system.git
}

# Add and commit
git add .gitignore
git add .github/
git add backend/
git add frontend/
git add deployment/
git add Dockerfile
git add docker-compose.yml
git add requirements.txt
git add run.py
git add server.py
git add README.md
git add render.yaml
git add railway.toml
git add vercel.json
git add .dockerignore

git commit -m "feat: add CI/CD pipeline and deployment configuration"

# Push
Write-Host "Pushing to main branch..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "Done! Check: https://github.com/oneclickreelsai/studious-system/actions" -ForegroundColor Green
