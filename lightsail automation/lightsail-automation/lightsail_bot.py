#!/usr/bin/env python3
"""
LightSail Automation Bot
Automatically reads books, flips pages, and answers comprehension questions
"""

import asyncio
import json
import time
import os
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from playwright.async_api import async_playwright, Page, Browser, ElementHandle
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class LightSailBot:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.config = self._load_config()
        self.current_book = None
        self.page_flip_interval = 120  # 2 minutes in seconds
        self.is_running = False
        self.question_answered_count = 0
        self.pages_read = 0
        
        # Initialize OpenAI
        # Support OpenRouter (OpenAI-compatible) as an alternative free backend.
        # To enable, set `use_openrouter` to true in config.json and provide `openrouter_api_key`.
        if self.config.get('use_openrouter'):
            openai.api_key = self.config.get('openrouter_api_key', '')
            # Default OpenRouter API base; change in config if needed
            openai.api_base = self.config.get('openrouter_api_base', 'https://api.openrouter.ai/v1')
            self.log('Using OpenRouter as AI backend')
        else:
            openai.api_key = self.config.get('openai_api_key', '')
        
    def _load_config(self) -> Dict:
        """Load configuration from config.json"""
        default_config = {
            "username": "",
            "password": "",
            "openai_api_key": "",
            "headless": False,
            "page_flip_interval": 120,
            "auto_answer_questions": True,
            "preferred_book_title": "",
            "reading_speed_wpm": 200,
            "screenshot_on_question": True,
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
        self.log("Starting LightSail Automation Bot...")
        
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
            # Fill in username
            await self.page.fill('input[placeholder="Username"], input[name="username"], input[type="text"]', username)
            
            # Fill in password
            await self.page.fill('input[placeholder="Password"], input[name="password"], input[type="password"]', password)
            
            # Click login button
            await self.page.click('button:has-text("Log In"), button[type="submit"]')
            
            # Wait for navigation after login
            try:
                await self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass  # Continue even if networkidle times out
            await asyncio.sleep(2)
            
            # Check if login was successful
            if 'login' not in self.page.url.lower():
                self.log("Login successful!")
                return True
            else:
                self.log("ERROR: Login failed - still on login page", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"ERROR during login: {str(e)}", "ERROR")
            return False
    
    async def select_book(self):
        """Select a book from the library"""
        self.log("Looking for books to select...")
        
        preferred_title = self.config.get('preferred_book_title', '')
        
        try:
            # Wait for the library to load
            await asyncio.sleep(3)
            
            # Take screenshot to debug
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
                'button:has-text("Read")',
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
                        await book_elements[0].click()
                        self.log(f"Clicked element with selector: {selector}")
                        await asyncio.sleep(2)
                        
                        # Check if we successfully navigated
                        if 'reader' in self.page.url.lower() or 'book' in self.page.url.lower():
                            self.log("Successfully selected a book!")
                            return True
                except Exception as e:
                    self.log(f"Failed with selector {selector}: {e}")
                    continue
            
            # If no specific books found, try clicking on any large button or link
            self.log("Trying alternative book selection method...")
            try:
                buttons = await self.page.query_selector_all('button, a[role="button"], div[role="button"]')
                if buttons:
                    for btn in buttons[:3]:
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
            return False
    
    async def start_reading(self):
        """Start reading the selected book"""
        self.log("Starting to read...")
        self.is_running = True
        
        try:
            # If already on reader page, skip button clicking
            if 'reader' not in self.page.url.lower():
                # Look for "Read" or "Start Reading" button
                read_buttons = [
                    'button:has-text("Read")',
                    'button:has-text("Start Reading")',
                    'button:has-text("Open Book")',
                    '.read-button',
                    '[data-testid="read-button"]'
                ]
                
                for selector in read_buttons:
                    try:
                        await self.page.click(selector, timeout=3000)
                        self.log("Clicked read button")
                        await asyncio.sleep(3)
                        break
                    except:
                        continue
            
            # Main reading loop
            while self.is_running:
                await self.reading_cycle()
                
        except Exception as e:
            self.log(f"ERROR in reading loop: {str(e)}", "ERROR")
            self.is_running = False
    
    async def reading_cycle(self):
        """One cycle of reading: check for questions, flip page, wait"""
        try:
            # Check for questions first
            question_detected = await self.check_and_answer_questions()
            
            if not question_detected:
                # No question, flip the page
                await self.flip_page()
                self.pages_read += 1
                self.log(f"Pages read: {self.pages_read}")
            
            # Wait for the configured interval before next action
            self.log(f"Waiting {self.page_flip_interval} seconds before next action...")
            await asyncio.sleep(self.page_flip_interval)
            
        except Exception as e:
            self.log(f"ERROR in reading cycle: {str(e)}", "ERROR")
    
    async def check_and_answer_questions(self) -> bool:
        """Check for questions and answer them if found"""
        try:
            # Skip SVG clicking for now - it causes website instability
            # First, check for hidden cloze SVG elements and click them to reveal
            """
            cloze_svg = await self.page.query_selector('g.cloze-assessment-pending, svg rect[data-id], g[class*="cloze"]')
            if cloze_svg:
                self.log("Found hidden cloze element (SVG), clicking to reveal...")
                await cloze_svg.click()
                await asyncio.sleep(2)  # Increased wait time for question to fully appear
            """
            
            # Look for multiple choice questions
            mc_question = await self.detect_multiple_choice_question()
            if mc_question:
                self.log("Multiple choice question detected!")
                if self.config.get('auto_answer_questions', True):
                    await self.answer_multiple_choice_question(mc_question)
                return True
            
            # Look for fill-in-the-blank (cloze) questions
            cloze_question = await self.detect_cloze_question()
            if cloze_question:
                self.log("Fill-in-the-blank (Cloze) question detected!")
                if self.config.get('auto_answer_questions', True):
                    await self.answer_cloze_question(cloze_question)
                return True
            
            # Look for short answer questions
            short_answer = await self.detect_short_answer_question()
            if short_answer:
                self.log("Short answer question detected!")
                if self.config.get('auto_answer_questions', True):
                    await self.answer_short_answer_question(short_answer)
                return True
                
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
                '.quiz-question'
            ]
            
            for selector in mc_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    # Get question text
                    question_text = await element.inner_text()
                    
                    # Get options (usually radio buttons or clickable options)
                    options = await element.query_selector_all(
                        'input[type="radio"], .option, .choice, label'
                    )
                    
                    if len(options) >= 2:  # At least 2 options
                        option_texts = []
                        for opt in options:
                            text = await opt.inner_text()
                            option_texts.append(text.strip())
                        
                        return {
                            'element': element,
                            'question': question_text,
                            'options': option_texts,
                            'option_elements': options
                        }
                        
        except Exception as e:
            pass
        
        return None
    
    async def detect_cloze_question(self) -> Optional[Dict]:
        """Detect fill-in-the-blank (cloze) questions"""
        try:
            # Look for input fields that might be cloze questions
            text_inputs = await self.page.query_selector_all('input[type="text"]:not([readonly]), input.cloze-answer')
            
            if len(text_inputs) > 0:
                # Get page context as question text
                context = await self.page.evaluate('''() => {
                    const inputs = document.querySelectorAll('input[type="text"]:not([readonly])');
                    let text = '';
                    
                    // Try to find question in common containers
                    const parent = inputs.length > 0 ? inputs[0].closest('.question, .cloze, .assessment, .fill-blank, form, [class*="question"], [class*="cloze"]') : null;
                    
                    if (parent) {
                        text = parent.innerText;
                    } else if (inputs.length > 0) {
                        // If no specific context, get surrounding text
                        const container = inputs[0].closest('div');
                        if (container) {
                            text = container.innerText;
                        }
                    }
                    
                    // Fallback: get visible page text
                    if (!text || text.length < 10) {
                        text = document.body.innerText.substring(0, 500);
                    }
                    
                    return text;
                }''')
                
                if text_inputs or context:  # Return if we found inputs OR context
                    return {
                        'inputs': text_inputs,
                        'context': context
                    }
                    
        except Exception as e:
            pass
        
        return None
    
    async def detect_short_answer_question(self) -> Optional[Dict]:
        """Detect short answer questions"""
        try:
            textarea = await self.page.query_selector('textarea.question-input, .short-answer, [data-testid="short-answer"]')
            if textarea:
                question_text = await self.page.evaluate('''() => {
                    const textarea = document.querySelector('textarea');
                    const parent = textarea.closest('.question, .assessment');
                    return parent ? parent.innerText : '';
                }''')
                
                return {
                    'textarea': textarea,
                    'question': question_text
                }
                
        except Exception as e:
            pass
        
        return None
    
    async def answer_multiple_choice_question(self, question_data: Dict):
        """Answer a multiple choice question using AI"""
        try:
            question_text = question_data['question']
            options = question_data['options']
            
            self.log(f"Question: {question_text[:100]}...")
            self.log(f"Options: {options}")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"question_{self.question_answered_count + 1}.png"
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

            # Look for submit button and click
            submit_buttons = [
                'button:has-text("Submit")',
                'button:has-text("Answer")',
                'button:has-text("Check")',
                '.submit-button',
                '[data-testid="submit"]'
            ]

            for selector in submit_buttons:
                try:
                    await self.page.click(selector, timeout=2000)
                    self.log("Submitted answer")
                    break
                except:
                    continue
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering MC question: {str(e)}", "ERROR")
    
    async def answer_cloze_question(self, question_data: Dict):
        """Answer a fill-in-the-blank question using AI"""
        try:
            context = question_data['context']
            inputs = question_data['inputs']
            
            self.log(f"Cloze context: {context[:100]}...")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"cloze_{self.question_answered_count + 1}.png"
                await self.page.screenshot(path=screenshot_path)
                self.log(f"Screenshot saved: {screenshot_path}")
            
            # Get answers from AI for each blank
            for i, input_field in enumerate(inputs):
                # Get surrounding sentence for context
                answer = await self.get_ai_cloze_answer(context, i + 1)
                self.log(f"AI answer for blank {i + 1}: {answer}")
                
                await input_field.fill(answer)
                await asyncio.sleep(0.5)
                # Click on the answer field to reveal submit button
                await input_field.click()
                await asyncio.sleep(0.5)
            
            # Submit the answer
            submit_buttons = [
                'button:has-text("Submit")',
                'button:has-text("Check")',
                '.submit-button'
            ]
            
            for selector in submit_buttons:
                try:
                    await self.page.click(selector, timeout=2000)
                    self.log("Submitted cloze answer")
                    break
                except:
                    continue
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering cloze question: {str(e)}", "ERROR")
    
    async def answer_short_answer_question(self, question_data: Dict):
        """Answer a short answer question using AI"""
        try:
            question_text = question_data['question']
            textarea = question_data['textarea']
            
            self.log(f"Short answer question: {question_text[:100]}...")
            
            # Take screenshot if enabled
            if self.config.get('screenshot_on_question', True):
                screenshot_path = f"short_answer_{self.question_answered_count + 1}.png"
                await self.page.screenshot(path=screenshot_path)
                self.log(f"Screenshot saved: {screenshot_path}")
            
            # Get answer from AI
            answer = await self.get_ai_short_answer(question_text)
            self.log(f"AI generated answer: {answer[:100]}...")
            
            await textarea.fill(answer)
            
            # Submit
            submit_buttons = [
                'button:has-text("Submit")',
                'button:has-text("Save")',
                '.submit-button'
            ]
            
            for selector in submit_buttons:
                try:
                    await self.page.click(selector, timeout=2000)
                    self.log("Submitted short answer")
                    break
                except:
                    continue
            
            self.question_answered_count += 1
            await asyncio.sleep(2)
            
        except Exception as e:
            self.log(f"ERROR answering short answer: {str(e)}", "ERROR")
    
    async def get_ai_answer(self, question: str, options: List[str]) -> str:
        """Get AI answer for multiple choice question"""
        try:
            if not openai.api_key:
                self.log("WARNING: No OpenAI API key, selecting first option", "WARNING")
                return options[0] if options else ""
            
            prompt = f"""Question: {question}

Options:
{chr(10).join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])}

Select the best answer. Respond with just the letter (A, B, C, or D) or the full answer text."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers reading comprehension questions accurately."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            self.log(f"ERROR getting AI answer: {str(e)}", "ERROR")
            return options[0] if options else ""
    
    async def get_ai_cloze_answer(self, context: str, blank_number: int) -> str:
        """Get AI answer for fill-in-the-blank question"""
        try:
            if not openai.api_key:
                self.log("WARNING: No OpenAI API key, returning 'answer'", "WARNING")
                return "answer"
            
            prompt = f"""Context: {context}

