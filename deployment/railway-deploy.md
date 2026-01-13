# Deploy to Railway - Step by Step

## Prerequisites
- GitHub account
- Railway account (https://railway.app)
- Your code pushed to GitHub

## Step 1: Prepare Your Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"

# Create GitHub repo and push
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Step 2: Deploy Backend to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your repository
6. Railway will auto-detect Python and deploy

## Step 3: Configure Environment Variables

In Railway dashboard, go to Variables tab and add:

```
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_secret
YOUTUBE_REFRESH_TOKEN=your_token
FB_PAGE_ID=your_page_id
FB_ACCESS_TOKEN=your_token
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
```

## Step 4: Get Your Backend URL

1. In Railway dashboard, go to Settings
2. Click "Generate Domain"
3. Copy the URL (e.g., `https://your-app.railway.app`)

## Step 5: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Set Root Directory to `frontend`
5. Add Environment Variable:
   ```
   VITE_API_URL=https://your-app.railway.app
   ```
6. Click "Deploy"

## Step 6: Update Frontend API URL

Edit `frontend/src/main.tsx` or create `.env.production`:

```env
VITE_API_URL=https://your-backend.railway.app
```

Redeploy frontend.

## Step 7: Test Your Deployment

1. Visit your Vercel URL
2. Test API connectivity
3. Try generating a video
4. Check logs in Railway dashboard

## Troubleshooting

### Backend not starting
- Check Railway logs
- Verify all environment variables are set
- Check if port 8002 is exposed

### Frontend can't connect to backend
- Verify CORS is enabled in backend
- Check API URL in frontend
- Verify backend is running

### Video generation fails
- Check FFmpeg is installed (should be in Dockerfile)
- Verify API keys are correct
- Check Railway logs for errors

## Cost Estimation

- Railway: $5/month (Hobby plan)
- Vercel: Free (Hobby plan)
- Total: ~$5/month

## Scaling

To handle more traffic:
1. Upgrade Railway plan
2. Add Redis for caching
3. Use CDN for video delivery
4. Consider AWS S3 for storage

## Support

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- GitHub Issues: [Your repo URL]
