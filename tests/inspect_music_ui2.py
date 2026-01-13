"""Inspect Meta AI music UI structure - v2."""
import asyncio
from playwright.async_api import async_playwright

async def inspect_music_ui():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='profile/meta_ai_browser',
            headless=False,
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        # Go to create page
        print('[*] Loading create page...')
        await page.goto('https://www.meta.ai/create/994679333719018/?prompt_id=994679373719014', wait_until='domcontentloaded')
        await page.wait_for_timeout(5000)
        
        # Get page content and find all text
        print('[*] Looking for Add music...')
        
        # Try different selectors
        selectors = [
            'button:has-text("Add music")',
            'div:has-text("Add music")',
            '[aria-label*="music"]',
            '[aria-label*="audio"]',
            'text=Add music',
            'text="Add music"',
        ]
        
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    print(f'[OK] Found with selector: {sel}')
                    box = await el.bounding_box()
                    print(f'    Position: {box}')
            except Exception as e:
                print(f'[X] {sel}: {e}')
        
        # Get all visible text on page
        print('\n[*] All buttons on page:')
        buttons = await page.query_selector_all('button')
        for i, btn in enumerate(buttons[:20]):
            try:
                text = await btn.inner_text()
                if text.strip():
                    print(f'  {i}: "{text.strip()[:50]}"')
            except:
                pass
        
        # Look for sidebar content
        print('\n[*] Looking for sidebar elements...')
        sidebar = await page.query_selector_all('div[class*="sidebar"], div[class*="panel"], aside')
        print(f'Found {len(sidebar)} sidebar elements')
        
        # Get all text containing "music" or "audio"
        print('\n[*] Elements with music/audio text:')
        all_elements = await page.query_selector_all('*')
        for el in all_elements[:500]:
            try:
                text = await el.inner_text()
                if text and ('music' in text.lower() or 'audio' in text.lower()) and len(text) < 100:
                    tag = await el.evaluate('el => el.tagName')
                    print(f'  <{tag}>: "{text.strip()}"')
            except:
                pass
        
        print('\n[*] Browser open - check manually')
        print('Press Ctrl+C to close...')
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(inspect_music_ui())