This is a fill-in-the-blank question. What word should go in blank #{blank_number}? 
Respond with just the single word that fits best."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that fills in blanks accurately based on context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            self.log(f"ERROR getting AI cloze answer: {str(e)}", "ERROR")
            return "answer"
    
    async def get_ai_short_answer(self, question: str) -> str:
        """Get AI answer for short answer question"""
        try:
            if not openai.api_key:
                self.log("WARNING: No OpenAI API key, returning generic answer", "WARNING")
                return "Based on the reading, this is an important concept."
            
            prompt = f"""Question: {question}

Provide a brief, accurate answer (2-3 sentences) based on typical reading comprehension."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers reading comprehension questions accurately and concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            self.log(f"ERROR getting AI short answer: {str(e)}", "ERROR")
            return "Based on the reading, this is an important concept."
    
    async def flip_page(self):
        """Flip to the next page"""
        try:
            # Common page navigation selectors
            next_page_selectors = [
                'button:has-text("Next")',
                'button:has-text(">")',
                '.next-page',
                '[data-testid="next-page"]',
                '.page-forward',
                'button[aria-label="Next page"]',
                '.arrow-right',
                '.pagination-next'
            ]
            
            for selector in next_page_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    self.log("Flipped to next page")
                    await asyncio.sleep(1)
                    return
                except:
                    continue
            
            # Try keyboard navigation
            await self.page.keyboard.press('ArrowRight')
            self.log("Used keyboard to flip page")
            await asyncio.sleep(1)
            
        except Exception as e:
            self.log(f"ERROR flipping page: {str(e)}", "ERROR")
    
    async def stop(self):
        """Stop the bot and close browser"""
        self.is_running = False
        self.log("Stopping bot...")
        
        if self.browser:
            await self.browser.close()
            self.log("Browser closed")
        
        self.log(f"Session Summary:")
        self.log(f"  - Pages read: {self.pages_read}")
        self.log(f"  - Questions answered: {self.question_answered_count}")
        self.log(f"  - Book: {self.current_book or 'N/A'}")
    
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
                self.log("Failed to login", "ERROR")
                
        except KeyboardInterrupt:
            self.log("Bot stopped by user")
        except Exception as e:
            self.log(f"FATAL ERROR: {str(e)}", "ERROR")
        finally:
            await self.stop()


async def main():
    bot = LightSailBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
