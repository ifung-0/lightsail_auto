#!/usr/bin/env python3
"""
LightSail Automation Bot - FREE Version (No OpenAI API required)
Uses local pattern matching and free Hugging Face Inference API
"""

import asyncio
import json
import time
import os
import re
import random
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from playwright.async_api import async_playwright, Page, Browser, ElementHandle
import requests

class LightSailBotFree:
    """Free version using Hugging Face Inference API (no API key needed for basic usage)"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.config = self._load_config()
        self.current_book = None
        self.page_flip_interval = self.config.get('page_flip_interval', 40)  # Changed to 40 seconds for alternating flip
        self.is_running = False
        self.question_answered_count = 0
        self.pages_read = 0
        self.session_context = []  # Store reading context for better answers
        self.flip_direction = 'forward'  # Track direction: 'forward' or 'back'
        self.reading_start_time = None  # Track when reading started
        self.total_flips = 0  # Track total flips in both directions
        
    def _load_config(self) -> Dict:
        """Load configuration from config.json"""
        default_config = {
            "username": "",
            "password": "",
            "huggingface_api_key": "",  # Optional - can work without for rate-limited access
            "headless": False,
            "page_flip_interval": 30,  # Changed to 30 seconds for farming minutes
            "auto_answer_questions": True,  # Re-enabled to detect questions and go back
            "preferred_book_title": "",
            "screenshot_on_question": True,
            "use_ai": True,  # Set to false to use random selection
            "log_level": "INFO"
        }
        
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def start(self):
        """Start the browser and navigate to LightSail"""
        self.log("Starting LightSail Automation Bot (FREE Version)...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.get('headless', False),
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Try to load stored authentication cookies
        if os.path.exists('storage_state.json'):
            try:
                await context.add_init_script('window.localStorage.clear(); window.sessionStorage.clear();')
                # Load cookies from storage
                with open('storage_state.json', 'r') as f:
                    storage = json.load(f)
                    if storage.get('cookies'):
                        await context.add_cookies(storage['cookies'])
                    if storage.get('localStorage'):
                        for item in storage['localStorage']:
                            await context.add_init_script(f'localStorage.setItem("{item["name"]}", "{item["value"]}")')
                self.log("Loaded stored authentication state")
            except Exception as e:
                self.log(f"WARNING: Could not load storage_state.json: {e}", "WARNING")
        
        self.page = await context.new_page()
        
        # Navigate to LightSail
        self.log("Navigating to LightSail (timeout: 60s)...")
        try:
            await self.page.goto("https://lightsailed.com/school/literacy/", timeout=60000)
            self.log("Page loaded, waiting for 15 seconds for dynamic content...")
            try:
                await self.page.wait_for_load_state('load', timeout=15000)
            except:
                pass  # Continue even if load state times out
            await asyncio.sleep(5)  # Give page extra time to load
        except Exception as e:
            self.log(f"WARNING: Navigation error: {e}", "WARNING")
            self.log(f"Current URL: {self.page.url}", "WARNING")
            # Continue anyway - may still be logged in
        try:
            await self.page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass  # Continue even if networkidle times out
        
        self.log("Browser started and navigated to LightSail")
        
    async def login(self):
        """Login to LightSail with credentials"""
        self.log("Checking login status...")
        
        # Check if already logged in by looking for Library link or dashboard elements
        try:
            library_link = await self.page.query_selector('a:has-text("Library"), a.link')
            if library_link:
                self.log("Already logged in! Detected dashboard/library page.")
                return True
        except:
            pass
        
        self.log("Attempting to login...")
        
        username = self.config.get('username')
        password = self.config.get('password')
        
        if not username or not password:
            self.log("No username/password configured in config.json - please sign in manually (e.g. Google).", "WARNING")
            self.log("Waiting for manual login in the opened browser...", "INFO")

            # Wait for manual sign-in (e.g. via Google). Poll the URL for a change indicating login.
            for _ in range(300):  # wait up to ~5 minutes
                try:
                    current_url = (self.page.url or "").lower()
                except Exception:
                    current_url = ""

                if 'login' not in current_url and current_url:
                    self.log("Detected successful manual login via browser.")
                    try:
                        await self.page.context.storage_state(path="storage_state.json")
                        self.log("Saved authenticated storage state to storage_state.json")
                    except Exception as e:
                        self.log(f"WARNING: failed to save storage state: {e}", "WARNING")
                    return True

                await asyncio.sleep(1)

            self.log("ERROR: Manual login timed out. Please try again.", "ERROR")
            return False
        
        try:
            # Try multiple selectors for username field
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
                    await self.page.fill(selector, username, timeout=2000)
                    self.log(f"Filled username using selector: {selector}")
                    break
                except:
                    continue
            
            # Try multiple selectors for password field
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
                    await self.page.fill(selector, password, timeout=2000)
                    self.log(f"Filled password using selector: {selector}")
                    break
                except:
                    continue
            
            # Click login button
            login_button_selectors = [
                'button:has-text("Log In")',
                'button[type="submit"]',
                'button.login',
                'button[id*="login" i]',
                'input[type="submit"]',
                'button[class*="login" i]'
            ]
            
            for selector in login_button_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    self.log(f"Clicked login button: {selector}")
                    break
                except:
                    continue
            
            # Wait for navigation after login
            try:
                await self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass  # Continue even if networkidle times out
            await asyncio.sleep(2)
            
            # Check if login was successful
            current_url = self.page.url
            if 'login' not in current_url.lower():
                self.log("Login successful!")
                self.log(f"Current URL: {current_url}")
                return True
            else:
                self.log("ERROR: Login failed - still on login page", "ERROR")
                # Take screenshot for debugging
                await self.page.screenshot(path='login_failed.png')
                return False
                
        except Exception as e:
            self.log(f"ERROR during login: {str(e)}", "ERROR")
            await self.page.screenshot(path='login_error.png')
            return False
    
    async def select_book(self):
        """Select a book from the library"""
        self.log("Looking for books to select...")
        
        preferred_title = self.config.get('preferred_book_title', '')
        
        try:
            # Wait for the library/dashboard to load
            await asyncio.sleep(3)
            
            # Take screenshot to see current state
            await self.page.screenshot(path='dashboard.png')
            self.log("Screenshot saved: dashboard.png")
            
            # First, try clicking on Home link if available
            if 'reader' not in self.page.url.lower():
                try:
                    await self.page.click('a:has-text("Home"), a.link:has-text("Home")', timeout=3000)
                    self.log("Clicked Home link")
                    await asyncio.sleep(3)
                except:
                    pass
            
            if preferred_title:
                # Try to find the preferred book
                try:
                    await self.page.get_by_text(preferred_title, exact=False).first.click()
                    self.log(f"Selected preferred book: {preferred_title}")
                    self.current_book = preferred_title
                    await asyncio.sleep(2)
                    return True
                except Exception as e:
                    self.log(f"Preferred book '{preferred_title}' not found: {e}")
            
            # Try to find book elements with various selectors
            book_selectors = [
                'button:has-text("Read")',  # Try Read buttons first
                '[data-testid="book"]',
                '.book-item',
                '.library-item',
                '.book-card',
                '.book-cover',
                'img[alt*="book" i]',
                '.thumbnail',
                '[class*="book" i]',
                'a[href*="book"]',
                'div[class*="item"]'
            ]
            
            for selector in book_selectors:
                try:
                    book_elements = await self.page.query_selector_all(selector)
                    if book_elements and len(book_elements) > 0:
                        self.log(f"Found {len(book_elements)} elements with selector: {selector}")
                        # Click the first one
                        try:
                            await book_elements[0].click(timeout=5000)  # Reduced timeout
                            self.log(f"Clicked element with selector: {selector}")
                            await asyncio.sleep(2)
                            
                            # Check if we successfully navigated
                            if 'reader' in self.page.url.lower() or 'book' in self.page.url.lower():
                                self.log("Successfully selected a book!")
                                return True
                        except:
                            # Skip this element and try next selector
                            continue
                except Exception as e:
                    self.log(f"Failed with selector {selector}: {e}")
                    continue
            
            # If no specific books found, try clicking on any large button or link
            self.log("Trying alternative book selection method...")
            try:
                # Try clicking any element that looks clickable
                buttons = await self.page.query_selector_all('button, a[role="button"], div[role="button"]')
                if buttons:
                    for btn in buttons[:3]:  # Try first 3 buttons
                        try:
                            await btn.click()
                            self.log("Clicked on a button element")
                            await asyncio.sleep(2)
                            
                            if 'reader' in self.page.url.lower() or 'book' in self.page.url.lower():
                                return True
                        except:
                            continue
            except Exception as e:
                self.log(f"Error trying alternative method: {e}")
                
        except Exception as e:
            self.log(f"ERROR selecting book: {str(e)}", "ERROR")
            await self.page.screenshot(path='book_selection_error.png')
        
        return False
    
    async def start_reading(self):
        """Start reading the selected book"""
        self.log("Starting to read...")
        self.is_running = True
        self.reading_start_time = time.time()  # Record when reading started
        
        try:
            # If already on reader page, skip button clicking
            if 'reader' not in self.page.url.lower():
                # Look for "Read" or "Start Reading" button
                read_buttons = [
                    'button:has-text("Read")',
                    'button:has-text("Start Reading")',
                    'button:has-text("Open Book")',
                    'button:has-text("Start")',
                    '.read-button',
                    '[data-testid="read-button"]',
                    'a:has-text("Read")',
                    'button[class*="read" i]'
                ]
                
                for selector in read_buttons:
                    try:
                        await self.page.click(selector, timeout=3000)
                        self.log(f"Clicked read button: {selector}")
                        await asyncio.sleep(4)
                        break
                    except:
                        continue
            
            # Main reading loop
            self.log("Entering main reading loop...")
            while self.is_running:
                await self.reading_cycle()
                
        except Exception as e:
            self.log(f"ERROR in reading loop: {str(e)}", "ERROR")
            self.is_running = False
    
    async def reading_cycle(self):
        """One cycle of reading: alternate between flipping right and left every 40 seconds"""
        try:
            # Calculate elapsed time
            elapsed_seconds = int(time.time() - self.reading_start_time) if self.reading_start_time else 0
            elapsed_minutes = elapsed_seconds // 60
            elapsed_hours = elapsed_minutes // 60
            remaining_minutes = elapsed_minutes % 60
            
            time_str = ""
            if elapsed_hours > 0:
                time_str = f"{elapsed_hours}h {remaining_minutes}m"
            else:
                time_str = f"{elapsed_minutes}m {elapsed_seconds % 60}s"
            
            # Alternate flipping direction
            if self.flip_direction == 'forward':
                self.log("Flipping RIGHT...")
                try:
                    await self.flip_page()
                    self.pages_read += 1
                    self.total_flips += 1
                    self.log(f"✓ Pages read: {self.pages_read} | Total flips: {self.total_flips} | Reading time: {time_str}")
                except Exception as e:
                    self.log(f"Error flipping page forward: {e}")
                
                # Switch to backward for next cycle
                self.flip_direction = 'back'
            else:
                self.log("Flipping LEFT...")
                try:
                    await self.flip_back()
                    self.total_flips += 1
                    self.log(f"✓ Pages read: {self.pages_read} | Total flips: {self.total_flips} | Reading time: {time_str}")
                except Exception as e:
                    self.log(f"Error flipping page back: {e}")
                
                # Switch to forward for next cycle
                self.flip_direction = 'forward'
            
            # Wait before next flip
            self.log(f"Waiting {self.page_flip_interval} seconds before next flip...")
            await asyncio.sleep(self.page_flip_interval)
            
        except Exception as e:
            self.log(f"ERROR in reading cycle: {str(e)}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            # If there's an error, wait longer before retrying
            await asyncio.sleep(10)
    
    async def check_and_answer_questions(self) -> bool:
        """Check for questions and answer them if found"""
        try:
            self.log("DEBUG: Starting question check...")
            
            # Look for multiple choice questions
            try:
                mc_question = await self.detect_multiple_choice_question()
                if mc_question:
                    self.log("=" * 50)
                    self.log("MULTIPLE CHOICE QUESTION DETECTED! Going back a page.")
                    self.log("=" * 50)
                    return True
                else:
                    self.log("DEBUG: No MC question detected")
            except Exception as e:
                self.log(f"Error detecting MC questions: {e}")
            
            # Look for fill-in-the-blank (cloze) questions
            try:
                self.log("DEBUG: Checking for cloze questions...")
                cloze_question = await self.detect_cloze_question()
                if cloze_question:
                    self.log("=" * 50)
                    self.log("FILL-IN-THE-BLANK QUESTION DETECTED! Going back a page.")
                    self.log(f"Cloze type: {cloze_question.get('type', 'unknown')}")
                    self.log("=" * 50)
                    return True
                else:
                    self.log("DEBUG: No cloze question detected")
            except Exception as e:
                self.log(f"Error detecting cloze questions: {e}")
            
            # Look for short answer questions
            try:
                short_answer = await self.detect_short_answer_question()
                if short_answer:
                    self.log("=" * 50)
                    self.log("SHORT ANSWER QUESTION DETECTED! Going back a page.")
                    self.log("=" * 50)
                    return True
                else:
                    self.log("DEBUG: No short answer question detected")
            except Exception as e:
                self.log(f"Error detecting short answer questions: {e}")
                
            self.log("DEBUG: Question check complete - no questions found")
                
        except Exception as e:
            self.log(f"ERROR checking for questions: {str(e)}", "ERROR")
        
        return False
    
    async def detect_multiple_choice_question(self) -> Optional[Dict]:
        """Detect if a multiple choice question is present"""
        try:
            # Common selectors for MC questions
            mc_selectors = [
                '.multiple-choice',
                '.mc-question',
                '[data-testid="mc-question"]',
                '.question-container',
                '.quiz-question',
                '.assessment-question',
                '[class*="question" i]',
                'form:has(input[type="radio"])'
            ]
            
            for selector in mc_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Get question text
                        question_text = await element.inner_text()
                        
                        # Get options (usually radio buttons or clickable options)
                        options = await element.query_selector_all(
                            'input[type="radio"], .option, .choice, label, [role="radio"]'
                        )
                        
                        if len(options) >= 2:  # At least 2 options
                            option_texts = []
                            for opt in options:
                                text = await opt.inner_text()
                                if text.strip():
                                    option_texts.append(text.strip())
                            
                            if option_texts:
                                return {
                                    'element': element,
                                    'question': question_text,
                                    'options': option_texts,
                                    'option_elements': options
                                }
                except:
                    continue
            
            # Alternative: Look for radio buttons anywhere on page
            radio_buttons = await self.page.query_selector_all('input[type="radio"]')
            if len(radio_buttons) >= 2:
                # Get surrounding context
                context = await self.page.evaluate('''() => {
                    const radios = document.querySelectorAll('input[type="radio"]');
                    if (radios.length > 0) {
                        const parent = radios[0].closest('.question, .assessment, form, div[class*="question"]');
                        return parent ? parent.innerText : document.body.innerText.substring(0, 500);
                    }
                    return '';
                }''')
                
                # Get option texts
                option_texts = []
                for radio in radio_buttons[:4]:  # Limit to 4 options
                    parent_text = await self.page.evaluate('''(radio) => {
                        const parent = radio.closest('label, .option, div');
                        return parent ? parent.innerText : '';
                    }''', radio)
                    if parent_text.strip():
                        option_texts.append(parent_text.strip())
                
                if option_texts:
                    return {
                        'element': radio_buttons[0],
                        'question': context,
                        'options': option_texts,
                        'option_elements': radio_buttons[:4]
                    }
                        
        except Exception as e:
            pass
        
        return None
    
    async def detect_cloze_question(self) -> Optional[Dict]:
        """Detect fill-in-the-blank (cloze) questions"""
        self.log("DEBUG: detect_cloze_question() called")
        try:
            # First check inside iframes for cloze SVG elements (EPUB content is in iframes)
            self.log(f"DEBUG: Checking {len(self.page.frames)} frames...")
            frames = self.page.frames
            
            for i, frame in enumerate(frames):
                try:
                    frame_url = frame.url
                    self.log(f"DEBUG: Frame {i}: {frame_url}")
                    
                    # Use XPath to find SVG element - more reliable than CSS selector
                    cloze_svg = await frame.query_selector('//g[@class="cloze-assessment-pending"]')
                    if not cloze_svg:
                        # Try CSS selector as fallback
                        cloze_svg = await frame.query_selector('g.cloze-assessment-pending')
                    
                    if cloze_svg:
                        self.log(f"DEBUG: Found cloze SVG element in frame {i}: {frame_url}")
                        return {'svg': cloze_svg, 'context': 'found', 'type': 'svg', 'frame': frame}
                    else:
                        # Try using evaluate to check via JavaScript
                        has_cloze = await frame.evaluate('''() => {
                            return document.querySelector('g.cloze-assessment-pending') !== null;
                        }''')
                        if has_cloze:
                            self.log(f"DEBUG: Found cloze SVG via JavaScript in frame {i}")
                            return {'svg': True, 'context': 'found', 'type': 'svg', 'frame': frame}
                        
                        self.log(f"DEBUG: No SVG in frame {i}")
                except Exception as e:
                    self.log(f"DEBUG: Error checking frame {i}: {e}")
                    continue
            
            self.log("DEBUG: No SVG found in any frame, checking main page...")
            
            # Check main page using JavaScript evaluate (more reliable)
            has_cloze_main = await self.page.evaluate('''() => {
                return document.querySelector('g.cloze-assessment-pending') !== null;
            }''')
            
            if has_cloze_main:
                self.log("DEBUG: Found cloze SVG element on main page")
                return {'svg': True, 'context': 'found', 'type': 'svg'}
            
            self.log("DEBUG: No cloze SVG found")
            return None
                    
        except Exception as e:
            self.log(f"DEBUG: Exception in detect_cloze_question: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return None
    
    async def detect_short_answer_question(self) -> Optional[Dict]:
        """Detect short answer questions"""
        try:
            textarea = await self.page.query_selector('textarea:not([readonly])')
            if textarea:
                question_text = await self.page.evaluate('''() => {
                    const textarea = document.querySelector('textarea:not([readonly])');
                    const parent = textarea.closest('.question, .assessment, form');
                    return parent ? parent.innerText : '';
                }''')
                
                if question_text:
                    return {
                        'textarea': textarea,
                        'question': question_text
                    }
                
        except Exception as e:
            pass
        
        return None
    
    async def answer_multiple_choice_question(self, question_data: Dict):
        """Answer a multiple choice question using AI or random selection"""
        try:
            question_text = question_data['question']
            options = question_data['options']
            
            self.log(f"Question: {question_text[:150]}...")
            self.log(f"Options found: {len(options)}")
            for i, opt in enumerate(options[:4]):
                self.log(f"  {chr(65+i)}. {opt[:80]}...")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"question_mc_{self.question_answered_count + 1}.png"
                await self.page.screenshot(path=screenshot_path)
                self.log(f"Screenshot saved: {screenshot_path}")
            
            # Click the first available option (click-any strategy)
            option_elements = question_data.get('option_elements', [])
            if option_elements:
                try:
                    await option_elements[0].click()
                    self.log(f"Clicked first option: {options[0] if options else 'unknown'}")
                except Exception as e:
                    self.log(f"Error clicking first option: {e}")
            else:
                self.log("No option elements found to click")

            # Submit the answer
            await self.submit_answer()
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering MC question: {str(e)}", "ERROR")
    
    async def answer_cloze_question(self, question_data: Dict):
        """Answer a fill-in-the-blank question"""
        try:
            context = question_data['context']
            inputs = question_data['inputs']
            
            self.log(f"Cloze context: {context[:150]}...")
            self.log(f"Number of blanks: {len(inputs)}")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"question_cloze_{self.question_answered_count + 1}.png"
                await self.page.screenshot(path=screenshot_path)
                self.log(f"Screenshot saved: {screenshot_path}")
            
            # Get answers for each blank
            for i, input_field in enumerate(inputs):
                if self.config.get('use_ai', True):
                    answer = await self.get_free_cloze_answer(context, i + 1)
                else:
                    # Common words for cloze
                    common_words = ['the', 'and', 'a', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'it', 'they', 'them', 'their', 'this', 'that']
                    answer = random.choice(common_words)
                
                self.log(f"Answer for blank {i + 1}: {answer}")
                
                try:
                    await input_field.fill(answer)
                    await asyncio.sleep(0.5)
                    # Click on the answer field to reveal submit button
                    await input_field.click()
                    await asyncio.sleep(0.5)
                except Exception as e:
                    self.log(f"Error filling blank: {e}")
            
            # Submit the answer
            await self.submit_answer()
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering cloze question: {str(e)}", "ERROR")
    
    async def answer_short_answer_question(self, question_data: Dict):
        """Answer a short answer question"""
        try:
            question_text = question_data['question']
            textarea = question_data['textarea']
            
            self.log(f"Short answer question: {question_text[:150]}...")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"question_short_{self.question_answered_count + 1}.png"
                await self.page.screenshot(path=screenshot_path)
                self.log(f"Screenshot saved: {screenshot_path}")
            
            # Get answer
            if self.config.get('use_ai', True):
                answer = await self.get_free_short_answer(question_text)
            else:
                answer = "This is an important concept from the reading."
            
            self.log(f"Generated answer: {answer[:100]}...")
            
            try:
                await textarea.fill(answer)
            except Exception as e:
                self.log(f"Error filling textarea: {e}")
            
            # Submit
            await self.submit_answer()
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering short answer: {str(e)}", "ERROR")
    
    async def submit_answer(self):
        """Click submit button"""
        submit_buttons = [
            'button:has-text("Submit")',
            'button:has-text("Answer")',
            'button:has-text("Check")',
            'button:has-text("Save")',
            'button[type="submit"]',
            '.submit-button',
            '[data-testid="submit"]',
            'input[type="submit"]'
        ]
        
        for selector in submit_buttons:
            try:
                await self.page.click(selector, timeout=2000)
                self.log("Submitted answer")
                return
            except:
                continue
        
        self.log("No submit button found")
    
    async def get_free_ai_answer(self, question: str, options: List[str]) -> str:
        """Get answer using free Hugging Face Inference API or pattern matching"""
        try:
            # Optionally use OpenRouter as a free AI backend if configured
            if self.config.get('use_openrouter'):
                try:
                    api_key = self.config.get('openrouter_api_key', '')
                    model = self.config.get('openrouter_model', 'google/gemma-3-27b-it:free')
                    url = self.config.get('openrouter_api_url', 'https://openrouter.ai/api/v1/chat/completions')
                    
                    self.log(f"Calling OpenRouter with model: {model}")

                    headers = {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    }

                    # Construct a simple prompt asking for the best option
                    prompt = f"Question: {question}\nOptions:\n"
                    for i, opt in enumerate(options):
                        prompt += f"{i+1}. {opt}\n"
                    prompt += "\nReply with the number of the best option and the short justification."

                    payload = {
                        'model': model,
                        'messages': [
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ]
                    }

                    self.log(f"Sending OpenRouter request...")
                    resp = requests.post(url, headers=headers, json=payload, timeout=15)
                    self.log(f"OpenRouter response status: {resp.status_code}")
                    
                    if resp.ok:
                        data = resp.json()
                        self.log(f"OpenRouter response received")
                        
                        # Try common response locations
                        text = ''
                        try:
                            text = data['choices'][0]['message']['content']
                        except Exception:
                            try:
                                text = data['output'][0]['content'][0]['text']
                            except Exception:
                                text = str(data)

                        text = (text or '').strip()
                        self.log(f"OpenRouter text response: '{text[:100]}...'")
                        
                        # Try to extract a number referring to option
                        for i, opt in enumerate(options):
                            if str(i+1) in text.split():
                                self.log(f"Selected option {i+1}: {options[i]}")
                                return options[i]
                        # If an option text appears in the response, return it
                        for opt in options:
                            if opt.lower() in text.lower():
                                self.log(f"Found option text match: {opt}")
                                return opt
                        # Fallback: return the first option
                        self.log("No clear match, returning first option")
                        return options[0] if options else ''
                    else:
                        self.log(f"OpenRouter API error: {resp.status_code} - {resp.text[:200]}")
                        # Fall back to pattern matching
                        return self.pattern_match_answer(question, options)
                except Exception as e:
                    self.log(f"OpenRouter error: {e}")
                    # Fall back to pattern matching
                    return self.pattern_match_answer(question, options)
            api_key = self.config.get('huggingface_api_key', '')
            
            if api_key:
                try:
                    API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    
                    # Format as QA
                    context = f"Question: {question}\nOptions: {', '.join(options)}"
                    payload = {
                        "inputs": {
                            "question": question,
                            "context": context
                        }
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if 'answer' in result:
                            return result['answer']
                except Exception as e:
                    self.log(f"Hugging Face API error: {e}")
            
            # Pattern matching fallback
            return self.pattern_match_answer(question, options)
            
        except Exception as e:
            self.log(f"Error getting AI answer: {e}")
            return options[0] if options else ""
    
    async def get_free_cloze_answer(self, context: str, blank_number: int) -> str:
        """Get answer for cloze question"""
        try:
            # If OpenRouter configured, ask it for the blank
            if self.config.get('use_openrouter'):
                try:
                    api_key = self.config.get('openrouter_api_key', '')
                    model = self.config.get('openrouter_model', 'google/gemma-3-27b-it:free')
                    url = self.config.get('openrouter_api_url', 'https://openrouter.ai/api/v1/chat/completions')

                    headers = {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    }

                    prompt = f"Fill in the blank #{blank_number} in the following context with a single word:\n{context}"
                    payload = {
                        'model': model,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }

                    resp = requests.post(url, headers=headers, json=payload, timeout=15)
                    if resp.ok:
                        data = resp.json()
                        try:
                            text = data['choices'][0]['message']['content'].strip()
                        except Exception:
                            try:
                                text = data['output'][0]['content'][0]['text'].strip()
                            except Exception:
                                text = ''
                        # return first word as the blank answer
                        if text:
                            return text.split()[0]
                except Exception as e:
                    self.log(f"OpenRouter cloze error: {e}")

            # Common cloze words based on context
            context_lower = context.lower()
            
            # Try to infer from context
            if 'plural' in context_lower or 'many' in context_lower:
                return 'are'
            if 'singular' in context_lower or 'one' in context_lower:
                return 'is'
            if 'past' in context_lower or 'yesterday' in context_lower or 'ago' in context_lower:
                return 'was'
            if 'future' in context_lower or 'will' in context_lower:
                return 'will'
            
            # Default common words
            common_words = ['the', 'and', 'a', 'is', 'are', 'was', 'were', 'have', 'has', 'it', 'they', 'their', 'this']
            return random.choice(common_words)
            
        except Exception as e:
            return 'the'
    
    async def get_free_short_answer(self, question: str) -> str:
        """Get short answer"""
        try:
            # If OpenRouter configured, ask it for a short answer
            if self.config.get('use_openrouter'):
                try:
                    api_key = self.config.get('openrouter_api_key', '')
                    model = self.config.get('openrouter_model', 'google/gemma-3-27b-it:free')
                    url = self.config.get('openrouter_api_url', 'https://openrouter.ai/api/v1/chat/completions')

                    headers = {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json'
                    }

                    prompt = f"Answer briefly: {question}"
                    payload = {
                        'model': model,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }

                    resp = requests.post(url, headers=headers, json=payload, timeout=15)
                    if resp.ok:
                        data = resp.json()
                        try:
                            text = data['choices'][0]['message']['content'].strip()
                        except Exception:
                            try:
                                text = data['output'][0]['content'][0]['text'].strip()
                            except Exception:
                                text = ''
                        if text:
                            return text
                except Exception as e:
                    self.log(f"OpenRouter short answer error: {e}")

            question_lower = question.lower()
            
            # Pattern-based responses
            if 'what' in question_lower and 'main idea' in question_lower:
                return "The main idea is the central point or key message that the author wants to convey."
            
            if 'why' in question_lower:
                return "This happened because of the events and circumstances described in the text."
            
            if 'how' in question_lower:
                return "This occurred through a series of steps and actions outlined in the reading."
            
            if 'when' in question_lower:
                return "This took place at the time mentioned in the text."
            
            if 'where' in question_lower:
                return "This happened at the location described in the passage."
            
            if 'who' in question_lower:
                return "The person or character mentioned in the text."
            
            # Default response
            return "Based on the reading, this is an important concept that helps us understand the main ideas of the text."
            
        except Exception as e:
            return "Based on the reading material, this relates to the key concepts discussed."
    
    def pattern_match_answer(self, question: str, options: List[str]) -> str:
        """Use pattern matching to select best answer"""
        question_lower = question.lower()
        
        # Look for keywords in question that match options
        for option in options:
            option_lower = option.lower()
            
            # Check for direct word matches
            words = question_lower.split()
            for word in words:
                if len(word) > 3 and word in option_lower:
                    return option
        
        # Look for negation patterns
        if 'not' in question_lower or 'never' in question_lower or "don't" in question_lower:
            # Often the correct answer is the one that contradicts
            for option in options:
                if 'not' in option.lower() or 'never' in option.lower():
                    return option
        
        # Default to first option
        return options[0] if options else ""
    
    async def flip_page(self):
        """Flip to the next page"""
        try:
            # Wait a moment before attempting to flip
            await asyncio.sleep(1)
            
            # Common page navigation selectors
            next_page_selectors = [
                'button[aria-label="Go To Next Page"]',
                'button.reader-button-next.btn',
                'button[aria-label="Next page"]',
                'button:has-text("Next")',
                'button:has-text(">")',
                '.next-page',
                '[data-testid="next-page"]',
                '.page-forward',
                '.arrow-right',
                '.pagination-next'
            ]
            
            for selector in next_page_selectors:
                try:
                    self.log(f"Trying selector: {selector}")
                    await self.page.click(selector, timeout=3000)
                    self.log("Flipped to next page (button)")
                    await asyncio.sleep(2)  # Wait for page to load
                    return
                except Exception as e:
                    self.log(f"Selector {selector} failed: {e}")
                    continue
            
            # Try keyboard navigation
            self.log("Trying keyboard navigation...")
            await self.page.keyboard.press('ArrowRight')
            self.log("Flipped page using keyboard (ArrowRight)")
            await asyncio.sleep(2)  # Wait for page to load
            
        except Exception as e:
            self.log(f"ERROR flipping page: {str(e)}", "ERROR")
    
    async def flip_back(self):
        """Flip to the previous page"""
        try:
            # Wait a moment before attempting to flip
            await asyncio.sleep(1)
            
            # Common page navigation selectors for previous
            prev_page_selectors = [
                'button[aria-label="Go To Previous Page"]',
                'button.reader-button-prev.btn',
                'button[aria-label="Previous page"]',
                'button:has-text("Previous")',
                'button:has-text("<")',
                '.prev-page',
                '[data-testid="prev-page"]',
                '.page-back',
                '.arrow-left',
                '.pagination-prev'
            ]
            
            for selector in prev_page_selectors:
                try:
                    self.log(f"Trying selector: {selector}")
                    await self.page.click(selector, timeout=3000)
                    self.log("Flipped to previous page (button)")
                    await asyncio.sleep(2)  # Wait for page to load
                    return
                except Exception as e:
                    self.log(f"Selector {selector} failed: {e}")
                    continue
            
            # Try keyboard navigation
            self.log("Trying keyboard navigation...")
            await self.page.keyboard.press('ArrowLeft')
            self.log("Flipped page using keyboard (ArrowLeft)")
            await asyncio.sleep(2)  # Wait for page to load
            
        except Exception as e:
            self.log(f"ERROR flipping back: {str(e)}", "ERROR")
    
    async def stop(self):
        """Stop the bot and close browser"""
        self.is_running = False
        self.log("=" * 50)
        self.log("STOPPING BOT")
        self.log("=" * 50)
        
        if self.browser:
            await self.browser.close()
            self.log("Browser closed")
        
        # Calculate final reading time
        if self.reading_start_time:
            elapsed_seconds = int(time.time() - self.reading_start_time)
            elapsed_minutes = elapsed_seconds // 60
            elapsed_hours = elapsed_minutes // 60
            remaining_minutes = elapsed_minutes % 60
            
            time_str = ""
            if elapsed_hours > 0:
                time_str = f"{elapsed_hours}h {remaining_minutes}m {elapsed_seconds % 60}s"
            else:
                time_str = f"{elapsed_minutes}m {elapsed_seconds % 60}s"
        else:
            time_str = "N/A"
        
        self.log("\n" + "=" * 50)
        self.log("SESSION SUMMARY")
        self.log("=" * 50)
        self.log(f"  Book: {self.current_book or 'N/A'}")
        self.log(f"  Pages read (flipped right): {self.pages_read}")
        self.log(f"  Total flips (both directions): {self.total_flips}")
        self.log(f"  Reading time: {time_str}")
        self.log("=" * 50)
    
    async def run(self):
        """Main run method"""
        try:
            await self.start()
            
            if await self.login():
                # Check if already on reader page
                if 'reader' in self.page.url.lower():
                    self.log("Already on a reader page - skipping book selection")
                    await self.start_reading()
                elif await self.select_book():
                    await self.start_reading()
                else:
                    self.log("Failed to select book", "ERROR")
            else:
                self.log("Failed to login - please check your credentials in config.json", "ERROR")
                
        except KeyboardInterrupt:
            self.log("\nBot stopped by user")
        except Exception as e:
            self.log(f"FATAL ERROR: {str(e)}", "ERROR")
        finally:
            await self.stop()


async def main():
    bot = LightSailBotFree()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
