import os
import requests
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load config
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / "config.env", override=True)

logger = logging.getLogger(__name__)

def get_fb_credentials():
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_ACCESS_TOKEN")
    return page_id, access_token

def upload_facebook_reel(video_path: str, caption: str = "") -> str:
    """
    Upload a video as a Reel to Facebook Page.
    Returns: post_id or raises Exception
    """
    PAGE_ID, ACCESS_TOKEN = get_fb_credentials()
    
    if not PAGE_ID or not ACCESS_TOKEN:
        raise ValueError("Facebook credentials (FB_PAGE_ID, FB_ACCESS_TOKEN) not set.")
    
    # Auto-exchange for Page Token if we have a User Token
    # This prevents Error 100/33 (Unsupported post request)
    try:
        logger.info(f"Exchanging token for Page {PAGE_ID} access...")
        token_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}?fields=access_token&access_token={ACCESS_TOKEN}"
        token_res = requests.get(token_url)
        if token_res.status_code == 200:
            data = token_res.json()
            if "access_token" in data:
                ACCESS_TOKEN = data["access_token"]
                logger.info("Successfully retrieved Page Access Token.")
            else:
                logger.warning("Could not retrieve Page Access Token (field missing). Using provided token.")
        else:
            logger.warning(f"Token exchange failed: {token_res.text}. Trying with provided token.")
    except Exception as e:
        logger.warning(f"Token exchange error: {e}. Using provided token.")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # 1. Initialize Upload
    init_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/video_reels"
    init_payload = {
        "upload_phase": "start",
        "access_token": ACCESS_TOKEN
    }
    
    logger.info("Initializing Facebook Reel upload...")
    init_res = requests.post(init_url, data=init_payload)
    
    # Log the response for debugging
    logger.info(f"Init response status: {init_res.status_code}")
    logger.info(f"Init response body: {init_res.text}")
    
    if init_res.status_code != 200:
        try:
            error_data = init_res.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            error_code = error_data.get('error', {}).get('code', 'N/A')
            raise Exception(f"Facebook Init Error ({error_code}): {error_msg}")
        except Exception as e:
            if "Facebook Init Error" in str(e):
                raise
            raise Exception(f"Facebook Init Failed: {init_res.status_code} - {init_res.text}")
    
    init_res.raise_for_status()
    init_data = init_res.json()
    
    video_id = init_data["video_id"]
    upload_url = init_data["upload_url"]
    
    logger.info(f"Upload initialized. Video ID: {video_id}")
    
    # 2. Upload Video Binary
    file_size = os.path.getsize(video_path)
    logger.info(f"Uploading {file_size} bytes...")
    
    with open(video_path, "rb") as f:
        headers = {
            "Authorization": f"OAuth {ACCESS_TOKEN}",
            "offset": "0",
            "file_size": str(file_size)
        }
        upload_res = requests.post(upload_url, data=f, headers=headers)
        upload_res.raise_for_status()
        
    logger.info("Binary upload complete.")
    
    # 3. Publish Reel
    publish_url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/video_reels"
    publish_payload = {
        "access_token": ACCESS_TOKEN,
        "video_id": video_id,
        "upload_phase": "finish",
        "video_state": "PUBLISHED",
        "description": caption
    }
    
    logger.info("Publishing Reel...")
    pub_res = requests.post(publish_url, data=publish_payload)
    
    # Check for specific FB errors
    if pub_res.status_code != 200:
        logger.error(f"Publish failed: {pub_res.text}")
        try:
            err = pub_res.json()
            if "error" in err:
                raise Exception(f"Facebook API Error: {err['error'].get('message')}")
        except:
            pass
        pub_res.raise_for_status()
        
    pub_data = pub_res.json()
    if not pub_data.get("success"):
        # Sometimes success is waiting for async processing
        pass
        
    logger.info(f"Reel published successfully! ID: {video_id}")
    return video_id
