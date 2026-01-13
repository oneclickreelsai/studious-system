import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from backend.utils.error_handler import retry_with_backoff, handle_api_error, RetryableError, ErrorType
from backend.utils.rate_limiter import rate_limit
from backend.config.security import sanitize_text_input

import time
import random

logger = logging.getLogger(__name__)

def sanitize_text(text, max_length=5000):
    """Sanitize text for YouTube API"""
    return sanitize_text_input(text, max_length)

@retry_with_backoff(max_retries=3)
@handle_api_error
@rate_limit("youtube_upload")
def upload_youtube_short(video_path, title, description, privacy_status="public"):
    """
    Uploads a short video to YouTube.
    
    Args:
        video_path (str): Path to the video file.
        title (str): Video title.
        description (str): Video description.
        privacy_status (str): "private", "unlisted", or "public". Defaults to "public" for monetization.
    """
    logger.info(f"Starting YouTube upload: {title.encode('ascii', 'ignore').decode()}")
    
    # SAFETY: Add a small random delay to prevent rapid-fire API calls (rate limit protection)
    time.sleep(random.uniform(1.0, 3.0))

    try:
        creds = Credentials(
            None,
            refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        )

        youtube = build("youtube", "v3", credentials=creds)

        # Sanitize title and description
        clean_title = sanitize_text(title, max_length=100)
        clean_description = sanitize_text(description, max_length=5000)

        logger.info(f"Uploading video as {privacy_status}...")

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": clean_title if clean_title else "Short Video",
                    "description": clean_description,
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )

        response = request.execute()
        video_id = response["id"]
        logger.info(f"[OK] YouTube upload successful! Video ID: {video_id}")
        return video_id
        
    except Exception as e:
        logger.error(f"YouTube upload error: {e}")
        if "quota" in str(e).lower():
            raise RetryableError(f"YouTube quota exceeded: {e}", ErrorType.API_ERROR, retry_after=3600)
        elif "authentication" in str(e).lower():
            raise RetryableError(f"YouTube auth error: {e}", ErrorType.API_ERROR, retry_after=300)
        else:
            raise RetryableError(f"YouTube upload error: {e}", ErrorType.API_ERROR)
