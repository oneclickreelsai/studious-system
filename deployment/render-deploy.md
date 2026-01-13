# Deploy to Render - Step by Step

## Prerequisites
- GitHub account
- Render account (https://render.com)
- Your code pushed to GitHub

## Step 1: Prepare Repository

```bash
git init
git add .
git commit -m "Ready for Render deployment"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Step 2: Deploy Backend

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: oneclick-reels-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Plan**: Free or Starter ($7/month)

## Step 3: Add Environment Variables

In Render dashboard, add these environment variables:

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

## Step 4: Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect same repository
3. Configure:
   - **Name**: oneclick-reels-frontend
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

## Step 5: Configure API Proxy

In frontend, update API URL:

Create `frontend/.env.production`:
```
VITE_API_URL=https://oneclick-reels-backend.onrender.com
```

## Step 6: Update CORS

In `backend/api/main.py`, update CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oneclick-reels-frontend.onrender.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 7: Test Deployment

1. Visit your frontend URL
2. Test all features
3. Check Render logs for any errors

## Important Notes

### Free Tier Limitations
- Backend spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free

### Paid Tier Benefits ($7/month)
- Always running
- Faster performance
- More resources
- Better for production

## Troubleshooting

### Build Fails
- Check Python version in `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Check Render build logs

### Backend Timeout
- Increase timeout in Render settings
- Optimize video generation code
- Consider upgrading plan

### Storage Issues
- Render has ephemeral storage
- Use Google Drive for permanent storage
- Consider AWS S3 for large files

## Cost Breakdown

### Free Tier
- Backend: Free (with limitations)
- Frontend: Free
- Total: $0/month

### Starter Tier
- Backend: $7/month
- Frontend: Free
- Total: $7/month

### Professional Setup
- Backend: $25/month (more resources)
- Frontend: Free
- Database: $7/month (if needed)
- Total: $32/month

## Monitoring

1. Enable health checks in Render
2. Set up email alerts
3. Monitor logs regularly
4. Use Render metrics dashboard

## Scaling

To handle more traffic:
1. Upgrade to higher tier
2. Enable auto-scaling
3. Add Redis for caching
4. Use CDN for assets

## Support

- Render docs: https://render.com/docs
- Community: https://community.render.com
- GitHub Issues: [Your repo URL]
