#!/usr/bin/env python3
"""
Test script to verify LightSail selectors work correctly
This helps debug if the website structure changes
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_selectors():
    """Test various selectors on LightSail website"""
    
    print("=" * 60)
    print("LightSail Selector Test")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to LightSail
        print("Navigating to LightSail...")
        try:
            await page.goto("https://lightsailed.com/school/literacy/", timeout=60000)
            print("Page loaded, waiting for network idle (timeout: 60s)...")
            await page.wait_for_load_state('networkidle', timeout=60000)
        except Exception as e:
            print(f"Navigation error: {e}")
            print(f"Current URL: {page.url}")
            print("Continuing with partial page...")
        
        print(f"Current URL: {page.url}")
        print()
        
        # Take screenshot of login page
        await page.screenshot(path='test_login_page.png')
        print("✓ Screenshot saved: test_login_page.png")
        
        # Test login form selectors
        print()
        print("Testing Login Form Selectors:")
        print("-" * 40)
        
        # Test username field selectors
        username_selectors = [
            'input[placeholder*="Username" i]',
            'input[name="username"]',
            'input[type="text"]',
            'input#username',
            'input[id*="user" i]',
            'input[class*="user" i]'
        ]
        
        for selector in username_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"✓ Username field found: {selector}")
                    break
            except:
                pass
        else:
            print("✗ No username field found with tested selectors")
        
        # Test password field selectors
        password_selectors = [
            'input[placeholder*="Password" i]',
            'input[name="password"]',
            'input[type="password"]',
            'input#password',
            'input[id*="pass" i]',
            'input[class*="pass" i]'
        ]
        
        for selector in password_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"✓ Password field found: {selector}")
                    break
            except:
                pass
        else:
            print("✗ No password field found with tested selectors")
        
        # Test login button selectors
        login_button_selectors = [
            'button:has-text("Log In")',
            'button[type="submit"]',
            'button.login',
            'button[id*="login" i]',
            'input[type="submit"]'
        ]
        
        for selector in login_button_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"✓ Login button found: {selector}")
                    break
            except:
                pass
        else:
            print("✗ No login button found with tested selectors")
        
        # Get all interactive elements
        print()
        print("All Interactive Elements on Page:")
        print("-" * 40)
        
        elements = await page.query_selector_all('input, button, a')
        for i, element in enumerate(elements[:20]):  # Limit to first 20
            try:
                tag = await element.evaluate('el => el.tagName')
                text = await element.inner_text()
                element_id = await element.get_attribute('id') or ''
                element_class = await element.get_attribute('class') or ''
                element_type = await element.get_attribute('type') or ''
                
                info = f"[{tag}]"
                if element_id:
                    info += f" id='{element_id}'"
                if element_class:
                    info += f" class='{element_class[:30]}'"
                if element_type:
                    info += f" type='{element_type}'"
                if text.strip():
                    info += f" text='{text.strip()[:30]}'"
                
                print(f"  {i+1}. {info}")
            except:
                pass
        
        print()
        print("=" * 60)
        print("Test Complete")
        print("=" * 60)
        print()
        print("Check test_login_page.png to see the login page")
        print()
        
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_selectors())
