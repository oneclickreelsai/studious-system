import os
import logging
import time
from backend.core.video_engine.meta_ai_generator import BROWSER_PROFILE_DIR, PLAYWRIGHT_AVAILABLE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaPoster:
    """
    Automates uploading videos to Instagram and Facebook Reels via Meta Business Suite.
    Uses Playwright to bypass API limitations for local file uploads.
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        
    async def start(self):
        """Start browser with persistent profile."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        # Reuse the same profile as Meta AI to share login session
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        
        # Meta Business Suite URL
        self.base_url = "https://business.facebook.com/latest/composer"
        
        logger.info(f"Launching browser with profile: {BROWSER_PROFILE_DIR}")
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=BROWSER_PROFILE_DIR,
            headless=self.headless,
            viewport={'width': 1280, 'height': 800},
            args=["--disable-blink-features=AutomationControlled"], # Avoid bot detection
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()

    async def stop(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def upload_reel(self, video_path: str, caption: str, share_to_feed: bool = True) -> dict:
        """
        Uploads a video to Instagram Reels via Meta Business Suite.
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
                
            await self.start()
            
            # 1. Go to Composer
            logger.info("Navigating to Meta Business Suite Composer...")
            await self.page.goto(self.base_url, wait_until="networkidle")
            
            # Check login
            if "login" in self.page.url:
                logger.error("Not logged in. Please login to Facebook in the browser window.")
                # We could try to reuse auto_login logic here, but for now assuming shared session
                # If headless, this will fail. If visible, user can login.
                if self.headless:
                    raise Exception("Not logged in to Facebook. Please run in headful mode first to login.")
            
            # 2. Select "Reel" (if not default)
            # This selector is tricky and changes often. We'll try text matching.
            await self.page.wait_for_timeout(3000)
            
            # Click "Create Reel" button if we are on Home instead of Composer
            create_button = await self.page.query_selector('text="Create Reel"')
            if create_button:
                await create_button.click()
                await self.page.wait_for_timeout(2000)
            
            # 3. Upload Video
            # Look for file input
            logger.info("Uploading video...")
            
            # "Add video" button often triggers a hidden file input
            # We can force show input or try to attach to the first file input found
            async with self.page.expect_file_chooser() as fc_info:
                # Find the upload click target. Common labels: "Add video", "Upload video"
                upload_btn = await self.page.query_selector('text="Add video"')
                if not upload_btn: 
                    # Try simplified "Upload" button
                    upload_btn = await self.page.query_selector('div[role="button"]:has-text("Upload")')
                
                if upload_btn:
                    await upload_btn.click()
                else:
                    # Fallback: Just look for any file input
                    await self.page.set_input_files('input[type="file"]', video_path)
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(video_path)
            
            logger.info("Video file attached. Waiting for upload...")
            # Wait for upload progress (generic wait for now)
            await self.page.wait_for_timeout(10000) 
            
            # 4. Enter Caption
            logger.info("Entering caption...")
            # Textarea for caption. Usually has aria-label="Write a caption" or similar
            caption_box = await self.page.query_selector('div[role="textbox"][contenteditable="true"]')
            if caption_box:
                await caption_box.click()
                await caption_box.fill(caption)
            
            # 5. Click Next / Share
            # This flow involves typically 2-3 "Next" clicks
            logger.info("Navigating through wizard...")
            
            # Function to click "Next"
            async def click_next():
                next_btn = await self.page.query_selector('div[role="button"]:has-text("Next")')
                if next_btn:
                    await next_btn.click()
                    return True
                return False
                
            # Try clicking Next a few times
            for _ in range(3):
                if await click_next():
                    await self.page.wait_for_timeout(2000)
            
            # 6. Click Share/Publish
            share_btn = await self.page.query_selector('div[role="button"]:has-text("Share")')
            if not share_btn:
                share_btn = await self.page.query_selector('div[role="button"]:has-text("Publish")')
                
            if share_btn:
                logger.info("Clicking Share/Publish...")
                await share_btn.click()
                # Wait for confirmation
                await self.page.wait_for_timeout(5000)
                
                return {"success": True, "message": "Upload started via browser automation."}
            else:
                raise Exception("Could not find Share/Publish button")

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            # Take screenshot on failure
            if self.page:
                try:
                    await self.page.screenshot(path="upload_error.png")
                except:
                    pass
            return {"success": False, "error": str(e)}
            
        finally:
            await self.stop()

# Wrapper for testing
if __name__ == "__main__":
    import asyncio
    poster = SocialMediaPoster(headless=False)
    # Using a dummy or existing video path for testing if run directly
    dummy_video = "output/reel.mp4" 
    if os.path.exists(dummy_video):
        asyncio.run(poster.upload_reel(dummy_video, "Test Caption #AI"))
    else:
        print(f"Test video not found at {dummy_video}")
