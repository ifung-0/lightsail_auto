#!/usr/bin/env python3
"""
Minimal test to debug bot startup
"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    print("[TEST] Starting minimal bot test...")
    
    async with async_playwright() as p:
        print("[TEST] Launching browser...")
        browser = await p.chromium.launch(headless=False)
        
        print("[TEST] Creating page...")
        page = await browser.new_page()
        
        print("[TEST] Navigating to LightSail (timeout: 60s)...")
        try:
            await page.goto("https://lightsailed.com/school/literacy/", timeout=60000)
            print(f"[TEST] Goto succeeded. URL: {page.url}")
        except Exception as e:
            print(f"[TEST] Goto error (might be timeout): {e}")
            print(f"[TEST] Current URL: {page.url}")
        
        print("[TEST] Checking for Library link...")
        try:
            # Try multiple selectors for Library link
            selectors = [
                'a:has-text("Library")',
                'a.link',
                'text=Library'
            ]
            library = None
            for sel in selectors:
                try:
                    library = await page.query_selector(sel)
                    if library:
                        print(f"[TEST] ✓ Found Library link with selector: {sel}")
                        break
                except:
                    pass
            
            if not library:
                print("[TEST] ✗ No Library link found with any selector")
                print("[TEST] Checking all links on page...")
                links = await page.query_selector_all('a')
                print(f"[TEST] Found {len(links)} total links")
                for i, link in enumerate(links[:5]):
                    text = await link.inner_text()
                    print(f"  Link {i}: {text}")
        except Exception as e:
            print(f"[TEST] Error checking library: {e}")
        
        print("[TEST] Taking screenshot...")
        try:
            await page.screenshot(path='test_startup.png')
            print("[TEST] Screenshot saved: test_startup.png")
        except Exception as e:
            print(f"[TEST] Screenshot error: {e}")
        
        print("[TEST] Waiting 5 seconds before close...")
        await asyncio.sleep(5)
        
        print("[TEST] Closing browser...")
        await browser.close()
        
    print("[TEST] Done!")

if __name__ == "__main__":
    asyncio.run(test())
