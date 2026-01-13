"""
OneClick Reels AI - FastAPI Backend
"""
import os
import sys
from pathlib import Path

# Set working directory and path
PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import psutil
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv("config.env")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Core Modules - Each module imported separately for better error handling
db = None
download_meta_ai_content = None
generate_facebook_post = None
post_to_facebook = None
get_page_stats = None
get_recent_posts = None
get_topic_suggestions = None
get_trending_news = None
download_youtube_video = None
get_video_info = None
health_checker = None
music_gen = None
music_finder = None
kokoro_engine = None
video_orchestrator = None

# Load JSON Database
try:
    from backend.database.json_db import db
    logger.info("JSON Database loaded successfully")
except ImportError as e:
    logger.warning(f"Database module not loaded: {e}")

try:
    from backend.core.video_engine.meta_ai_downloader import download_meta_ai_content
except ImportError as e:
    logger.warning(f"Meta AI downloader not loaded: {e}")

try:
    from backend.core.ai_engine.facebook_poster import (
        generate_facebook_post, 
        post_to_facebook, 
        get_page_stats,
        get_recent_posts,
        get_topic_suggestions,
        post_photo_to_facebook
    )
except ImportError as e:
    logger.warning(f"Facebook poster not loaded: {e}")

try:
    from backend.core.ai_engine.news_agent import get_trending_news
except ImportError as e:
    logger.warning(f"News agent not loaded: {e}")

try:
    from backend.core.video_engine.youtube_downloader import download_youtube_video, get_video_info
except ImportError as e:
    logger.warning(f"YouTube downloader not loaded: {e}")

try:
    from backend.utils.health_checker import health_checker
except ImportError as e:
    logger.warning(f"Health checker not loaded: {e}")

try:
    from backend.core.audio_engine.music_generator import music_gen
except ImportError as e:
    logger.warning(f"Music generator not loaded: {e}")

try:
    from backend.core.audio_engine.music_finder import music_finder
except ImportError as e:
    logger.warning(f"Music finder not loaded: {e}")

try:
    from backend.core.audio_engine.kokoro_engine import kokoro_engine
except ImportError as e:
    logger.warning(f"Kokoro engine not loaded: {e}")

try:
    from backend.core.video_engine.video_orchestrator import video_orchestrator
except ImportError as e:
    logger.warning(f"Video orchestrator not loaded: {e}")

# Initialize app
app = FastAPI(
    title="OneClick Reels AI API",
    version="2.0.0",
    description="AI-powered video generation"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory=PROJECT_ROOT / "output"), name="output")
app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "assets"), name="assets")

# ===== Request Models =====
class GenerationRequest(BaseModel):
    niche: Optional[str] = None
    topic: Optional[str] = None
    upload_youtube: bool = False
    upload_facebook: bool = False

class MetaVideoRequest(BaseModel):
    url: str

class FacebookPreviewRequest(BaseModel):
    topic: str
    niche: str = "general"

class FacebookPostRequest(BaseModel):
    topic: str
    niche: str = "general"
    post_now: bool = True
    content: Optional[str] = None

class NewsRequest(BaseModel):
    category: str

class YouTubeDownloadRequest(BaseModel):
    url: str
    quality: str = "720p"

class BatchGenerationRequest(BaseModel):
    count: int = 3
    niche: Optional[str] = None
    upload_youtube: bool = True
    upload_facebook: bool = False

class AddMusicRequest(BaseModel):
    video_path: str
    prompt: Optional[str] = ""
    mood: Optional[str] = None

class MetaLoginRequest(BaseModel):
    timeout: int = 300

class GenerateFromScriptRequest(BaseModel):
    script: str
    niche: str = "general"
    topic: str
    voice_id: str = "af_heart"
    music_prompt: Optional[str] = None
    visual_keywords: Optional[str] = None

class ScriptToVideoRequest(BaseModel):
    script: str
    voice_id: str = "af_heart"
    theme: str = "nature"
    music_prompt: Optional[str] = None

class SocialUploadRequest(BaseModel):
    video_path: str
    caption: str
    platforms: List[str] = ["instagram", "facebook"]

@app.post("/api/social/upload")
async def api_social_upload(request: SocialUploadRequest):
    """Upload video to social media using browser automation."""
    try:
        # Initialize poster (headless=False so user can see/interact if needed)
        # In production, we might want headless=True, but for this desktop app, visible is better for debugging login
        poster = SocialMediaPoster(headless=False)
        
        # Verify file exists
        if not os.path.exists(request.video_path):
             # Try adding project root
            request.video_path = os.path.join(PROJECT_ROOT, request.video_path.lstrip("/"))
            
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail=f"Video file not found: {request.video_path}")

        result = await poster.upload_reel(
            video_path=request.video_path,
            caption=request.caption
        )
        
        return result
    except Exception as e:
        logger.error(f"Social upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/generate-from-script")
