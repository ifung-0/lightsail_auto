#!/usr/bin/env python3
"""
Setup script for LightSail Automation Bot
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✓ Packages installed")

def install_playwright():
    """Install Playwright browsers"""
    print("Installing Playwright Chromium browser...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    print("✓ Playwright Chromium installed")

def create_config():
    """Create config.json if it doesn't exist"""
    if not os.path.exists('config.json'):
        print("Creating config.json...")
        config_content = '''{
  "username": "YOUR_USERNAME_HERE",
  "password": "YOUR_PASSWORD_HERE",
  "openai_api_key": "",
  "headless": false,
  "page_flip_interval": 120,
  "auto_answer_questions": true,
  "preferred_book_title": "",
  "screenshot_on_question": true,
  "use_ai": true
}'''
        with open('config.json', 'w') as f:
            f.write(config_content)
        print("✓ config.json created - PLEASE EDIT WITH YOUR CREDENTIALS")
    else:
        print("✓ config.json already exists")

def main():
    print("=" * 50)
    print("LightSail Automation Bot - Setup")
    print("=" * 50)
    print()
    
    try:
        install_requirements()
        install_playwright()
        create_config()
        
        print()
        print("=" * 50)
        print("Setup Complete!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Edit config.json with your LightSail credentials")
        print("2. Run: python lightsail_bot_free_ai.py")
        print()
        print("For OpenAI version (requires API key):")
        print("  Run: python lightsail_bot.py")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
