"""Debug: Find how to get to create page after video generation."""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright

async def debug_create_page():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir='profile/meta_ai_browser',
            headless=False,
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        # Go to Meta AI
        print('[*] Going to Meta AI...')
        await page.goto('https://www.meta.ai/', wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        
        # Enter a prompt
        print('[*] Entering prompt...')
        prompt_input = await page.query_selector('[role="textbox"]')
        if prompt_input:
            await prompt_input.click()
            await page.keyboard.type('Create a video of a dancing robot', delay=20)
            await page.wait_for_timeout(1000)
            await page.keyboard.press('Enter')
        
        # Wait for video
        print('[*] Waiting for video generation...')
        for i in range(60):
            await page.wait_for_timeout(2000)
            video = await page.query_selector('video')
            if video:
                print('[OK] Video found!')
                break
            if i % 5 == 0:
                print(f'[*] Still waiting... ({i*2}s)')
        
        await page.wait_for_timeout(5000)
        
        # Now let's see what's on the page
        print('\n[*] Current URL:', page.url)
        
        # Find all links
        print('\n[*] All links on page:')
        links = await page.query_selector_all('a')
        for link in links[:30]:
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                if href and ('create' in href.lower() or 'edit' in href.lower()):
                    print(f'  FOUND: href="{href}" text="{text[:30]}"')
            except:
                pass
        
        # Find all buttons
        print('\n[*] Buttons with edit/create/open text:')
        buttons = await page.query_selector_all('button, [role="button"]')
        for btn in buttons:
            try:
                text = await btn.inner_text()
                aria = await btn.get_attribute('aria-label')
                if text and any(x in text.lower() for x in ['edit', 'create', 'open', 'expand']):
                    print(f'  text="{text[:30]}" aria="{aria}"')
                elif aria and any(x in aria.lower() for x in ['edit', 'create', 'open', 'expand']):
                    print(f'  text="{text[:30]}" aria="{aria}"')
            except:
                pass
        
        # Check if there's a way to click on the video preview
        print('\n[*] Video element info:')
        video = await page.query_selector('video')
        if video:
            parent = await video.evaluate_handle('el => el.parentElement')
            parent_html = await parent.evaluate('el => el.outerHTML.substring(0, 500)')
            print(f'  Parent HTML: {parent_html[:200]}...')
        
        print('\n[*] Browser open - try clicking on video manually to see what happens')
        print('Close browser to exit...')
        
        try:
            await page.wait_for_event('close', timeout=300000)
        except:
            pass
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(debug_create_page())
