#!/usr/bin/env python3
"""
LightSail Bot - Anti-AFK Detection
Simulates user activity to prevent AFK detection when switching programs
"""

import asyncio
import json
import time
import os
import webbrowser
import random
import requests
from datetime import datetime
from typing import Optional, List
from playwright.async_api import async_playwright, Page, Browser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from collections import deque

# Config
FLIP_INTERVAL = 40
HEADLESS = False
OPENROUTER_API_KEY = "YOUR API HERE"
OPENROUTER_MODEL = "qwen/qwen-2.5-coder-32b-instruct:free"
DASHBOARD_PORT = 8765

# State
stats = {'status': 'starting', 'book': '', 'pages_read': 0, 'total_flips': 0,
         'questions_detected': 0, 'questions_answered': 0, 'start_time': None, 'session_duration': '0m 0s'}
logs = deque(maxlen=50)
lock = threading.Lock()

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    with lock:
        logs.append({'time': ts, 'level': level, 'message': msg})
    print(f"[{ts}] [{level}] {msg}")

def update(**kwargs):
    global stats
    with lock:
        for k, v in kwargs.items():
            stats[k] = v
        if stats['start_time'] is None:
            stats['start_time'] = datetime.now().isoformat()
        start = datetime.fromisoformat(stats['start_time'])
        diff = datetime.now() - start
        stats['session_duration'] = f"{int(diff.total_seconds() // 60)}m {int(diff.total_seconds() % 60)}s"

# Dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>LightSail Bot</title><meta http-equiv="refresh" content="2">
<style>
body{font-family:Arial,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);color:#eee;padding:30px}
h1{color:#4f46e5}.header{display:flex;justify-content:space-between;margin-bottom:30px}
.status{padding:8px 20px;border-radius:25px;font-weight:bold}.status-running{background:#10b981}.status-stopped{background:#666}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:30px}
.card{background:rgba(22,33,62,0.8);padding:20px;border-radius:12px}
.card-title{color:#94a3b8;font-size:12px;text-transform:uppercase}
.card-value{font-size:36px;font-weight:bold;color:#4f46e5;margin-top:8px}
.log-container{background:rgba(15,15,35,0.9);border-radius:12px;padding:20px;height:400px;overflow-y:auto;font-family:monospace;font-size:13px}
.log-entry{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;gap:12px}
.log-time{color:#64748b;min-width:65px}.log-info{color:#10b981}.log-warning{color:#f59e0b}.log-error{color:#ef4444}
</style></head>
<body>
<div class="header"><h1>📚 LightSail Bot (Anti-AFK)</h1><span class="status status-running" id="status">Running</span></div>
<div class="grid">
<div class="card"><div class="card-title">Book</div><div class="card-value" id="book" style="font-size:18px">-</div></div>
<div class="card"><div class="card-title">Pages</div><div class="card-value" id="pages">0</div></div>
<div class="card"><div class="card-title">Flips</div><div class="card-value" id="flips">0</div></div>
<div class="card"><div class="card-title">Duration</div><div class="card-value" id="duration" style="font-size:24px">0m 0s</div></div>
<div class="card"><div class="card-title">Questions</div><div class="card-value" id="questions">0</div></div>
<div class="card"><div class="card-title">Answered</div><div class="card-value" id="answered">0</div></div>
</div>
<h3 style="margin-bottom:15px">📋 Activity Log</h3>
<div class="log-container" id="log"></div>
<script>
let scrolled=false;
document.getElementById('log').addEventListener('scroll',e=>scrolled=e.target.scrollHeight-e.target.scrollTop-e.target.clientHeight>30);
function update(){
    fetch('/api/stats').then(r=>r.json()).then(d=>{
        document.getElementById('book').textContent=d.book||'-';
        document.getElementById('pages').textContent=d.pages_read;
        document.getElementById('flips').textContent=d.total_flips;
        document.getElementById('duration').textContent=d.session_duration;
        document.getElementById('questions').textContent=d.questions_detected;
        document.getElementById('answered').textContent=d.questions_answered;
        document.getElementById('status').textContent=d.status;
        document.getElementById('status').className='status status-'+d.status;
    });
    fetch('/api/logs').then(r=>r.json()).then(logs=>{
        const c=document.getElementById('log');
        const atBottom=!scrolled;
        c.innerHTML=logs.map(l=>'<div class="log-entry"><span class="log-time">'+l.time+'</span><span class="log-'+l.level.toLowerCase()+'">'+l.level+'</span><span>'+l.message+'</span></div>').join('');
        if(atBottom)c.scrollTop=c.scrollHeight;
    });
}
setInterval(update,2000);
update();
</script>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with lock:
                self.wfile.write(json.dumps(stats).encode())
        elif self.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with lock:
                self.wfile.write(json.dumps(list(logs)).encode())
        else:
            self.send_response(404)
    def log_message(self, format, *args):
        pass

def run_dashboard():
    server = HTTPServer(('127.0.0.1', DASHBOARD_PORT), Handler)
    log(f"Dashboard started at http://127.0.0.1:{DASHBOARD_PORT}")
    server.serve_forever()

# AI Answerer
async def get_ai_answer(question, options):
    if not OPENROUTER_API_KEY:
        return 0
    try:
        opts = "\n".join([f"{i+1}. {o}" for i, o in enumerate(options)])
        prompt = f"Question: {question}\n\nOptions:\n{opts}\n\nReply with ONLY the NUMBER (1, 2, 3, or 4)."
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 5},
            timeout=20)
        if r.ok:
            ans = r.json()['choices'][0]['message']['content'].strip()
            log(f"AI: '{ans}'", "INFO")
            for i in range(len(options)):
                if str(i+1) in ans:
                    log(f"Selected: {options[i]}", "INFO")
                    return i
            for i, o in enumerate(options):
                if o.lower() in ans.lower():
                    return i
        return 0
    except Exception as e:
        log(f"AI error: {e}", "ERROR")
        return 0

# Bot
class Bot:
    def __init__(self):
        self.browser = None
        self.page = None
        self.running = False
        self.pages = 0
        self.flips = 0
        self.book = ""
        self.q_detected = 0
        self.q_answered = 0
        self.books_completed = 0
        self.ai_enabled = bool(OPENROUTER_API_KEY)
        self.forward_only = self.ai_enabled
        self.afk_task = None
    
    async def start_afk_prevention(self):
        """Start background task to prevent AFK detection"""
        log("Starting AFK prevention...", "INFO")
        
        # Inject JavaScript to override visibility API
        await self.page.add_init_script('''() => {
            // Override Page Visibility API
            Object.defineProperty(document, 'hidden', {
                get: () => false
            });
            Object.defineProperty(document, 'visibilityState', {
                get: () => 'visible'
            });
            
            // Prevent visibility change events
            const originalAddEventListener = document.addEventListener;
            document.addEventListener = function(type, listener, options) {
                if (type === 'visibilitychange' || type === 'blur' || type === 'focus') {
                    // Don't register these listeners
                    return;
                }
                return originalAddEventListener.call(this, type, listener, options);
            };
            
            // Simulate occasional mouse movement
            setInterval(() => {
                const event = new MouseEvent('mousemove', {
                    bubbles: true,
                    cancelable: true,
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            }, 5000);  // Every 5 seconds
        }''')
        
        # Start background activity simulation
        self.afk_task = asyncio.create_task(self._simulate_activity())
    
    async def _simulate_activity(self):
        """Simulate user activity in background"""
        while self.running:
            try:
                await asyncio.sleep(10)  # Every 10 seconds
                
                # Small mouse movement
                await self.page.mouse.move(
                    random.randint(100, 200),
                    random.randint(100, 200)
                )
                
                # Occasional tiny scroll
                if random.random() < 0.3:  # 30% chance
                    scroll_amount = random.randint(-10, 10)
                    await self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                
            except Exception as e:
                log(f"AFK sim error: {e}", "DEBUG")
    
    async def start(self):
        log("Starting browser...")
        pw = await async_playwright().start()
        self.browser = await pw.chromium.launch(headless=HEADLESS, args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows'
        ])
        ctx = await self.browser.new_context(viewport={'width': 1366, 'height': 768})
        if os.path.exists("storage_state.json"):
            try:
                with open("storage_state.json") as f:
                    s = json.load(f)
                if s.get('cookies'):
                    await ctx.add_cookies(s['cookies'])
                    log("Loaded session")
            except:
                pass
        self.page = await ctx.new_page()
        await self.page.goto("https://lightsailed.com/school/literacy/", timeout=60000)
        await asyncio.sleep(5)
        
        # Start AFK prevention
        await self.start_afk_prevention()
        
        log("Browser ready with AFK prevention")
        log(f"AI Enabled: {self.ai_enabled}", "INFO")
        log(f"Forward Only Mode: {self.forward_only}", "INFO")
    
    async def wait_login(self):
        log("Please log in (click Google)")
        for i in range(300):
            try:
                url = self.page.url.lower()
                lib = await self.page.query_selector('a:has-text("Library"), a:has-text("Home")')
                if lib and 'login' not in url:
                    log("Login detected!")
                    await self.page.context.storage_state(path="storage_state.json")
                    return True
            except:
                pass
            await asyncio.sleep(1)
            if (i+1) % 30 == 0:
                log(f"Waiting... {i+1}s")
        return False
    
    async def select_book(self, auto: bool = False) -> bool:
        log("Searching for Power Text books..." if not auto else "Selecting next book...")
        await asyncio.sleep(3)
        await self.page.screenshot(path="book_selection.png")

        # Keywords that indicate an assignment (not a book)
        assignment_keywords = [
            'retake', 'clozes', 'assignment', 'quiz', 'test',
            'start', 'resume', 'submit', 'retry', 'current assignment'
        ]
        
        # Section keywords that indicate assignment area
        assignment_sections = [
            'current assignment', 'assignments', 'to-do', 'todo'
        ]

        # Find Power Text books first (most reliable - they have the Power Text icon)
        imgs = await self.page.query_selector_all('img[src*="power-text.svg"]')
        for img in imgs[:3]:
            try:
                # Get the parent container
                container = await img.evaluate_handle('''el => {
                    // Go up to find the book card or button
                    let p = el;
                    for (let i = 0; i < 5; i++) {
                        if (p.closest && p.closest('.book-card, .library-item, [class*="book" i]')) {
                            return p.closest('.book-card, .library-item, [class*="book" i]');
                        }
                        p = p.parentElement;
                        if (!p) break;
                    }
                    return el.closest('button') || el.parentElement;
                }''')
                
                if container:
                    # Check if this is in an assignment section
                    container_text = await container.evaluate('el => el.innerText')
                    is_in_assignment_section = any(kw in container_text.lower() for kw in assignment_sections)
                    
                    if is_in_assignment_section:
                        log(f"Skipping - in assignment section", "INFO")
                        continue
                    
                    # Get button and verify not an assignment
                    btn = await container.query_selector('button.btn.w-100.border-0.image-wrapper')
                    if btn:
                        btn_text = await btn.evaluate('el => el.innerText')
                        is_assignment = any(kw in btn_text.lower() for kw in assignment_keywords)

                        if is_assignment:
                            log(f"Skipping assignment: {btn_text[:50]}", "INFO")
                            continue

                        title = await btn.evaluate('el => el.innerText')
                        log(f"Found Power Text: {title[:50]}")
                        await btn.click()
                        await asyncio.sleep(3)
                        await self.click_read()
                        self.book = title[:50]
                        update(book=self.book)
                        return True
            except Exception as e:
                log(f"Power Text select error: {e}", "DEBUG")
                continue

        # Fallback: Look for books in library section (not assignments)
        # First, try to find the library section specifically
        library_sections = await self.page.query_selector_all('[class*="library" i], [class*="book" i]:not([class*="assignment" i])')
        
        for section in library_sections:
            try:
                # Check if this section is an assignment area
                section_text = await section.evaluate('el => el.innerText')
                if any(kw in section_text.lower() for kw in assignment_sections):
                    continue
                
                # Find book buttons in this section
                books = await section.query_selector_all('button.btn.w-100.border-0.image-wrapper')
                for book_btn in books[:5]:
                    try:
                        title = await book_btn.evaluate('el => el.innerText')
                        
                        # Skip if this was the last book
                        if title[:50] == self.book:
                            continue
                        
                        # Skip assignment buttons
                        is_assignment = any(kw in title.lower() for kw in assignment_keywords)
                        if is_assignment:
                            log(f"Skipping assignment: {title[:50]}", "INFO")
                            continue
                        
                        # Skip if too short (likely not a real book title)
                        if len(title) < 10:
                            continue
                        
                        # Verify has book image (not just text)
                        has_book_img = await book_btn.evaluate('''el => {
                            return el.querySelector('img[src*=".jpg"], img[src*=".png"], img[alt*="book" i]') !== null;
                        }''')
                        
                        if not has_book_img:
                            continue
                        
                        await book_btn.click()
                        await asyncio.sleep(3)
                        await self.click_read()
                        self.book = title[:50]
                        update(book=self.book)
                        log(f"Selected: {self.book}")
                        return True
                    except:
                        continue
            except:
                continue
        
        # Last resort: any book button that's clearly not an assignment
        books = await self.page.query_selector_all('button.btn.w-100.border-0.image-wrapper')
        if books:
            for book_btn in books[:20]:  # Check more buttons
                try:
                    title = await book_btn.evaluate('el => el.innerText')
                    
                    # Multiple checks to ensure it's a book
                    is_assignment = any(kw in title.lower() for kw in assignment_keywords)
                    if is_assignment:
                        log(f"Skipping assignment: {title[:50]}", "INFO")
                        continue
                    
                    if len(title) < 15:  # Real book titles are usually longer
                        continue
                    
                    # Check parent context
                    parent = await book_btn.evaluate_handle('el => el.parentElement')
                    if parent:
                        parent_text = await parent.evaluate('el => el.innerText')
                        if any(kw in parent_text.lower() for kw in assignment_sections):
                            log(f"Skipping - parent is assignment section", "INFO")
                            continue
                    
                    await book_btn.click()
                    await asyncio.sleep(3)
                    await self.click_read()
                    self.book = title[:50]
                    update(book=self.book)
                    log(f"Selected: {self.book}")
                    return True
                except:
                    continue
        
        log("No suitable books found", "ERROR")
        return False
    
    async def click_read(self):
        """Click the Read Book button to enter the book"""
        try:
            log("Attempting to click Read Book button...", "INFO")
            
            # Already on reader page
            if 'reader' in self.page.url.lower():
                log("Already on reader page", "INFO")
                return True
            
            # Take screenshot to see what's on page
            await self.page.screenshot(path="read_button_check.png")
            log("Screenshot saved: read_button_check.png", "INFO")
            
            log(f"Page URL: {self.page.url}", "INFO")
            
            # Method 1: Find button by class (btn btn-primary) and check text
            log("Looking for Read Book button by class...", "INFO")
            btns = await self.page.query_selector_all('button.btn.btn-primary')
            log(f"Found {len(btns)} btn-primary button(s)", "INFO")
            
            for i, btn in enumerate(btns):
                # Get full text content
                text = await btn.evaluate('el => el.innerText')
                log(f"Button {i} text: '{text}'", "INFO")
                
                # Check if this is the Read Book button
                if 'Read Book' in text or 'Read' in text:
                    log(f"Found Read Book button! Text: '{text}'", "INFO")
                    
                    try:
                        # Try clicking with bounding box (more reliable)
                        box = await btn.bounding_box()
                        if box:
                            log(f"Button position: x={box['x']}, y={box['y']}, w={box['width']}, h={box['height']}", "INFO")
                            await self.page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                            log("Clicked with mouse!", "INFO")
                            await asyncio.sleep(3)
                            
                            # Check if we're now on reader page
                            if 'reader' in self.page.url.lower():
                                log("Successfully entered reader!", "INFO")
                                return True
                            else:
                                log(f"Click worked but URL is: {self.page.url}", "WARNING")
                    except Exception as e:
                        log(f"Mouse click failed: {e}", "ERROR")
                    
                    # Fallback: try regular click
                    try:
                        await btn.click()
                        log("Regular click worked!", "INFO")
                        await asyncio.sleep(3)
                        return True
                    except Exception as e:
                        log(f"Regular click also failed: {e}", "ERROR")
            
            # Method 2: Try XPath for buttons containing "Read"
            log("Trying XPath selector...", "DEBUG")
            try:
                from playwright.async_api import async_playwright
                btns = await self.page.query_selector_all('xpath=//button[contains(text(), "Read")]')
                log(f"XPath found {len(btns)} button(s)", "INFO")
                
                if btns:
                    box = await btns[0].bounding_box()
                    if box:
                        await self.page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                        await asyncio.sleep(3)
                        log("XPath click successful!", "INFO")
                        return True
            except Exception as e:
                log(f"XPath failed: {e}", "DEBUG")
            
            # Method 3: Try clicking any button with "Read" in class or text
            log("Trying alternative selectors...", "DEBUG")
            alt_selectors = [
                'button[class*="primary"]',
                '.btn-primary',
                'button:has-text("Read")',
            ]
            
            for selector in alt_selectors:
                try:
                    btns = await self.page.query_selector_all(selector)
                    if btns:
                        log(f"Found {len(btns)} with selector: {selector}", "INFO")
                        for btn in btns:
                            text = await btn.evaluate('el => el.innerText')
                            if 'Read' in text:
                                box = await btn.bounding_box()
                                if box:
                                    await self.page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                                    await asyncio.sleep(3)
                                    log(f"Alternative click worked!", "INFO")
                                    return True
                except:
                    continue
            
            # Method 4: Keyboard fallback
            log("Trying Enter key as last resort...", "INFO")
            await self.page.keyboard.press('Tab')  # Focus first element
            await asyncio.sleep(0.5)
            await self.page.keyboard.press('Enter')
            await asyncio.sleep(3)
            
            if 'reader' in self.page.url.lower():
                log("Keyboard worked!", "INFO")
                return True
            
            log("Could not click Read Book button", "ERROR")
            log(f"Final URL: {self.page.url}", "ERROR")
            return False
            
        except Exception as e:
            log(f"Click read error: {e}", "ERROR")
            return False
    
    async def check_book_completed(self) -> bool:
        """Check if book is completed by checking progress and next button"""
        try:
            # Check 1: Progress at 100%
            progress_100 = False
            try:
                progress_text = await self.page.query_selector('span.reader-progress-text')
                if progress_text:
                    text = await progress_text.evaluate('el => el.innerText.trim()')
                    if text == '100%':
                        progress_100 = True
                        log(f"Progress at 100%!", "INFO")
            except:
                pass
            
            # Check 2: Next page button is gone
            next_button_gone = False
            try:
                next_btn = await self.page.query_selector('button[aria-label="Go To Next Page"]')
                if not next_btn:
                    next_button_gone = True
                    log("Next page button not found!", "INFO")
            except:
                pass
            
            # Book is complete if progress is 100% AND next button is gone
            if progress_100 and next_button_gone:
                log("Book completion detected! (100% + no next button)", "WARNING")
                return await self.exit_and_select_new_book()
            
            return False
            
        except Exception as e:
            log(f"Book completion check error: {e}", "ERROR")
            return False
    
    async def exit_and_select_new_book(self) -> bool:
        """Exit current book and select a new one"""
        try:
            self.books_completed += 1
            log(f"Books completed: {self.books_completed}", "INFO")
            
            # Step 1: Click exit button
            log("Clicking exit button...", "INFO")
            exit_btn = await self.page.query_selector('button.reader-exit-btn')
            if exit_btn:
                await exit_btn.click()
                await asyncio.sleep(2)
                log("Exit button clicked", "INFO")
            else:
                log("Exit button not found, trying alternative...", "WARNING")
                # Try alternative exit selectors
                alt_exit = await self.page.query_selector('button:has-text("Exit"), button:has-text("Close"), .exit-button')
                if alt_exit:
                    await alt_exit.click()
                    await asyncio.sleep(2)
            
            # Step 2: Click confirmation "Yes, I want to exit"
            log("Clicking confirm exit...", "INFO")
            confirm_btn = await self.page.query_selector('button:has-text("Yes, I want to exit")')
            if confirm_btn:
                await confirm_btn.click()
                await asyncio.sleep(3)
                log("Exit confirmed", "INFO")
            else:
                # Try alternative confirmation
                confirm_btn = await self.page.query_selector('button.btn-primary:has-text("Exit"), button:has-text("Yes")')
                if confirm_btn:
                    await confirm_btn.click()
                    await asyncio.sleep(3)
            
            # Wait for library to load
            await asyncio.sleep(2)
            
            # Step 3: Select new Power Text book
            log("Selecting new Power Text book...", "INFO")
            if await self.select_book(auto=True):
                log(f"Auto-selected new book: {self.book}", "INFO")
                return True
            else:
                log("Could not select new book", "ERROR")
                return False
                
        except Exception as e:
            log(f"Exit and select error: {e}", "ERROR")
            # Fallback: go to library URL directly
            try:
                await self.page.goto("https://lightsailed.com/school/literacy/")
                await asyncio.sleep(3)
                if await self.select_book(auto=True):
                    return True
            except:
                pass
            return False
    
    async def check_questions(self):
        try:
            svgs = await self.page.query_selector_all('g.cloze-assessment-pending')
            visible = []
            for svg in svgs:
                try:
                    v = await svg.evaluate('''el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    }''')
                    if v:
                        visible.append(svg)
                except:
                    continue
            if visible:
                log(f"Found {len(visible)} cloze question(s)!", "WARNING")
                await self.answer_cloze(visible)
                return True
            
            radios = await self.page.query_selector_all('input[type="radio"]')
            if len(radios) >= 2:
                log("Multiple choice detected!", "WARNING")
                await self.answer_mc(radios)
                return True
        except Exception as e:
            log(f"Question error: {e}", "ERROR")
        return False
    
    async def answer_cloze(self, svgs):
        try:
            self.q_detected += 1
            update(questions_detected=self.q_detected)
            
            for svg in svgs[:1]:
                await svg.click()
                log("Clicked cloze SVG", "INFO")
                await asyncio.sleep(3)
                
                await self.page.screenshot(path=f"q_{self.q_detected}.png")
                log(f"Screenshot: q_{self.q_detected}.png", "INFO")
                
                all_buttons = await self.page.query_selector_all('button')
                log(f"Total buttons: {len(all_buttons)}", "INFO")
                
                button_info = []
                for i, btn in enumerate(all_buttons):
                    txt = await btn.evaluate('el => el.innerText.trim()')
                    cls = await btn.evaluate('el => el.className')
                    visible = await btn.evaluate('el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; }')
                    if txt and visible:
                        button_info.append({'index': i, 'text': txt, 'class': cls})
                
                log(f"Buttons: {button_info}", "INFO")
                
                answer_opts = []
                for btn in button_info:
                    t = btn['text']
                    if t.lower() in ['submit', 'check', 'answer', 'continue', 'ok', 'cancel', 'close', 'next', 'back', 'clear']:
                        continue
                    if len(t) < 2 or len(t) > 40:
                        continue
                    if 'icon' in btn['class'].lower() or 'arrow' in btn['class'].lower():
                        continue
                    answer_opts.append(t)
                
                log(f"Options: {answer_opts}", "INFO")
                
                if len(answer_opts) >= 2:
                    ctx = await self.page.evaluate('''() => {
                        const svg = document.querySelector('g.cloze-assessment-pending');
                        if (svg) {
                            let p = svg.parentElement;
                            while (p && p.tagName !== 'svg') p = p.parentElement;
                            return p ? p.parentElement.innerText.substring(0, 500) : '';
                        }
                        return '';
                    }''')
                    
                    sel = await get_ai_answer(ctx, answer_opts)
                    log(f"AI chose: {answer_opts[sel]}", "INFO")
                    
                    for btn in all_buttons:
                        txt = await btn.evaluate('el => el.innerText.trim()')
                        if txt == answer_opts[sel]:
                            await btn.click()
                            log(f"Clicked: {txt}", "INFO")
                            break
                    else:
                        for btn in all_buttons:
                            txt = await btn.evaluate('el => el.innerText.trim()')
                            if txt == answer_opts[0]:
                                await btn.click()
                                log(f"Clicked (fallback): {txt}", "INFO")
                                break
                
                await asyncio.sleep(1)
            
            await self.submit()
            self.q_answered += 1
            update(questions_answered=self.q_answered)
            
        except Exception as e:
            log(f"Cloze error: {e}", "ERROR")
    
    async def answer_mc(self, radios):
        try:
            self.q_detected += 1
            update(questions_detected=self.q_detected)
            q = await self.page.evaluate('''() => {
                const r = document.querySelectorAll('input[type="radio"]');
                if (r.length) {
                    const p = r[0].closest('.question, .assessment');
                    return p ? p.innerText : '';
                }
                return '';
            }''')
            opts = []
            for radio in radios[:4]:
                lbl = await radio.evaluate_handle('el => el.closest("label")')
                if lbl:
                    t = await lbl.evaluate('el => el.innerText.trim()')
                    opts.append(t if t else f"Option {len(opts)+1}")
                else:
                    opts.append(f"Option {len(opts)+1}")
            log(f"Options: {opts}", "INFO")
            sel = await get_ai_answer(q, opts)
            if sel < len(radios):
                await radios[sel].click()
                log(f"Selected: {opts[sel]}", "INFO")
            await self.submit()
            self.q_answered += 1
            update(questions_answered=self.q_answered)
        except Exception as e:
            log(f"MC error: {e}", "ERROR")
    
    async def submit(self):
        btns = await self.page.query_selector_all('button:has-text("Submit"), button:has-text("Check"), button:has-text("Answer")')
        if btns:
            await btns[0].click()
            log("Submitted", "INFO")
            await asyncio.sleep(2)
    
    async def flip(self, forward=True):
        if self.forward_only:
            forward = True
        
        try:
            if forward:
                sel = 'button[aria-label="Go To Next Page"]'
            else:
                sel = 'button[aria-label="Go To Previous Page"]'
            
            btn = await self.page.query_selector(sel)
            if btn:
                await btn.click()
                direction = "forward" if forward else "backward"
                log(f"Flipped {direction}")
                await asyncio.sleep(1)
                return True
            
            key = 'ArrowRight' if forward else 'ArrowLeft'
            await self.page.keyboard.press(key)
            log(f"Flipped with {key}")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            log(f"Flip error: {e}", "ERROR")
            return False
    
    async def run(self):
        try:
            await self.start()
            if not await self.wait_login():
                return
            if not await self.select_book():
                log("Select a book manually", "WARNING")
                await asyncio.sleep(60)
            
            self.running = True
            update(status='running')
            start = time.time()
            consecutive_no_progress = 0
            
            log("=" * 50)
            log("READING STARTED")
            log(f"AI Enabled: {self.ai_enabled}")
            log(f"Forward Only: {self.forward_only}")
            log(f"AFK Prevention: Active")
            log("=" * 50)
            
            while self.running:
                try:
                    if await self.check_book_completed():
                        log("Continuing with new book...", "INFO")
                        await asyncio.sleep(5)
                        continue
                    
                    if await self.check_questions():
                        await asyncio.sleep(5)
                        continue
                    
                    if await self.flip(forward=True):
                        self.pages += 1
                        self.flips += 1
                        update(pages=self.pages, flips=self.flips)
                        elapsed = int(time.time() - start)
                        log(f"Pages: {self.pages} | Flips: {self.flips} | Time: {elapsed//60}m {elapsed%60}s")
                        consecutive_no_progress = 0
                    else:
                        consecutive_no_progress += 1
                        if consecutive_no_progress > 3:
                            log("No progress, checking completion...", "WARNING")
                            if await self.check_book_completed():
                                continue
                            consecutive_no_progress = 0
                    
                    wait = FLIP_INTERVAL + random.randint(-5, 5)
                    for _ in range(wait):
                        if not self.running:
                            break
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    log(f"Loop error: {e}", "ERROR")
                    await asyncio.sleep(5)
                    
        except KeyboardInterrupt:
            log("\nStopped")
        except Exception as e:
            log(f"Fatal: {e}", "ERROR")
        finally:
            await self.stop()
    
    async def stop(self):
        self.running = False
        if self.afk_task:
            self.afk_task.cancel()
        update(status='stopped')
        log("=" * 50)
        log("SESSION SUMMARY")
        log(f"Book: {self.book}")
        log(f"Pages read: {self.pages}")
        log(f"Total flips: {self.flips}")
        log(f"Books completed: {self.books_completed}")
        log(f"Questions: {self.q_detected}")
        log(f"Answered: {self.q_answered}")
        log(f"Duration: {stats['session_duration']}")
        log("=" * 50)
        if self.browser:
            await self.browser.close()

# Main
if __name__ == "__main__":
    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()
    time.sleep(1)
    try:
        webbrowser.open(f'http://127.0.0.1:{DASHBOARD_PORT}')
    except:
        pass
    asyncio.run(Bot().run())
