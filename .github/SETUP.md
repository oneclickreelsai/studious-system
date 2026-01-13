# GitHub Actions CI/CD Setup Guide

## Overview
This repository uses GitHub Actions for automated testing, building, and deployment.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)
**Triggers**: Push to main/develop, Pull Requests
**Jobs**:
- Backend testing and linting
- Frontend testing and building
- Docker image building
- Security scanning
- Deployment to Railway/Render

### 2. Production Deployment (`deploy-production.yml`)
**Triggers**: Release published, Manual dispatch
**Jobs**:
- Build and deploy to production
- Deploy to multiple platforms
- Create deployment summary

### 3. Pull Request Testing (`test-pr.yml`)
**Triggers**: Pull request opened/updated
**Jobs**:
- Test only changed files
- Fast feedback on PRs
- Automated PR comments

### 4. Docker Publishing (`docker-publish.yml`)
**Triggers**: Push to main, Tags
**Jobs**:
- Build Docker images
- Push to GitHub Container Registry
- Multi-platform support

### 5. Dependency Updates (`dependency-update.yml`)
**Triggers**: Weekly schedule, Manual
**Jobs**:
- Update Python dependencies
- Update NPM dependencies
- Create automated PRs

## Required Secrets

### GitHub Repository Secrets
Go to: Settings → Secrets and variables → Actions → New repository secret

#### Deployment Secrets
```
RAILWAY_TOKEN          # Railway CLI token
RENDER_DEPLOY_HOOK     # Render deploy webhook URL
VERCEL_TOKEN          # Vercel deployment token
DOCKER_USERNAME       # Docker Hub username
DOCKER_PASSWORD       # Docker Hub password/token
```

#### Application Secrets (for deployment)
```
OPENAI_API_KEY
PERPLEXITY_API_KEY
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
FB_PAGE_ID
FB_ACCESS_TOKEN
PEXELS_API_KEY
PIXABAY_API_KEY
```

#### URLs (for notifications)
```
BACKEND_URL           # Your backend URL
FRONTEND_URL          # Your frontend URL
```

## How to Get Secrets

### Railway Token
1. Go to https://railway.app
2. Click on your profile → Account Settings
3. Go to "Tokens" tab
4. Create new token
5. Copy and add to GitHub secrets as `RAILWAY_TOKEN`

### Render Deploy Hook
1. Go to your Render dashboard
2. Select your service
3. Go to Settings → Deploy Hook
4. Copy the webhook URL
5. Add to GitHub secrets as `RENDER_DEPLOY_HOOK`

### Vercel Token
1. Go to https://vercel.com
2. Settings → Tokens
3. Create new token
4. Add to GitHub secrets as `VERCEL_TOKEN`

### Docker Hub
1. Go to https://hub.docker.com
2. Account Settings → Security
3. Create Access Token
4. Add username as `DOCKER_USERNAME`
5. Add token as `DOCKER_PASSWORD`

## Setup Steps

### 1. Enable GitHub Actions
- Go to repository Settings
- Actions → General
- Enable "Allow all actions and reusable workflows"

### 2. Add Secrets
- Add all required secrets (see above)
- Verify secrets are added correctly

### 3. Configure Environments
- Go to Settings → Environments
- Create "production" environment
- Add environment-specific secrets if needed
- Configure protection rules

### 4. Test Workflows
```bash
# Push to trigger CI/CD
git add .
git commit -m "test: trigger CI/CD"
git push origin main

# Check Actions tab to see workflow running
```

### 5. Monitor Deployments
- Go to Actions tab
- Click on running workflow
- Monitor logs in real-time
- Check deployment status

## Workflow Customization

### Disable Specific Jobs
Edit workflow files and add `if: false` to jobs you want to disable:

```yaml
deploy-railway:
  if: false  # This job will be skipped
  name: Deploy to Railway
  ...
```

### Change Deployment Platform
Edit `ci-cd.yml` and enable/disable deployment jobs:

```yaml
# Enable Railway deployment
deploy-railway:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  ...

# Disable Render deployment
deploy-render:
  if: false
  ...
```

### Modify Test Commands
Edit test jobs in `ci-cd.yml`:

```yaml
- name: Run tests
  run: |
    pytest tests/ -v --cov=backend
    # Add more test commands here
```

## Troubleshooting

### Workflow Fails
1. Check Actions tab for error logs
2. Verify all secrets are set correctly
3. Check if dependencies are up to date
4. Review recent code changes

### Deployment Fails
1. Check deployment platform logs
2. Verify environment variables
3. Check if services are running
4. Review deployment configuration

### Tests Fail
1. Run tests locally first
2. Check for missing dependencies
3. Verify test environment setup
4. Review test logs in Actions

### Docker Build Fails
1. Check Dockerfile syntax
2. Verify base image availability
3. Check for missing dependencies
4. Review build logs

## Best Practices

### 1. Branch Protection
- Require PR reviews before merging
- Require status checks to pass
- Require branches to be up to date

### 2. Semantic Versioning
- Use tags for releases: `v1.0.0`
- Follow semver: MAJOR.MINOR.PATCH
- Create releases for production deployments

### 3. Commit Messages
- Use conventional commits
- Format: `type(scope): message`
- Examples:
  - `feat: add video generation`
  - `fix: resolve upload issue`
  - `docs: update README`

### 4. Pull Requests
- Keep PRs small and focused
- Write clear descriptions
- Link related issues
- Request reviews

### 5. Testing
- Write tests for new features
- Maintain test coverage
- Run tests locally before pushing
- Fix failing tests immediately

## Monitoring

### GitHub Actions Dashboard
- View workflow runs
- Check success/failure rates
- Monitor execution times
- Review logs

### Deployment Status
- Check deployment environments
- Monitor application health
- Review error logs
- Track performance metrics

## Support

### Documentation
- GitHub Actions: https://docs.github.com/actions
- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs

### Issues
- Report bugs: Create issue with bug template
- Request features: Create issue with feature template
- Ask questions: Use discussions

## Updates

This setup guide is maintained in `.github/SETUP.md`. 
Last updated: 2026-01-13
