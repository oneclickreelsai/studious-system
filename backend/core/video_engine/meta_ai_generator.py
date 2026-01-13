"""
Meta AI Video Generator - Fully Automated
Generates videos on Meta AI using browser automation.

Flow:
1. Login to Meta AI (uses saved browser session or auto-login)
2. Enter prompt
3. Wait for video generation
4. Extract post URL
5. Download video
"""
import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
load_dotenv("config.env")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Facebook credentials for auto-login
FB_EMAIL = os.getenv("FACEBOOK_LOGIN_USER_ID")
FB_PASSWORD = os.getenv("FACEBOOK_LOGIN_PASSWORD")

# Playwright
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")

# Browser profile path for persistent login
BROWSER_PROFILE_DIR = "profile/meta_ai_browser"
META_AI_URL = "https://www.meta.ai/"
META_AI_PROFILE = "oneclickreelsai"  # Your Meta AI username

class MetaAIGenerator:
    """Automated Meta AI video generator."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    async def start(self):
        """Start browser with persistent profile."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")
        
        os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        # Use persistent context to keep login session
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=BROWSER_PROFILE_DIR,
            headless=self.headless,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        logger.info("[OK] Browser started with persistent profile")
    
    async def stop(self):
        """Close browser."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("[OK] Browser closed")
    
    async def is_logged_in(self) -> bool:
        """Check if already logged into Meta AI."""
        try:
            await self.page.goto(META_AI_URL, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Check for login indicators
            page_content = await self.page.content()
            
            # If we see "Log in" button prominently, we're not logged in
            login_btn = await self.page.query_selector('[data-testid="login-button"], button:has-text("Log in with Facebook")')
            
            # If we see the prompt input area, we're logged in
            prompt_input = await self.page.query_selector('textarea, [role="textbox"], [contenteditable="true"]')
            
            # Check for user avatar or profile indicator
            avatar = await self.page.query_selector('[aria-label*="profile"], [aria-label*="account"], img[alt*="profile"]')
            
            if prompt_input or avatar:
                logger.info("[OK] Already logged in to Meta AI")
                return True
            elif login_btn:
                logger.info("[!] Not logged in - login button found")
                return False
            else:
                # Assume logged in if no clear login button
                logger.info("[OK] Assuming logged in (no login button found)")
                return True
                
        except Exception as e:
            logger.warning(f"Login check error: {e}, assuming logged in")
            return True
    
    async def auto_login(self) -> bool:
        """Automatically login to Meta AI using Facebook credentials."""
        if not FB_EMAIL or not FB_PASSWORD:
            logger.warning("[!] No Facebook credentials in config.env")
            return False
        
        try:
            logger.info("[*] Attempting auto-login with Facebook...")
            
            # Go to Meta AI
            await self.page.goto(META_AI_URL, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            # Look for login button
            login_btn = await self.page.query_selector('button:has-text("Log in"), a:has-text("Log in"), [data-testid="login-button"]')
            
            if login_btn:
                await login_btn.click()
                await self.page.wait_for_timeout(2000)
            
            # Check if we're on Facebook login page
            if 'facebook.com' in self.page.url:
                logger.info("[*] On Facebook login page...")
                
                # Find email input
                email_input = await self.page.query_selector('input[name="email"], input[id="email"], #email')
                if email_input:
                    await email_input.fill(FB_EMAIL)
                    logger.info("[OK] Entered email")
                
                # Find password input
                pass_input = await self.page.query_selector('input[name="pass"], input[id="pass"], #pass')
                if pass_input:
                    await pass_input.fill(FB_PASSWORD)
                    logger.info("[OK] Entered password")
                
                # Click login button
                await self.page.wait_for_timeout(500)
                submit_btn = await self.page.query_selector('button[name="login"], button[type="submit"], #loginbutton')
                if submit_btn:
                    await submit_btn.click()
                    logger.info("[OK] Clicked login button")
                
                # Wait for redirect back to Meta AI
                await self.page.wait_for_timeout(5000)
                
                # Check if login successful
                if 'meta.ai' in self.page.url:
                    # Check for prompt input
                    prompt_input = await self.page.query_selector('[role="textbox"], textarea')
                    if prompt_input:
                        logger.info("[OK] Auto-login successful!")
                        return True
                
                # May need to handle 2FA or other prompts
                logger.warning("[!] Login may require additional verification")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"[X] Auto-login error: {e}")
            return False
    
    async def wait_for_login(self, timeout: int = 120):
        """Wait for user to manually login."""
        logger.info("[*] Please login to Meta AI in the browser window...")
        logger.info(f"[*] Waiting up to {timeout} seconds...")
        
        start = datetime.now()
        while (datetime.now() - start).seconds < timeout:
            # Check for prompt input (indicates logged in)
            prompt_input = await self.page.query_selector('textarea, [contenteditable="true"]')
            if prompt_input:
                logger.info("[OK] Login detected!")
                return True
            await self.page.wait_for_timeout(2000)
        
        logger.error("[X] Login timeout")
        return False
    
    async def generate_video(self, prompt: str, wait_time: int = 180, add_music: bool = True) -> Optional[str]:
        """
        Generate video on Meta AI and return the video URL or download it directly.
        
        Args:
            prompt: The prompt for video generation
            wait_time: Max seconds to wait for generation
            add_music: Whether to add music using Meta AI's built-in feature
        
        Returns:
            Post URL or direct video URL if successful, None otherwise
        """
        try:
            # Go to Meta AI main page
            await self.page.goto(META_AI_URL, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Find prompt input
            prompt_input = await self.page.query_selector('[role="textbox"]')
            if not prompt_input:
                prompt_input = await self.page.query_selector('[contenteditable="true"]')
            if not prompt_input:
                prompt_input = await self.page.query_selector('textarea')
            
            if not prompt_input:
                logger.error("[X] Could not find prompt input")
                return None
            
            logger.info("[OK] Found input element")
            
            # Click and enter prompt
            await prompt_input.click()
            await self.page.wait_for_timeout(500)
            
            # Use "Create a video of..." format for video generation
            if not prompt.lower().startswith("create"):
                video_prompt = f"Create a video of {prompt}"
            else:
                video_prompt = prompt
            
            # Use keyboard.type for contenteditable divs
            await self.page.keyboard.type(video_prompt, delay=15)
            logger.info(f"[OK] Entered prompt: {video_prompt[:60]}...")
            
            await self.page.wait_for_timeout(1000)
            
            # Press Enter or click send button
            send_btn = await self.page.query_selector('[aria-label*="Send"], button[type="submit"]')
            if send_btn:
                await send_btn.click()
                logger.info("[OK] Clicked send button")
            else:
                await self.page.keyboard.press('Enter')
                logger.info("[OK] Pressed Enter to submit")
            
            # Wait for video generation
            logger.info(f"[*] Waiting for video generation (up to {wait_time}s)...")
            
            video_url = None
            create_page_url = None
            start = datetime.now()
            last_check = 0
            
            while (datetime.now() - start).seconds < wait_time:
                await self.page.wait_for_timeout(5000)
                elapsed = (datetime.now() - start).seconds
                
                try:
                    # Look for video element
                    video = await self.page.query_selector('video')
                    if video:
                        logger.info("[OK] Video element found!")
                        
                        # Wait for video to fully load
                        await self.page.wait_for_timeout(3000)
                        
                        # Check if we're on the create page (has Add music button)
                        current_url = self.page.url
                        if '/create/' in current_url:
                            create_page_url = current_url
                            logger.info(f"[OK] On create page: {current_url[:60]}...")
                        
                        # Get video source URL directly
                        video_urls = await self.page.evaluate('''() => {
                            const videos = document.querySelectorAll('video');
                            return Array.from(videos).map(v => v.src || v.currentSrc).filter(u => u && u.includes('.mp4'));
                        }''')
                        
                        if video_urls:
                            # Get the first (newest) video URL
                            video_url = video_urls[0]
                            logger.info(f"[OK] Got video URL: {video_url[:80]}...")
                            break
                        
                except Exception as nav_error:
                    logger.info(f"[*] Page navigating... ({elapsed}s)")
                    await self.page.wait_for_timeout(3000)
                    continue
                
                # Progress update
                if elapsed - last_check >= 15:
                    logger.info(f"[*] Still generating... ({elapsed}s)")
                    last_check = elapsed
            
            # Try to add music if on create page
            if video_url and add_music:
                logger.info("[*] Attempting to add music...")
                music_added = await self.add_music_to_video()
                if music_added:
                    # Get updated video URL with music
                    await self.page.wait_for_timeout(3000)
                    new_urls = await self.page.evaluate('''() => {
                        const videos = document.querySelectorAll('video');
                        return Array.from(videos).map(v => v.src || v.currentSrc).filter(u => u && u.includes('.mp4'));
                    }''')
                    if new_urls:
                        video_url = new_urls[0]
                        logger.info(f"[OK] Updated video URL with music")
            
            return video_url
            
        except Exception as e:
            logger.error(f"[X] Generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_and_select_best_video(self) -> bool:
        """
        Analyze all 4 generated video options and select the best one.
        Criteria: resolution, visual quality, composition
        
        Returns:
            True if successfully selected best video
        """
        try:
            logger.info("[*] Analyzing all 4 video options to select the best...")
            
            # Wait for all videos to load
            await self.page.wait_for_timeout(3000)
            
            # Get info about all video options
            video_info = await self.page.evaluate('''() => {
                const videos = document.querySelectorAll('video');
                const results = [];
                
                for (let i = 0; i < videos.length && i < 4; i++) {
                    const video = videos[i];
                    const rect = video.getBoundingClientRect();
                    
                    // Get video properties
                    const info = {
                        index: i,
                        width: video.videoWidth || rect.width,
                        height: video.videoHeight || rect.height,
                        duration: video.duration || 0,
                        src: (video.src || video.currentSrc || '').substring(0, 80),
                        visible: rect.width > 0 && rect.height > 0,
                        position: {
                            x: rect.left,
                            y: rect.top
                        }
                    };
                    
                    // Calculate quality score
                    info.resolution = info.width * info.height;
                    info.aspectRatio = info.height / info.width;
                    
                    results.push(info);
                }
                
                return results;
            }''')
            
            if not video_info or len(video_info) == 0:
                logger.warning("[!] No videos found to analyze")
                return False
            
            logger.info(f"[*] Found {len(video_info)} video options")
            
            # Score each video
            for i, info in enumerate(video_info):
                score = 0
                
                # Higher resolution = better (max 50 points)
                if info['resolution'] > 0:
                    score += min(50, info['resolution'] / 10000)
                
                # Prefer vertical videos (9:16 aspect ratio ~1.78) (max 30 points)
                if info['aspectRatio'] > 1.5:  # Vertical
                    score += 30
                elif info['aspectRatio'] > 1.0:  # Portrait-ish
                    score += 20
                else:  # Horizontal
                    score += 10
                
                # Visible videos get bonus (20 points)
                if info['visible']:
                    score += 20
                
                info['score'] = score
                logger.info(f"   Video {i+1}: {info['width']}x{info['height']}, "
                           f"aspect={info['aspectRatio']:.2f}, score={score:.1f}")
            
            # Select best video (highest score)
            best_video = max(video_info, key=lambda x: x['score'])
            best_index = best_video['index']
            
            logger.info(f"[OK] Best video: #{best_index + 1} "
                       f"({best_video['width']}x{best_video['height']}, "
                       f"score={best_video['score']:.1f})")
            
            # Click on the best video
            click_result = await self.page.evaluate(f'''() => {{
                const videos = document.querySelectorAll('video');
                if (videos.length > {best_index}) {{
                    const video = videos[{best_index}];
                    
                    // Find clickable parent
                    let el = video;
                    while (el && el.parentElement) {{
                        el = el.parentElement;
                        if (el.onclick || el.getAttribute('role') === 'button' || 
                            el.style.cursor === 'pointer' || el.hasAttribute('tabindex')) {{
                            el.click();
                            return 'clicked best video #{best_index + 1}';
                        }}
                    }}
                    
                    // Fallback: click parent
                    video.parentElement.click();
                    return 'clicked parent of best video';
                }}
                return 'video not found';
            }}''')
            
            logger.info(f"[OK] {click_result}")
            
            # Wait for navigation
            await self.page.wait_for_timeout(3000)
            
            return True
            
        except Exception as e:
            logger.error(f"[X] Video analysis error: {e}")
            return False
    
    async def get_video_duration(self) -> float:
        """Get current video duration from the page."""
        try:
            # Look for duration indicator (e.g., "5s" or "0:05")
            duration_text = await self.page.evaluate('''() => {
                // Try to find duration from video element
                const video = document.querySelector('video');
                if (video && video.duration) return video.duration;
                
                // Try to find duration text in UI
                const texts = document.body.innerText;
                const match = texts.match(/(\\d+)s\\b/);
                if (match) return parseInt(match[1]);
                
                return 0;
            }''')
            return float(duration_text) if duration_text else 0
        except:
            return 0
    
    async def extend_video(self, target_duration: int = 15) -> bool:
        """
        Extend video using Meta AI's 'Extend' feature.
        Clicks the Extend button and waits for extension to COMPLETE (2-3 minutes).
        
        Args:
            target_duration: Target duration in seconds (default 15)
        
        Returns:
            True if video was extended successfully
        """
        try:
            logger.info(f"[*] Extending video (this takes 140-150 seconds)...")
            
            # Get initial state - count video elements and check URL
            initial_state = await self.page.evaluate('''() => {
                const videos = document.querySelectorAll('video');
                const duration = videos.length > 0 && videos[0].duration ? videos[0].duration : 0;
                const src = videos.length > 0 ? (videos[0].src || videos[0].currentSrc) : '';
                return { count: videos.length, duration, src: src.substring(0, 80) };
            }''')
            logger.info(f"[*] Initial state: {initial_state['count']} videos, {initial_state['duration']}s")
            
            # Find and click "Extend animation" section first to expand it
            await self.page.evaluate('''() => {
                const elements = document.querySelectorAll('div, span');
                for (const el of elements) {
                    if (el.textContent.includes('Extend animation') && el.offsetParent !== null) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }''')
            await self.page.wait_for_timeout(1500)
            
            # Click the Extend button
            extend_clicked = await self.page.evaluate('''() => {
                const elements = document.querySelectorAll('div, span, button');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    const rect = el.getBoundingClientRect();
                    // Extend button is small, not the whole section
                    if (text === 'Extend' && rect.width < 150 && rect.height < 60 && el.offsetParent !== null) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }''')
            
            if not extend_clicked:
                logger.warning("[!] Could not find Extend button")
                return False
            
            logger.info("[OK] Clicked Extend button")
            logger.info("[*] Waiting for extension to complete (140-150 seconds)...")
            
            # WAIT for extension - check for video URL change (new video = extended)
            extension_complete = False
            for wait_count in range(12):  # Max 3 minutes (12 x 15 seconds)
                await self.page.wait_for_timeout(15000)  # Wait 15 seconds
                elapsed = (wait_count + 1) * 15
                
                # Check if video source changed (new video URL = extension complete)
                current_state = await self.page.evaluate('''() => {
                    const videos = document.querySelectorAll('video');
                    const duration = videos.length > 0 && videos[0].duration ? videos[0].duration : 0;
                    const src = videos.length > 0 ? (videos[0].src || videos[0].currentSrc) : '';
                    
                    // Check for loading indicators
                    const loaders = document.querySelectorAll('[role="progressbar"], .loading, [aria-busy="true"]');
                    const isLoading = loaders.length > 0;
                    
                    return { 
                        count: videos.length, 
                        duration, 
                        src: src.substring(0, 80),
                        isLoading 
                    };
                }''')
                
                logger.info(f"[*] Checking... ({elapsed}s) - Duration: {current_state['duration']}s, Loading: {current_state['isLoading']}")
                
                # Extension complete when:
                # 1. Video URL changed (different src)
                # 2. OR duration increased significantly
                # 3. AND not loading anymore
                if current_state['src'] != initial_state['src'] and current_state['src']:
                    logger.info(f"[OK] Extension complete! New video detected")
                    extension_complete = True
                    break
                elif current_state['duration'] > initial_state['duration'] + 2 and not current_state['isLoading']:
                    logger.info(f"[OK] Extension complete! Duration: {initial_state['duration']}s -> {current_state['duration']}s")
                    extension_complete = True
                    break
                
                # After 150 seconds, check if there's a new video in sidebar
                if elapsed >= 150:
                    # Click on first thumbnail to see if it's the extended version
                    await self.page.evaluate('''() => {
                        const imgs = document.querySelectorAll('img');
                        const thumbs = Array.from(imgs).filter(img => {
                            const rect = img.getBoundingClientRect();
                            return rect.width > 30 && rect.width < 150 && rect.height > 30 && rect.left < 100;
                        });
                        if (thumbs.length > 0) thumbs[0].click();
                    }''')
                    await self.page.wait_for_timeout(3000)
                    
                    new_duration = await self.get_video_duration()
                    if new_duration > initial_duration + 2:
                        logger.info(f"[OK] Found extended video! Duration: {new_duration}s")
                        extension_complete = True
                        break
            
            if not extension_complete:
                logger.warning("[!] Extension may not have completed, continuing anyway...")
            
            # Wait a bit more for video to fully load
            await self.page.wait_for_timeout(3000)
            
            # Click on the TOP thumbnail to select the extended version
            await self.page.evaluate('''() => {
                const imgs = document.querySelectorAll('img');
                const thumbs = Array.from(imgs).filter(img => {
                    const rect = img.getBoundingClientRect();
                    return rect.width > 30 && rect.width < 150 && rect.height > 30 && rect.left < 100;
                });
                if (thumbs.length > 0) {
                    thumbs[0].click();
                }
            }''')
            logger.info("[OK] Selected extended video from sidebar")
            
            # Wait for video to load
            await self.page.wait_for_timeout(3000)
            
            return extension_complete
            
        except Exception as e:
            logger.error(f"[X] Extend video error: {e}")
            return False
    
    async def add_music_to_video(self) -> bool:
        """
        Add music to video using Meta AI's built-in music library.
        Opens the music modal, selects Trending tab, picks a song, and WAITS for it to apply.
        
        Returns:
            True if music was added successfully
        """
        try:
            logger.info("[*] Adding music to video (this takes 1-2 minutes)...")
            
            # Get initial thumbnail count
            initial_thumbs = await self.page.evaluate('''() => {
                const imgs = document.querySelectorAll('img');
                return Array.from(imgs).filter(img => {
                    const rect = img.getBoundingClientRect();
                    return rect.width > 30 && rect.width < 150 && rect.height > 30 && rect.left < 100;
                }).length;
            }''')
            logger.info(f"[*] Initial thumbnails: {initial_thumbs}")
            
            # Step 1: Look for "Add audio" or "Add or change audio" section and click it
            add_audio_clicked = await self.page.evaluate('''() => {
                // Look for the Add audio section header
                const allElements = document.querySelectorAll('div, span, h3, h4');
                for (const el of allElements) {
                    const text = el.textContent.trim();
                    if ((text === 'Add audio' || text === 'Add or change audio' || 
                         text.includes('Add audio')) && 
                        el.offsetParent !== null && 
                        el.getBoundingClientRect().width > 50) {
                        el.click();
                        return text;
                    }
                }
                return null;
            }''')
            
            if add_audio_clicked:
                logger.info(f"[OK] Clicked '{add_audio_clicked}' section")
            else:
                logger.info("[*] No 'Add audio' section found, looking for music button directly...")
            
            await self.page.wait_for_timeout(2000)
            
            # Step 2: Click "Add music" or "Browse" button to open the modal
            # Try multiple approaches to find and click the button
            music_btn_clicked = await self.page.evaluate('''() => {
                // Method 1: Look for button with exact text
                const buttons = document.querySelectorAll('button, div[role="button"], span[role="button"]');
                for (const btn of buttons) {
                    const text = btn.textContent.trim();
                    if ((text === 'Add music' || text === 'Browse' || text === 'Add Music') && 
                        btn.offsetParent !== null) {
                        btn.click();
                        return 'button: ' + text;
                    }
                }
                
                // Method 2: Look for any clickable element with music-related text
                const allElements = document.querySelectorAll('div, span');
                for (const el of allElements) {
                    const text = el.textContent.trim();
                    const rect = el.getBoundingClientRect();
                    if ((text === 'Add music' || text === 'Browse') && 
                        rect.width > 30 && rect.width < 200 &&
                        rect.height > 20 && rect.height < 60 &&
                        el.offsetParent !== null) {
                        el.click();
                        return 'element: ' + text;
                    }
                }
                
                // Method 3: Look for music icon button (usually has aria-label)
                const iconBtns = document.querySelectorAll('[aria-label*="music"], [aria-label*="audio"], [aria-label*="Music"]');
                for (const btn of iconBtns) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return 'icon: ' + btn.getAttribute('aria-label');
                    }
                }
                
                return null;
            }''')
            
            if music_btn_clicked:
                logger.info(f"[OK] Clicked music button: {music_btn_clicked}")
            else:
                logger.warning("[!] Could not find Add music button")
                return False
            
            # Step 3: Wait for music modal/panel to appear
            logger.info("[*] Waiting for music panel to open...")
            await self.page.wait_for_timeout(3000)
            
            # Check if modal opened by looking for Trending/Suggested tabs or song list
            modal_opened = await self.page.evaluate('''() => {
                const texts = ['Trending', 'Suggested', 'Saved', 'Search songs'];
                for (const text of texts) {
                    const el = document.evaluate(
                        `//*[contains(text(), '${text}')]`,
                        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
                    ).singleNodeValue;
                    if (el && el.offsetParent !== null) return text;
                }
                // Also check for song list items
                const songItems = document.querySelectorAll('[role="listitem"], [role="option"]');
                if (songItems.length > 0) return 'song list found';
                return null;
            }''')
            
            if modal_opened:
                logger.info(f"[OK] Music panel opened: found '{modal_opened}'")
            else:
                logger.warning("[!] Music panel may not have opened, trying to continue...")
                # Try clicking the button again
                await self.page.evaluate('''() => {
                    const elements = document.querySelectorAll('div, span, button');
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        if ((text === 'Add music' || text === 'Browse') && el.offsetParent !== null) {
                            el.click();
                            return;
                        }
                    }
                }''')
                await self.page.wait_for_timeout(3000)
            
            # Step 4: Click "Trending" tab for popular music
            trending_clicked = await self.page.evaluate('''() => {
                const elements = document.querySelectorAll('div, span, button, [role="tab"]');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text === 'Trending' && el.offsetParent !== null) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }''')
            
            if trending_clicked:
                logger.info("[OK] Clicked 'Trending' tab")
            else:
                logger.info("[*] No Trending tab found, using default list")
            
            await self.page.wait_for_timeout(2000)
            
            # Step 5: Select first song from the list - try multiple methods
            song_selected = await self.page.evaluate('''() => {
                // Method 1: Look for role="listitem" or role="option" (common for song lists)
                const listItems = document.querySelectorAll('[role="listitem"], [role="option"], [role="row"]');
                for (const item of listItems) {
                    const rect = item.getBoundingClientRect();
                    // Song items typically have reasonable size
                    if (rect.height > 40 && rect.height < 120 && rect.width > 150) {
                        const hasImg = item.querySelector('img');
                        const text = item.textContent.trim();
                        // Skip if it's a tab or header
                        if (text.includes('Trending') && text.length < 15) continue;
                        if (text.includes('Suggested') && text.length < 15) continue;
                        if (hasImg || text.length > 10) {
                            item.click();
                            return 'listitem: ' + text.substring(0, 40);
                        }
                    }
                }
                
                // Method 2: Look for divs that look like song rows (have album art + text)
                const allDivs = document.querySelectorAll('div');
                for (const div of allDivs) {
                    const rect = div.getBoundingClientRect();
                    // Song rows are typically 50-100px height
                    if (rect.height > 45 && rect.height < 110 && rect.width > 180 && rect.width < 500) {
                        const img = div.querySelector('img');
                        const text = div.textContent.trim();
                        
                        // Must have album art image
                        if (img && text.length > 5 && text.length < 150) {
                            // Skip navigation tabs
                            if (text === 'Trending' || text === 'Suggested' || 
                                text === 'Saved' || text.includes('Search')) continue;
                            
                            div.click();
                            return 'div: ' + text.substring(0, 40);
                        }
                    }
                }
                
                // Method 3: Find any clickable element with an image inside (album art)
                const clickables = document.querySelectorAll('div[tabindex], button, [role="button"]');
                for (const el of clickables) {
                    const rect = el.getBoundingClientRect();
                    if (rect.height > 40 && rect.height < 120 && rect.width > 100) {
                        const img = el.querySelector('img');
                        if (img && el.textContent.length > 3) {
                            el.click();
                            return 'clickable: ' + el.textContent.substring(0, 40);
                        }
                    }
                }
                
                return null;
            }''')
            
            if song_selected:
                logger.info(f"[OK] Selected song: {song_selected}")
            else:
                logger.warning("[!] Could not select a song automatically")
                # Take a screenshot for debugging
                try:
                    await self.page.screenshot(path="debug_music_modal.png")
                    logger.info("[*] Saved debug screenshot: debug_music_modal.png")
                except:
                    pass
                
                # Try one more fallback - just click in the area where songs should be
                await self.page.evaluate('''() => {
                    // Click in the center-right area where song list typically appears
                    const centerX = window.innerWidth * 0.6;
                    const centerY = window.innerHeight * 0.4;
                    const el = document.elementFromPoint(centerX, centerY);
                    if (el) el.click();
                }''')
                logger.info("[*] Attempted click in song list area")
            
            # Step 6: WAIT for music to be applied (new thumbnail should appear)
            logger.info("[*] Waiting for music to be applied (1-2 minutes)...")
            
            music_applied = False
            for wait_count in range(18):  # Max 3 minutes (18 x 10 seconds)
                await self.page.wait_for_timeout(10000)  # Wait 10 seconds
                elapsed = (wait_count + 1) * 10
                
                # Check if new thumbnail appeared
                current_thumbs = await self.page.evaluate('''() => {
                    const imgs = document.querySelectorAll('img');
                    return Array.from(imgs).filter(img => {
                        const rect = img.getBoundingClientRect();
                        return rect.width > 30 && rect.width < 150 && rect.height > 30 && rect.left < 100;
                    }).length;
                }''')
                
                logger.info(f"[*] Checking... ({elapsed}s) - Thumbnails: {current_thumbs}")
                
                if current_thumbs > initial_thumbs:
                    logger.info(f"[OK] Music applied! New thumbnail appeared ({current_thumbs} total)")
                    music_applied = True
                    break
                
                # After 30 seconds, if no change, music probably wasn't selected
                if elapsed >= 30 and not song_selected:
                    logger.warning("[!] No song was selected, skipping music")
                    await self.page.keyboard.press('Escape')
                    return False
            
            if not music_applied:
                logger.warning("[!] Music application timed out")
                # Close modal and continue
                await self.page.keyboard.press('Escape')
                return False
            
            # Wait for video to fully update
            await self.page.wait_for_timeout(3000)
            
            # Select the TOP thumbnail (latest version with music)
            await self.page.evaluate('''() => {
                const imgs = document.querySelectorAll('img');
                const thumbs = Array.from(imgs).filter(img => {
                    const rect = img.getBoundingClientRect();
                    return rect.width > 30 && rect.width < 150 && rect.height > 30 && rect.left < 100;
                });
                if (thumbs.length > 0) {
                    thumbs[0].click();
                }
            }''')
            logger.info("[OK] Selected video with music from sidebar")
            
            # Close any open modals
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(2000)
            
            return True
            
        except Exception as e:
            logger.error(f"[X] Add music error: {e}")
            return False
    
    async def download_video_direct(self, video_url: str, output_path: str) -> bool:
        """Download video directly from URL."""
        try:
            import httpx
            
            logger.info(f"[*] Downloading video from: {video_url[:60]}...")
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(video_url)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"[OK] Downloaded: {len(response.content) / 1024 / 1024:.2f} MB")
                    return True
                else:
                    logger.error(f"[X] Download failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"[X] Download error: {e}")
            return False
    
    async def download_via_button(self, output_path: str) -> bool:
        """Download video using the download button on the create page."""
        try:
            logger.info("[*] Looking for download button...")
            
            # Press Escape to close any overlays
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(500)
            
            # Set up download handler BEFORE clicking
            async with self.page.expect_download(timeout=30000) as download_info:
                # Use JS to click download button (bypasses overlay issues)
                clicked = await self.page.evaluate('''() => {
                    const btn = document.querySelector('[aria-label*="Download"], [aria-label*="download"]');
                    if (btn) { btn.click(); return true; }
                    return false;
                }''')
                
                if not clicked:
                    raise Exception("Download button not found")
                
                logger.info("[*] Clicked download, waiting...")
            
            download = await download_info.value
            await download.save_as(output_path)
            
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                logger.info(f"[OK] Downloaded: {size / 1024 / 1024:.2f} MB")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"[!] Download button failed: {e}")
            return False
    
    async def get_latest_post_url(self, username: str = None) -> Optional[str]:
        """Get the URL of the latest post (after generation)."""
        try:
            username = username or META_AI_PROFILE
            profile_url = f"https://www.meta.ai/@{username}"
            
            await self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Find the first post link
            post_links = await self.page.query_selector_all('a[href*="/post/"]')
            if post_links:
                href = await post_links[0].get_attribute('href')
                if href:
                    if href.startswith('/'):
                        href = f"https://www.meta.ai{href}"
                    # Clean up URL (remove query params)
                    if '?' in href:
                        href = href.split('?')[0]
                    logger.info(f"[OK] Found latest post: {href}")
                    return href
            
            logger.warning("[!] No posts found on profile")
            return None
        except Exception as e:
            logger.error(f"[X] Error getting post URL: {e}")
            return None
    
    async def navigate_to_create_page(self, create_url: str) -> bool:
        """
        Navigate to a Meta AI create page (for adding music to existing video).
        
        Args:
            create_url: URL like https://www.meta.ai/create/994679333719018/?prompt_id=994679373719014
        
        Returns:
            True if successfully navigated
        """
        try:
            logger.info(f"[*] Navigating to create page: {create_url[:60]}...")
            await self.page.goto(create_url, wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            # Check if video is present
            video = await self.page.query_selector('video')
            if video:
                logger.info("[OK] Video found on create page")
                return True
            else:
                logger.warning("[!] No video found on create page")
                return False
                
        except Exception as e:
            logger.error(f"[X] Navigation error: {e}")
            return False
    
    async def add_music_and_download(self, create_url: str, output_dir: str = None, 
                                      extend_to: int = 15) -> Optional[Dict]:
        """
        Navigate to create page, extend video, add music, and download.
        
        Args:
            create_url: Meta AI create page URL
            output_dir: Output directory for download
            extend_to: Target video duration in seconds (default 15)
        
        Returns:
            Download result dict or None
        """
        try:
            # Navigate to create page
            if not await self.navigate_to_create_page(create_url):
                return None
            
            # Step 1: Extend video to target duration
            if extend_to > 0:
                logger.info(f"[*] Step 1: Extending video to {extend_to}s...")
                extended = await self.extend_video(target_duration=extend_to)
                if extended:
                    logger.info("[OK] Video extended successfully")
                else:
                    logger.warning("[!] Could not extend video, continuing with current length")
            
            # Step 2: Add music
            logger.info("[*] Step 2: Adding music to video...")
            music_added = await self.add_music_to_video()
            
            if not music_added:
                logger.warning("[!] Could not add music, downloading without audio")
            
            # Wait for video to update with music
            await self.page.wait_for_timeout(3000)
            
            # Step 3: Download
            logger.info("[*] Step 3: Downloading video...")
            
            # Create output directory
            if not output_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"output/meta_ai_downloads/{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            video_path = os.path.join(output_dir, "video.mp4")
            
            # Try download via button first (gets video WITH music)
            downloaded = await self.download_via_button(video_path)
            
            if not downloaded:
                # Fallback: Get video URL and download directly
                video_urls = await self.page.evaluate('''() => {
                    const videos = document.querySelectorAll('video');
                    return Array.from(videos).map(v => v.src || v.currentSrc).filter(u => u && u.includes('.mp4'));
                }''')
                
                if not video_urls:
                    logger.error("[X] Could not get video URL")
                    return None
                
                video_url = video_urls[0]
                logger.info(f"[OK] Video URL: {video_url[:60]}...")
                
                if not await self.download_video_direct(video_url, video_path):
                    return None
            
            file_size = os.path.getsize(video_path)
            
            # Get final duration
            final_duration = await self.get_video_duration()
            
            return {
                "success": True,
                "source_url": create_url,
                "output_folder": output_dir,
                "file_path": video_path,
                "file_size": file_size,
                "duration": final_duration,
                "music_added": music_added,
                "message": f"Video downloaded ({final_duration}s)" + (" with music" if music_added else "")
            }
            
        except Exception as e:
            logger.error(f"[X] Add music and download error: {e}")
            import traceback
            traceback.print_exc()
            return None


async def generate_and_download(prompt: str, headless: bool = False, add_music: bool = True,
                                target_duration: int = 15) -> Optional[Dict]:
    """
    Full pipeline: Generate video on Meta AI, extend it, add music, and download.
    
    Args:
        prompt: Video generation prompt
        headless: Run browser in headless mode
        add_music: Whether to add music using Meta AI's built-in feature
        target_duration: Target video duration in seconds (default 15)
    
    Returns:
        Download result dict or None
    """
    import os
    from datetime import datetime
    
    generator = MetaAIGenerator(headless=headless)
    
    try:
        await generator.start()
        
        # Check login
        if not await generator.is_logged_in():
            logger.info("[!] Not logged in. Attempting auto-login...")
            
            # Try auto-login first
            if FB_EMAIL and FB_PASSWORD:
                if await generator.auto_login():
                    logger.info("[OK] Auto-login successful!")
                else:
                    logger.warning("[!] Auto-login failed, opening browser for manual login...")
                    await generator.stop()
                    
                    # Reopen in non-headless mode for manual login
                    generator = MetaAIGenerator(headless=False)
                    await generator.start()
                    
                    if not await generator.wait_for_login(timeout=120):
                        logger.error("[X] Login failed")
                        return None
            else:
                # No credentials, open browser for manual login
                logger.info("[!] No credentials found, opening browser for manual login...")
                await generator.stop()
                generator = MetaAIGenerator(headless=False)
                await generator.start()
                
                if not await generator.wait_for_login(timeout=120):
                    logger.error("[X] Login failed")
                    return None
        
        # Generate video
        logger.info(f"[*] Generating video with prompt: {prompt[:60]}...")
        video_url = await generator.generate_video(prompt, wait_time=180, add_music=False)  # Don't add music yet
        
        if not video_url:
            logger.error("[X] Could not get video URL")
            await generator.stop()
            return None
        
        logger.info(f"[OK] Video URL: {video_url[:80]}...")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/meta_ai_downloads/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        video_path = os.path.join(output_dir, "video.mp4")
        music_added = False
        video_extended = False
        final_duration = 5  # Default
        
        # Check if we're on a create page (can extend and add music)
        current_url = generator.page.url
        
        # If not on create page, we need to select one of the generated video options
        if '/create/' not in current_url:
            logger.info("[*] Analyzing and selecting best video from 4 options...")
            
            try:
                # Analyze all 4 videos and select the best one
                selected = await generator.analyze_and_select_best_video()
                
                if not selected:
                    # Fallback: just click first video
                    logger.warning("[!] Analysis failed, selecting first video...")
                    await generator.page.evaluate('''() => {
                        const videos = document.querySelectorAll('video');
                        if (videos.length > 0) {
                            videos[0].parentElement.click();
                        }
                    }''')
                
                # Wait for navigation to create page
                await generator.page.wait_for_timeout(3000)
                
                # Check if URL changed
                current_url = generator.page.url
                logger.info(f"[*] URL after click: {current_url[:70]}...")
                
                # Wait for create page URL
                if '/create/' not in current_url:
                    try:
                        await generator.page.wait_for_url('**/create/**', timeout=10000)
                        current_url = generator.page.url
                    except:
                        pass
                
                if '/create/' in current_url:
                    logger.info("[OK] Opened create page!")
                    # Wait for page to fully load
                    await generator.page.wait_for_timeout(3000)
                        
            except Exception as e:
                logger.warning(f"[!] Could not select video option: {e}")
        
        # If on create page, extend and add music
        if '/create/' in current_url:
            logger.info(f"[OK] On create page: {current_url[:60]}...")
            
            # Step 1: Extend video
            if target_duration > 5:
                logger.info(f"[*] Extending video to {target_duration}s...")
                video_extended = await generator.extend_video(target_duration=target_duration)
                if video_extended:
                    final_duration = await generator.get_video_duration()
                    logger.info(f"[OK] Video extended to {final_duration}s")
            
            # Step 2: Add music
            if add_music:
                logger.info("[*] Adding music...")
                music_added = await generator.add_music_to_video()
            
            # Step 3: Download via button
            await generator.page.wait_for_timeout(2000)
            downloaded = await generator.download_via_button(video_path)
            
            if downloaded:
                prompt_path = os.path.join(output_dir, "prompt.txt")
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                
                file_size = os.path.getsize(video_path)
                await generator.stop()
                
                return {
                    "success": True,
                    "source_url": current_url,
                    "output_folder": output_dir,
                    "prompt": prompt,
                    "prompt_file": prompt_path,
                    "type": "video",
                    "file_path": video_path,
                    "file_size": file_size,
                    "filename": "video.mp4",
                    "duration": final_duration,
                    "music_added": music_added,
                    "extended": video_extended,
                    "message": f"Video downloaded ({final_duration}s)" + (" with music" if music_added else "")
                }
        
        # Fallback: Download video directly (without extension/music from Meta AI)
        logger.info("[*] Downloading video directly (fallback)...")
        if await generator.download_video_direct(video_url, video_path):
            prompt_path = os.path.join(output_dir, "prompt.txt")
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            file_size = os.path.getsize(video_path)
            
            await generator.stop()
            
            return {
                "success": True,
                "source_url": video_url,
                "output_folder": output_dir,
                "prompt": prompt,
                "prompt_file": prompt_path,
                "type": "video",
                "file_path": video_path,
                "file_size": file_size,
                "filename": "video.mp4",
                "duration": 5,
                "music_added": False,
                "extended": False,
                "message": "Video downloaded (5s, no music - fallback)"
            }
        else:
            await generator.stop()
            return None
        
    except Exception as e:
        logger.error(f"[X] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await generator.stop()
        except:
            pass
        return None


def run_generate_and_download(prompt: str, headless: bool = False, target_duration: int = 15, 
                              add_music: bool = True) -> Optional[Dict]:
    """Sync wrapper for generate_and_download with Meta AI extension and music."""
    return asyncio.run(generate_and_download(prompt, headless, add_music=add_music, target_duration=target_duration))


async def add_music_to_create_url(create_url: str, headless: bool = False, extend_to: int = 15) -> Optional[Dict]:
    """
    Add music to an existing Meta AI video using the create page.
    Also extends the video if needed.
    
    Args:
        create_url: Meta AI create page URL (e.g., https://www.meta.ai/create/994679333719018/?prompt_id=...)
        headless: Run browser in headless mode
        extend_to: Target duration in seconds (default 15, set to 0 to skip extension)
    
    Returns:
        Download result dict or None
    """
    generator = MetaAIGenerator(headless=headless)
    
    try:
        await generator.start()
        
        # Check login
        if not await generator.is_logged_in():
            logger.info("[!] Not logged in. Attempting auto-login...")
            if FB_EMAIL and FB_PASSWORD:
                if not await generator.auto_login():
                    logger.warning("[!] Auto-login failed, opening browser for manual login...")
                    await generator.stop()
                    generator = MetaAIGenerator(headless=False)
                    await generator.start()
                    if not await generator.wait_for_login(timeout=120):
                        return None
            else:
                await generator.stop()
                generator = MetaAIGenerator(headless=False)
                await generator.start()
                if not await generator.wait_for_login(timeout=120):
                    return None
        
        # Extend, add music and download
        result = await generator.add_music_and_download(create_url, extend_to=extend_to)
        
        await generator.stop()
        return result
        
    except Exception as e:
        logger.error(f"[X] Error: {e}")
        try:
            await generator.stop()
        except:
            pass
        return None


def run_add_music_to_create_url(create_url: str, headless: bool = False, extend_to: int = 15) -> Optional[Dict]:
    """Sync wrapper for add_music_to_create_url."""
    return asyncio.run(add_music_to_create_url(create_url, headless, extend_to))