async def api_generate_video_from_script(request: ScriptToVideoRequest):
    """Generate a full video from script using Orchestrator."""
    if not video_orchestrator:
        raise HTTPException(status_code=501, detail="Video orchestrator not loaded")
    
    try:
        result = await video_orchestrator.generate_video_from_script(
            script=request.script,
            voice_id=request.voice_id,
            theme=request.theme,
            music_prompt=request.music_prompt
        )
        return result
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== API Endpoints =====

@app.get("/")
async def root():
    return {
        "name": "OneClick Reels AI API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": "running",
            "perplexity": "configured" if os.getenv("PERPLEXITY_API_KEY") else "not configured",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not configured (fallback)",
            "youtube": "configured" if os.getenv("YOUTUBE_CLIENT_ID") else "not configured",
            "pexels": "configured" if os.getenv("PEXELS_API_KEY") else "not configured"
        }
    }

@app.get("/metrics")
async def get_metrics():
    """System metrics for frontend SystemHealth component."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": time.time(),
        "status": "healthy"
    }

@app.get("/system/status")
async def get_system_status():
    return await get_metrics()

@app.get("/api/settings")
async def get_settings():
    """Get configuration status for Settings page."""
    # Reload environment variables to ensure fresh values
    from dotenv import dotenv_values
    env_vars = dotenv_values("config.env")
    
    return {
        "has_openai_key": bool(env_vars.get("OPENAI_API_KEY")),
        "has_youtube_credentials": bool(env_vars.get("YOUTUBE_CLIENT_ID") and env_vars.get("YOUTUBE_REFRESH_TOKEN")),
        "has_facebook_credentials": bool(env_vars.get("FB_PAGE_ID") and env_vars.get("FB_ACCESS_TOKEN")),
        "has_pexels_key": bool(env_vars.get("PEXELS_API_KEY")),
        "has_pixabay_key": bool(env_vars.get("PIXABAY_API_KEY")),
        "has_perplexity_key": bool(env_vars.get("PERPLEXITY_API_KEY")),
        "enable_caching": env_vars.get("ENABLE_CACHING", "true").lower() == "true",
        "fb_page_id": env_vars.get("FB_PAGE_ID", ""),
        "openai_key": env_vars.get("OPENAI_API_KEY", "")[:20] + "..." if env_vars.get("OPENAI_API_KEY") else "",
        "perplexity_key": env_vars.get("PERPLEXITY_API_KEY", "")[:20] + "..." if env_vars.get("PERPLEXITY_API_KEY") else "",
        "youtube_client_id": env_vars.get("YOUTUBE_CLIENT_ID", "")[:30] + "..." if env_vars.get("YOUTUBE_CLIENT_ID") else "",
        "youtube_refresh_token": env_vars.get("YOUTUBE_REFRESH_TOKEN", "")[:30] + "..." if env_vars.get("YOUTUBE_REFRESH_TOKEN") else "",
        "pexels_key": env_vars.get("PEXELS_API_KEY", "")[:20] + "..." if env_vars.get("PEXELS_API_KEY") else "",
        "pixabay_key": env_vars.get("PIXABAY_API_KEY", "")[:20] + "..." if env_vars.get("PIXABAY_API_KEY") else "",
    }

# --- Post Generation ---
@app.post("/generate")
async def generate_video(request: GenerationRequest):
    """Generate a video."""
    try:
        from backend.core.ai_engine.niche_selector import select_niche
        from backend.core.ai_engine.script_generator import generate_script
        from backend.core.ai_engine.caption_hashtags import generate_caption
        
        # Select niche/topic
        if not request.niche or not request.topic:
            niche_data = select_niche()
            niche = request.niche or niche_data["niche"]
            topic = request.topic or niche_data["topic"]
        else:
            niche = request.niche
            topic = request.topic
        
        logger.info(f"Generating video: {niche}/{topic}")
        
        # Generate script
        script = generate_script(niche, topic)
        
        # Generate metadata
        meta = generate_caption(niche, topic)
        
        # Record in DB
        if db:
            try:
                # Assuming generic signature, or skip if complex
                 pass 
                 # db.add_video(title=f"{niche} - {topic}", niche=niche, topic=topic, script=script)
            except:
                pass
        
        return {
            "success": True,
            "niche": niche,
            "topic": topic,
            "script": script,
            "metadata": meta
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-from-script")
async def api_generate_from_script(request: GenerateFromScriptRequest):
    """Generate video from provided script."""
    try:
        from backend.core.video_engine.voiceover import generate_voiceover
        from backend.core.video_engine.pexels_downloader import get_video_for_keyword
        from backend.core.video_engine.advanced_video_builder import advanced_video_builder
        import asyncio
        
        loop = asyncio.get_event_loop()
        
        # 1. Voiceover - run in thread pool to avoid async conflicts
        logger.info("Generating voiceover...")
        voiceover = await loop.run_in_executor(
            None, 
            lambda: generate_voiceover(request.script, niche=request.niche)
        )
        
        if not voiceover:
            raise HTTPException(status_code=500, detail="Voiceover generation failed")
        
        # 2. Background Video
        logger.info(f"Searching background for: {request.topic}")
        # Use visual keywords if available, else use topic directly
        search_term = request.visual_keywords if request.visual_keywords else request.topic
        # If visual_keywords suggests multiple tags, split and take first few for better search
        if "," in search_term:
            search_term = search_term.split(",")[0].strip()
            
        video_path = await loop.run_in_executor(None, lambda: get_video_for_keyword(search_term))
        
        if not video_path:
            raise HTTPException(status_code=500, detail="Could not find background video")
        
        # 3. Build Video
        logger.info("Building video...")
        output_filename = f"reel_{int(time.time())}.mp4"
        output_path = f"output/{output_filename}"
        
        def build_task():
             return advanced_video_builder.build_video_gpu_accelerated(
                background_video=video_path,
                voiceover_audio=voiceover,
                script=request.script,
                niche=request.niche,
                output_path=output_path,
                quality="high"
            )
            
        final_video_path = await loop.run_in_executor(None, build_task)
        
        return {
            "success": True, 
            "video_path": f"/output/{output_filename}",
            "filename": output_filename,
            "full_path": str(final_video_path)
        }
        
    except Exception as e:
        logger.error(f"Generation from script failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/niches")
async def get_niches():
    """Get available niches."""
    from backend.core.ai_engine.niche_selector import NICHES
    return {"niches": NICHES}

# --- Meta AI Tools ---
class MetaToYouTubeRequest(BaseModel):
    url: str
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    analyze_content: bool = True
    upload: bool = True

@app.post("/api/download-meta-video")
async def api_download_meta_video(request: MetaVideoRequest):
    """Download video from Meta AI post."""
    if not download_meta_ai_content:
        raise HTTPException(status_code=501, detail="Meta AI module failed to load.")
        
    try:
        logger.info(f"Downloading Meta AI video from: {request.url}")
        
        # Run sync function in thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, download_meta_ai_content, request.url)
            
        if not result:
            raise HTTPException(status_code=400, detail="Failed to download video. Check URL or try again.")
            
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Meta AI download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meta-to-youtube")
async def api_meta_to_youtube(request: MetaToYouTubeRequest):
    """Download Meta AI video, analyze content, generate metadata, and upload to YouTube."""
    try:
        from backend.core.video_engine.meta_to_youtube import meta_ai_to_youtube
        
        logger.info(f"Meta AI to YouTube pipeline: {request.url}")
        
        # Run pipeline
        import asyncio
        loop = asyncio.get_event_loop()
        
        def run_pipeline():
            return meta_ai_to_youtube(
                request.url,
                custom_title=request.custom_title,
                custom_desc=request.custom_description,
                analyze_content=request.analyze_content
            )
        
        result = await loop.run_in_executor(None, run_pipeline)
        return result
        
    except Exception as e:
        logger.error(f"Meta to YouTube error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-video")
async def api_analyze_video(video_path: str = Form(...)):
    """Analyze video content using OCR and AI vision."""
    try:
        from backend.core.ai_engine.video_analyzer import analyze_video_content
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, analyze_video_content, video_path)
        
        return {"success": True, "analysis": result}
        return {"success": True, "analysis": result}
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch-generate")
async def api_batch_generate(request: BatchGenerationRequest, background_tasks: BackgroundTasks):
    """Start batch video generation."""
    try:
        from cli.auto_pipeline import run_batch_pipeline
        
        # Run in background
        background_tasks.add_task(
            run_batch_pipeline,
            count=request.count,
            category=request.niche,
            upload_youtube=request.upload_youtube,
            upload_facebook=request.upload_facebook,
            headless=True 
        )
        
        return {"success": True, "message": f"Started batch generation for {request.count} videos", "status": "processing"}
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add-music")
async def api_add_music(request: AddMusicRequest):
    """Add AI-selected music to a video."""
    try:
        from backend.core.video_engine.audio_enhancer import enhance_video_with_audio
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        
        def run_enhancer():
            return enhance_video_with_audio(request.video_path, request.prompt)
            
        result = await loop.run_in_executor(None, run_enhancer)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Add music error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content-plan")
async def api_content_plan(days: int = 3):
    """Get daily content plan."""
    try:
        from backend.core.ai_engine.content_curator import get_daily_content_plan
        plan = get_daily_content_plan(days)
        return {"success": True, "plan": plan}
    except Exception as e:
        logger.error(f"Content plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meta-login")
async def api_meta_login(request: MetaLoginRequest, background_tasks: BackgroundTasks):
    """Trigger browser for Meta AI login."""
    try:
        from backend.core.video_engine.meta_ai_generator import MetaAIGenerator
        import asyncio

        async def do_login():
            gen = MetaAIGenerator(headless=False)
            await gen.start()
            await gen.wait_for_login(timeout=request.timeout)
            await gen.stop()
            
        # We can't easily await async function in background task from sync context without a wrapper
        # But FastAPI BackgroundTasks can accept async functions
        background_tasks.add_task(do_login)
        
        return {"success": True, "message": "Browser opening for login..."}
    except Exception as e:
        logger.error(f"Meta login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Facebook Tools ---
@app.get("/api/facebook-stats")
async def api_facebook_stats():
    """Get Facebook Page stats."""
    if not get_page_stats:
         return {"page": {"success": False, "error": "Module not loaded"}, "recent_posts": [], "topics": {}}
         
    try:
        stats = get_page_stats()
        recent = get_recent_posts(limit=5)
        
        # Get topic suggestions for all niches
        topics = {
             "trading": get_topic_suggestions("trading"),
             "finance": get_topic_suggestions("finance"),
             "tech": get_topic_suggestions("tech"),
             "motivation": get_topic_suggestions("motivation"),
             "general": get_topic_suggestions("general")
        }
        
        return {
            "page": stats,
            "recent_posts": recent,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"Facebook stats error: {e}")
        # Return fallback structure so UI doesn't crash
        return {
            "page": {"success": False, "error": str(e)},
            "recent_posts": [],
            "topics": {}
        }

@app.post("/api/facebook-preview")
async def api_facebook_preview(request: FacebookPreviewRequest):
    """Generate preview for Facebook post."""
    if not generate_facebook_post:
         return {"success": False, "error": "Module not loaded"}
         
    try:
        result = generate_facebook_post(request.topic, request.niche)
        return result
    except Exception as e:
        logger.error(f"Facebook preview error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/facebook-post")
async def api_facebook_post(
    topic: str = Form(...),
    niche: str = Form("general"),
    post_now: bool = Form(True),
    content: Optional[str] = Form(None),
    image: UploadFile = File(None),
    image_path: Optional[str] = Form(None)
):
    """Post to Facebook (Text or Image)."""
    if not post_to_facebook:
          raise HTTPException(status_code=500, detail="Module not loaded")
          
    try:
        # If content provided (from preview), use it. Otherwise generate new.
        msg_content = content
        if not msg_content:
            gen_res = generate_facebook_post(topic, niche)
            if not gen_res.get("success"):
                raise HTTPException(status_code=500, detail=gen_res.get("error"))
            msg_content = gen_res.get("content")
            
        if post_now:
            if image:
                # Handle Image Upload
                timestamp = int(time.time())
                filename = f"temp_fb_img_{timestamp}_{image.filename}"
                temp_path = f"temp/{filename}"
                os.makedirs("temp", exist_ok=True)
                
                with open(temp_path, "wb") as buffer:
                    import shutil
                    shutil.copyfileobj(image.file, buffer)
                    
                result = post_photo_to_facebook(temp_path, msg_content)
                
                # Cleanup
                try:
                    os.remove(temp_path)
                except:
                    pass
                return result
            elif image_path:
                # Handle Dynamic/Local Image
                if os.path.exists(image_path):
                    result = post_photo_to_facebook(image_path, msg_content)
                    return result
                else:
                     raise HTTPException(status_code=400, detail=f"Image path not found: {image_path}")
            else:
                # Text Only
                result = post_to_facebook(msg_content)
                return result
        else:
            return {"success": True, "posted": False, "content": msg_content}
            
    except Exception as e:
        logger.error(f"Facebook post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- News Generator ---
@app.post("/api/news-generate")
async def api_generate_news(request: NewsRequest):
    """Generate viral news content."""
    if not get_trending_news:
         raise HTTPException(status_code=501, detail="News module failed to load.")
    try:
        news = get_trending_news(request.category)
        return {"success": True, "news": news}
    except Exception as e:
        logger.error(f"News generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- YouTube Downloader ---
@app.post("/api/youtube-info")
async def api_youtube_info(request: YouTubeDownloadRequest):
    """Get YouTube video info without downloading."""
    if not get_video_info:
        raise HTTPException(status_code=501, detail="YouTube module not loaded")
    try:
        info = get_video_info(request.url)
        return {"success": True, **info}
    except Exception as e:
        logger.error(f"YouTube info error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/youtube-download")
async def api_youtube_download(request: YouTubeDownloadRequest, background_tasks: BackgroundTasks):
    """Download YouTube video."""
    if not download_youtube_video:
        raise HTTPException(status_code=501, detail="YouTube module not loaded")
    try:
        result = download_youtube_video(request.url)
        return {
            "success": True,
            "title": result.get("title"),
            "file_path": result.get("file_path"),
            "duration": result.get("duration"),
            "channel": result.get("channel"),
            "output_folder": result.get("output_folder")
        }
    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Video Upload ---
@app.post("/api/upload-video")
async def api_upload_video(
    file: UploadFile = File(...),
    title: str = Query(...),
    niche: str = Query("general"),
    upload_youtube: bool = Query(False)
):
    """Handle video uploads."""
    try:
        # Save file
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        file_path = f"output/uploads/{filename}"
        os.makedirs("output/uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
        # Log to DB (if DB available)
        if db:
            db.add_upload(title=title, filename=filename, niche=niche, file_path=file_path)
            
        return {
            "success": True, 
            "filename": filename, 
            "path": file_path,
            "message": "Upload successful"
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-facebook-reel")
async def api_upload_facebook_reel(
    file: UploadFile = File(...),
    caption: str = Form("")
):
    """Upload video reel to Facebook Page."""
    try:
        from backend.core.post_engine.facebook import upload_facebook_reel
        import shutil
        
        # Save file temporarily
        timestamp = int(time.time())
        filename = f"fb_reel_{timestamp}_{file.filename}"
        temp_path = f"temp/{filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to Facebook
        video_id = upload_facebook_reel(temp_path, caption)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            "success": True,
            "video_id": video_id,
            "message": "Reel uploaded successfully!"
        }
    except Exception as e:
        logger.error(f"Facebook Reel upload error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/upload-instagram-reel")
async def api_upload_instagram_reel(
    file: UploadFile = File(...),
    caption: str = Form("")
):
    """Upload video reel to Instagram via Facebook Graph API.
    
    Requires:
    - Facebook Page linked to Instagram Business/Creator account
    - Page Access Token with instagram_content_publish permission
    """
    try:
        import shutil
        import requests
        
        # Get Instagram Account ID from Facebook Page
        PAGE_ID = os.getenv("FB_PAGE_ID")
        ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
        
        if not PAGE_ID or not ACCESS_TOKEN:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        # Exchange for Page Token
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={ACCESS_TOKEN}"
        token_res = requests.get(token_url, timeout=10)
        if token_res.status_code == 200 and "access_token" in token_res.json():
            page_token = token_res.json()["access_token"]
        else:
            page_token = ACCESS_TOKEN
        
        # Get Instagram Business Account ID linked to Page
        ig_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=instagram_business_account&access_token={page_token}"
        ig_res = requests.get(ig_url, timeout=10)
        
        if ig_res.status_code != 200:
            return {"success": False, "error": f"Failed to get Instagram account: {ig_res.text}"}
        
        ig_data = ig_res.json()
        if "instagram_business_account" not in ig_data:
            return {"success": False, "error": "No Instagram Business account linked to this Facebook Page. Link your Instagram account in Facebook Page settings."}
        
        ig_account_id = ig_data["instagram_business_account"]["id"]
        logger.info(f"Found Instagram Account ID: {ig_account_id}")
        
        # Save file temporarily
        timestamp = int(time.time())
        filename = f"ig_reel_{timestamp}_{file.filename}"
        temp_path = f"temp/{filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # For Instagram Reels, we need to upload video to a publicly accessible URL
        # Since we're running locally, we'll use the Facebook resumable upload API
        
        # Step 1: Create container for Reel
        # Note: Instagram requires video_url to be publicly accessible
        # For local files, you'd need to host it or use a different approach
        
        # For now, return info about the limitation
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            "success": False,
            "error": "Instagram Reel upload requires a publicly accessible video URL. For local uploads, please use a CDN or cloud storage first. Alternatively, use Facebook Reel Upload which supports direct file upload.",
            "suggestion": "Upload your video to a cloud service (e.g., S3, Google Drive public link) and provide the URL, or use the Facebook Reel Upload feature instead."
        }
        
    except Exception as e:
        logger.error(f"Instagram Reel upload error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

class InstagramReelUrlRequest(BaseModel):
    video_url: str
    caption: str = ""

@app.get("/api/health")
async def api_health():
    """Get system health status."""
    if not health_checker:
        raise HTTPException(status_code=501, detail="Health checker not loaded")
    return health_checker.health_check_with_cache()

# --- Audio Studio Endpoints ---
@app.get("/api/audio/search")
async def api_audio_search(q: str):
    """Search for music tracks on YouTube."""
    if not music_finder:
        raise HTTPException(status_code=501, detail="Music module not loaded")
    return {"success": True, "results": music_finder.search_music(q)}

class AudioDownloadRequest(BaseModel):
    video_id: str

@app.post("/api/audio/download")
async def api_audio_download(request: AudioDownloadRequest):
    """Download audio track."""
    if not music_finder:
        raise HTTPException(status_code=501, detail="Music module not loaded")
        
    result = music_finder.download_music(request.video_id)
    if not result:
        raise HTTPException(status_code=400, detail="Download failed")
        
    return {"success": True, "track": result}

class AudioGenRequest(BaseModel):
    prompt: str
    duration: int = 15

@app.post("/api/audio/generate")
async def api_generate_audio(request: AudioGenRequest):
    """Generate generic AI music."""
    try:
        logging.info(f"Generating audio for prompt: {request.prompt} ({request.duration}s)")
        file_url = music_gen.generate(request.prompt, request.duration)
        return {
            "success": True,
            "url": file_url,
            "filename": os.path.basename(file_url)
        }
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class AddMusicRequest(BaseModel):
    video_path: str
    audio_path: Optional[str] = None
    prompt: Optional[str] = None
    mix: bool = False

@app.post("/api/add-music")
async def api_add_music(request: AddMusicRequest):
    """Add configured or AI-selected music to video."""
    try:
        from backend.core.video_engine.advanced_video_builder import advanced_video_builder
        
        video_path = request.video_path.strip().replace('"', '')
        if not os.path.exists(video_path):
             raise HTTPException(status_code=404, detail="Video file not found")

        audio_path = request.audio_path
        music_name = "Custom Track"
        
        # If no audio provided, find one using prompt
        if not audio_path and request.prompt and music_finder:
            logger.info(f"Finding music for prompt: {request.prompt}")
            results = music_finder.search_music(str(request.prompt), limit=1)
            if results:
                track = results[0]
                music_name = track['title']
                dl_result = music_finder.download_music(track['id'])
                if dl_result:
                    audio_path = dl_result['full_path']
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=400, detail="No suitable audio found or provided")
            
        # Process
        timestamp = int(time.time())
        output_filename = f"enhanced_{timestamp}.mp4"
        output_path = f"output/{output_filename}"
        
        final_path = advanced_video_builder.add_audio_to_video(
            video_path=video_path,
            audio_path=audio_path,
            output_path=output_path,
            mix=request.mix
        )
        
        return {
            "success": True,
            "output_video": str(Path(final_path).absolute()),
            "music_track": {
                "name": music_name,
                "url": audio_path,
                "mood": request.prompt or "Custom"
            }
        }

    except Exception as e:
        logger.error(f"Add music failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0

@app.post("/api/tts/generate")
async def api_tts_generate(request: TTSRequest):
    """Generate speech from text using local Kokoro model."""
    if not kokoro_engine:
        raise HTTPException(status_code=501, detail="Kokoro TTS module not loaded")
    
    try:
        audio_url = kokoro_engine.generate(request.text, request.voice, request.speed)
        return {
            "success": True,
            "url": audio_url,
            "filename": os.path.basename(audio_url)
        }
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/voices")
async def api_tts_voices():
    """Get available Kokoro voices."""
    if not kokoro_engine:
        return {"voices": []}
    return {"voices": kokoro_engine.get_available_voices()}

@app.get("/api/assets")
async def api_list_assets():
    """List all generated assets in output directory."""
    output_dir = PROJECT_ROOT / "output"
    assets = []
    
    if not output_dir.exists():
        return {"success": True, "assets": []}
        
    for file_path in output_dir.glob("*"):
        if file_path.is_file():
            # Determine type
            ext = file_path.suffix.lower()
            asset_type = "unknown"
            if ext in [".mp4", ".mov", ".avi"]:
                asset_type = "video"
            elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                asset_type = "image"
            elif ext in [".mp3", ".wav", ".aac"]:
                asset_type = "audio"
            
            # Get stats
            stats = file_path.stat()
            
            assets.append({
                "name": file_path.name,
                "path": f"/output/{file_path.name}",
                "type": asset_type,
                "size": stats.st_size,
                "created": stats.st_mtime,
                "created_str": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sort by newest first
    assets.sort(key=lambda x: x["created"], reverse=True)
    
    return {"success": True, "assets": assets}

@app.delete("/api/assets/{filename}")
async def api_delete_asset(filename: str):
    """Delete an asset file."""
    file_path = PROJECT_ROOT / "output" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        os.remove(file_path)
        return {"success": True, "message": "File deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-instagram-reel-url")
async def api_upload_instagram_reel_url(request: InstagramReelUrlRequest):
    """Upload video reel to Instagram via public URL.
    
    This is the recommended method as Instagram API requires publicly accessible video URLs.
    """
    try:
        import requests
        
        # Get credentials
        PAGE_ID = os.getenv("FB_PAGE_ID")
        ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
        
        if not PAGE_ID or not ACCESS_TOKEN:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        # Exchange for Page Token
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={ACCESS_TOKEN}"
        token_res = requests.get(token_url, timeout=10)
        if token_res.status_code == 200 and "access_token" in token_res.json():
            page_token = token_res.json()["access_token"]
        else:
            page_token = ACCESS_TOKEN
        
        # Get Instagram Business Account ID
        ig_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=instagram_business_account&access_token={page_token}"
        ig_res = requests.get(ig_url, timeout=10)
        
        if ig_res.status_code != 200:
            return {"success": False, "error": f"Failed to get Instagram account: {ig_res.text}"}
        
        ig_data = ig_res.json()
        if "instagram_business_account" not in ig_data:
            return {"success": False, "error": "No Instagram Business account linked to this Facebook Page"}
        
        ig_account_id = ig_data["instagram_business_account"]["id"]
        logger.info(f"Found Instagram Account ID: {ig_account_id}")
        
        # Step 1: Create media container for Reel
        container_url = f"https://graph.facebook.com/v20.0/{ig_account_id}/media"
        container_params = {
            "media_type": "REELS",
            "video_url": request.video_url,
            "caption": request.caption,
            "access_token": page_token
        }
        
        container_res = requests.post(container_url, data=container_params, timeout=30)
        
        if container_res.status_code != 200:
            return {"success": False, "error": f"Failed to create media container: {container_res.text}"}
        
        container_id = container_res.json().get("id")
        logger.info(f"Created media container: {container_id}")
        
        # Step 2: Wait for video processing and publish
        # Instagram processes the video asynchronously
        import time as time_module
        max_retries = 30
        for i in range(max_retries):
            status_url = f"https://graph.facebook.com/v20.0/{container_id}?fields=status_code&access_token={page_token}"
            status_res = requests.get(status_url, timeout=10)
            
            if status_res.status_code == 200:
                status = status_res.json().get("status_code")
                if status == "FINISHED":
                    break
                elif status == "ERROR":
                    return {"success": False, "error": "Video processing failed on Instagram's side"}
            
            time_module.sleep(2)
        
        # Step 3: Publish the container
        publish_url = f"https://graph.facebook.com/v20.0/{ig_account_id}/media_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": page_token
        }
        
        publish_res = requests.post(publish_url, data=publish_params, timeout=30)
        
        if publish_res.status_code != 200:
            return {"success": False, "error": f"Failed to publish reel: {publish_res.text}"}
        
        media_id = publish_res.json().get("id")
        logger.info(f"Published Instagram Reel: {media_id}")
        
        return {
            "success": True,
            "media_id": media_id,
            "message": "Reel published successfully!"
        }
        
    except Exception as e:
        logger.error(f"Instagram Reel URL upload error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# --- Admin Dashboard Stats ---
@app.get("/api/stats")
async def get_dashboard_stats():
    if db: return db.get_total_stats()
    return {}

# --- Upload and Publish ---
@app.post("/api/upload-and-publish")
async def api_upload_and_publish(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    niche: str = Form("general"),
    privacy: str = Form("public"),
    upload_youtube: str = Form("false"),
    upload_facebook: str = Form("false")
):
    """Upload video and publish to YouTube/Facebook."""
    try:
        # Save file first
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        file_path = f"output/uploads/{filename}"
        os.makedirs("output/uploads", exist_ok=True)
        
        import shutil
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        result = {"success": True, "file_path": file_path}
        
        # Upload to YouTube
        if upload_youtube.lower() == "true":
            try:
                from backend.core.post_engine.youtube import upload_youtube_short
                video_id = upload_youtube_short(file_path, title, description, privacy)
                result["youtube_id"] = video_id
                result["youtube_url"] = f"https://youtube.com/watch?v={video_id}"
                logger.info(f"YouTube upload success: {video_id}")
            except Exception as e:
                logger.error(f"YouTube upload failed: {e}")
                result["youtube_error"] = str(e)
        
        # Upload to Facebook
        if upload_facebook.lower() == "true":
            try:
                from backend.core.post_engine.facebook import upload_facebook_reel
                caption = f"{title}\n\n{description}" if description else title
                fb_id = upload_facebook_reel(file_path, caption)
                result["facebook_id"] = fb_id
                result["facebook_url"] = f"https://facebook.com/{fb_id}"
                logger.info(f"Facebook upload success: {fb_id}")
            except Exception as e:
                logger.error(f"Facebook upload failed: {e}")
                result["facebook_error"] = str(e)
        
        return result
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-metadata")
async def api_generate_metadata(request: dict):
    """Generate AI metadata for video."""
    try:
        title = request.get("title", "")
        niche = request.get("niche", "general")
        
        from backend.core.ai_engine.caption_hashtags import generate_caption
        meta = generate_caption(niche, title)
        
        return {
            "success": True,
            "title": meta.get("title", title),
            "description": meta.get("description", ""),
            "hashtags": meta.get("hashtags", [])
        }
    except Exception as e:
        logger.error(f"Metadata generation error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/videos")
async def get_videos(limit: int = 50):
    if db: return {"videos": db.get_videos(limit=limit)}
    return {"videos": []}

@app.get("/api/uploads")
async def get_uploads(limit: int = 50):
    if db: return {"uploads": db.get_uploads(limit=limit)}
    return {"uploads": []}

@app.get("/api/accounts")
async def get_accounts():
    if db: return {"accounts": db.get_accounts()}
    return {"accounts": []}

@app.get("/api/links")
async def get_links():
    if db: return {"links": db.get_links()}
    return {"links": []}

@app.get("/api/analytics")
async def get_analytics(days: int = 30):
    if db: return db.get_analytics(days=days)
    return {}

# ===== Google Drive API Endpoints =====

SYNC_LOG_FILE = "sync_log.json"

@app.get("/api/drive/sync-log")
async def get_drive_sync_log():
    """Get Google Drive sync log and stats."""
    try:
        import json
        from pathlib import Path
        
        sync_log = {}
        stats = None
        
        if Path(SYNC_LOG_FILE).exists():
            with open(SYNC_LOG_FILE, 'r') as f:
                sync_log = json.load(f)
            
            # Calculate stats
            total_files = len(sync_log)
            total_size = sum(int(v.get('size', 0)) for v in sync_log.values())
            
            # Get last sync time
            last_sync = None
            for v in sync_log.values():
                uploaded_at = v.get('uploaded_at')
                if uploaded_at:
                    if not last_sync or uploaded_at > last_sync:
                        last_sync = uploaded_at
            
            stats = {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "last_sync": last_sync[:16].replace('T', ' ') if last_sync else "Never",
                "status": "synced"
            }
        
        return {"success": True, "log": sync_log, "stats": stats}
    except Exception as e:
        logger.error(f"Failed to get sync log: {e}")
        return {"success": False, "error": str(e)}

class DriveSyncRequest(BaseModel):
    files: Optional[List[str]] = None

@app.post("/api/drive/sync")
async def sync_to_drive(request: DriveSyncRequest, background_tasks: BackgroundTasks):
    """Sync output folder to Google Drive."""
    try:
        import subprocess
        import sys
        
        # Run sync script in background
        def run_sync():
            try:
                result = subprocess.run(
                    [sys.executable, "sync_output_to_drive.py"],
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_ROOT)
                )
                logger.info(f"Sync completed: {result.returncode}")
                if result.stderr:
                    logger.error(f"Sync errors: {result.stderr}")
            except Exception as e:
                logger.error(f"Sync failed: {e}")
        
        background_tasks.add_task(run_sync)
        
        return {"success": True, "message": "Sync started in background"}
    except Exception as e:
        logger.error(f"Failed to start sync: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/drive/status")
async def get_drive_status():
    """Check Google Drive connection status."""
    try:
        from pathlib import Path
        
        # Check if credentials exist
        has_oauth = Path("drive_oauth_token.json").exists()
        has_service_account = Path("service_account.json").exists()
        
        return {
            "success": True,
            "connected": has_oauth or has_service_account,
            "auth_type": "oauth" if has_oauth else ("service_account" if has_service_account else "none"),
            "oauth_configured": has_oauth,
            "service_account_configured": has_service_account
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== Run Server =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
