# Push to GitHub - Manual Steps

Your code is ready and committed! Now you need to push it to GitHub.

## The Issue
You're authenticated as `QuantalgoGitBackup` but need to push to `oneclickreelsai/studious-system`.

## Solution Options

### Option 1: Use GitHub CLI (Recommended)

1. **Install GitHub CLI** (if not installed):
   ```powershell
   winget install GitHub.cli
   ```

2. **Login to GitHub**:
   ```powershell
   gh auth login
   ```
   - Choose: GitHub.com
   - Choose: HTTPS
   - Authenticate with your browser

3. **Push the code**:
   ```powershell
   git push -u origin main
   ```

### Option 2: Use Personal Access Token

1. **Create a Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (all)
   - Generate and copy the token

2. **Configure Git**:
   ```powershell
   git remote set-url origin https://YOUR_TOKEN@github.com/oneclickreelsai/studious-system.git
   ```
   Replace `YOUR_TOKEN` with your actual token

3. **Push**:
   ```powershell
   git push -u origin main
   ```

### Option 3: Use SSH

1. **Generate SSH key** (if you don't have one):
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub**:
   - Copy your public key:
     ```powershell
     Get-Content ~/.ssh/id_ed25519.pub | clip
     ```
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste and save

3. **Change remote to SSH**:
   ```powershell
   git remote set-url origin git@github.com:oneclickreelsai/studious-system.git
   ```

4. **Push**:
   ```powershell
   git push -u origin main
   ```

### Option 4: Push from GitHub Desktop

1. **Install GitHub Desktop**: https://desktop.github.com
2. **Open the repository** in GitHub Desktop
3. **Sign in** with your GitHub account
4. **Publish repository** or **Push origin**

## After Successful Push

1. **View your repository**:
   https://github.com/oneclickreelsai/studious-system

2. **Check CI/CD pipeline**:
   https://github.com/oneclickreelsai/studious-system/actions

3. **Add secrets** (required for deployment):
   - Go to: Settings → Secrets and variables → Actions
   - Add these secrets:
     - `RAILWAY_TOKEN`
     - `RENDER_DEPLOY_HOOK`
     - `OPENAI_API_KEY`
     - `PERPLEXITY_API_KEY`
     - `YOUTUBE_CLIENT_ID`
     - `YOUTUBE_CLIENT_SECRET`
     - `YOUTUBE_REFRESH_TOKEN`
     - `FB_PAGE_ID`
     - `FB_ACCESS_TOKEN`
     - `PEXELS_API_KEY`
     - `PIXABAY_API_KEY`

## Current Status

✅ Git repository initialized
✅ Files committed
✅ CI/CD workflows configured
✅ Deployment files ready
⏳ Waiting for push to GitHub

## Quick Command

Once authenticated, just run:
```powershell
git push -u origin main
```

## Need Help?

- GitHub authentication: https://docs.github.com/en/authentication
- GitHub CLI: https://cli.github.com/manual/
- Personal Access Tokens: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
