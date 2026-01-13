# OneClick Reels AI - Web Deployment Guide

## Deployment Options

### Option 1: Railway (Recommended - Easiest)
- **Cost**: Free tier available, then ~$5-20/month
- **Best for**: Quick deployment, automatic scaling
- **GPU Support**: Limited (CPU only on free tier)

### Option 2: Render
- **Cost**: Free tier available, then ~$7-25/month
- **Best for**: Simple deployment, good for startups
- **GPU Support**: No GPU on free tier

### Option 3: DigitalOcean App Platform
- **Cost**: Starting at $5/month
- **Best for**: More control, better performance
- **GPU Support**: Available on higher tiers

### Option 4: AWS EC2 with GPU (Best Performance)
- **Cost**: ~$50-200/month (with GPU)
- **Best for**: Production, high performance
- **GPU Support**: Full NVIDIA GPU support

### Option 5: Google Cloud Run
- **Cost**: Pay per use, ~$10-50/month
- **Best for**: Serverless, auto-scaling
- **GPU Support**: Limited

## Quick Start - Railway Deployment

### Prerequisites
- GitHub account
- Railway account (sign up at railway.app)
- Your code pushed to GitHub

### Steps

1. **Prepare Your Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect and deploy

3. **Configure Environment Variables**
   Add these in Railway dashboard:
   - `OPENAI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`
   - `FB_PAGE_ID`
   - `FB_ACCESS_TOKEN`
   - `PEXELS_API_KEY`
   - `PIXABAY_API_KEY`

4. **Access Your App**
   - Railway provides a public URL
   - Your app will be live at: `https://your-app.railway.app`

## Architecture for Web Deployment

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              (React + Vite)                      │
│         Hosted on: Vercel/Netlify               │
└─────────────────┬───────────────────────────────┘
                  │
                  │ HTTPS API Calls
                  │
┌─────────────────▼───────────────────────────────┐
│                  Backend API                     │
│              (FastAPI + Python)                  │
│         Hosted on: Railway/Render                │
└─────────────────┬───────────────────────────────┘
                  │
                  ├─── Google Drive API
                  ├─── YouTube API
                  ├─── Facebook API
                  ├─── OpenAI API
                  ├─── Perplexity API
                  └─── Pexels/Pixabay API
```

## Performance Considerations

### Without GPU (Cloud Hosting)
- Video generation will be slower (CPU-based encoding)
- Use FFmpeg software encoding instead of NVENC
- Consider using cloud GPU services for video processing

### With GPU (AWS/GCP)
- Much faster video generation
- Requires GPU-enabled instances
- Higher cost but better performance

## Cost Estimation

### Minimal Setup (No GPU)
- Frontend (Vercel): Free
- Backend (Railway): $5-10/month
- Storage (Google Drive): Free (15GB)
- **Total**: ~$5-10/month

### Production Setup (With GPU)
- Frontend (Vercel): Free
- Backend (AWS EC2 g4dn.xlarge): ~$150/month
- Storage (S3 + CloudFront): ~$10-20/month
- **Total**: ~$160-170/month

### Recommended Starter Setup
- Frontend (Vercel): Free
- Backend (Render): $7/month
- Storage (Google Drive): Free
- **Total**: ~$7/month

## Next Steps

1. Choose your deployment platform
2. Follow the specific deployment guide
3. Configure environment variables
4. Test the deployment
5. Set up custom domain (optional)

## Support

For deployment issues, check:
- Railway docs: https://docs.railway.app
- Render docs: https://render.com/docs
- Our GitHub issues: [Your repo URL]
