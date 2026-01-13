"""Inspect Meta AI music UI structure."""
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
        await page.goto('https://www.meta.ai/create/994679333719018/?prompt_id=994679373719014', wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        
        # Click Add music
        add_music = await page.query_selector('button:has-text("Add music")')
        if add_music:
            print('[OK] Found Add music button')
            await add_music.click()
            await page.wait_for_timeout(3000)
            
            # Look for music-related elements
            elements = await page.query_selector_all('button, [role="option"], [role="listitem"], [role="button"]')
            print(f'Found {len(elements)} potential elements')
            
            for i, el in enumerate(elements[:30]):
                try:
                    text = await el.inner_text()
                    aria = await el.get_attribute('aria-label')
                    if text and len(text) < 100:
                        print(f'{i}: text="{text[:50]}" aria="{aria}"')
                    elif aria:
                        print(f'{i}: aria="{aria}"')
                except:
                    pass
        else:
            print('[X] Add music button not found')
        
        # Keep browser open for inspection
        print('\nBrowser open - inspect the music UI manually')
        print('Press Enter to close...')
        input()
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(inspect_music_ui())
