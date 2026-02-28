# LightSail Automation Bot - Enhanced Edition

## 🚀 Complete Features

An advanced browser automation bot for LightSail Education with AI-powered question answering, anti-AFK detection, and automatic book selection.

### ✨ Key Features

1. **AI Question Answering** - Uses OpenRouter API (Qwen model) to answer questions automatically
2. **Anti-AFK Detection** - Prevents LightSail from detecting when you switch programs
3. **Forward-Only Mode** - Only flips pages forward when AI is enabled
4. **Auto Book Completion** - Detects 100% progress and auto-selects new books
5. **Power Text Priority** - Automatically finds and selects Power Text books
6. **Real-Time Dashboard** - Web UI at http://localhost:8765
7. **Screenshot Capture** - Saves screenshots of questions for debugging

---

## 📦 Installation

### Step 1: Install Python
Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

### Step 2: Install Dependencies
```bash
cd "lightsail automation\lightsail-automation"
pip install -r requirements.txt
playwright install chromium
```

### Step 3: Configure API Key (Optional but Recommended)

**🔐 Secure Method (Recommended):**

1. Navigate to the bot folder:
   ```bash
   cd "lightsail automation\lightsail-automation"
   ```

2. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` and add your API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

4. Get a free key at: https://openrouter.ai/keys

**Why use .env?** Your API key stays private and won't be uploaded to GitHub!

---

## 🎮 Quick Start

### Option 1: Double-Click (Windows)
1. Double-click `run.bat`
2. Select option 1 (Enhanced Bot with AI)
3. Browser opens automatically
4. Log in with Google
5. Bot starts reading automatically

### Option 2: Command Line
```bash
python bot_with_dashboard.py
```

### Option 3: VS Code
1. Open folder in VS Code
2. Press F5 or run `python bot_with_dashboard.py`

---

## 🌐 Dashboard

Access the real-time dashboard at: **http://localhost:8765**

### Dashboard Shows:
- Current book title
- Pages read counter
- Total flips counter
- Session duration
- Questions detected/answered
- Real-time activity log

---

## ⚙️ Configuration

### API Key (Secure Method)
Edit `.env` file in `lightsail automation\lightsail-automation/`:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Bot Settings
Edit `bot_with_dashboard.py`:
```python
FLIP_INTERVAL = 40          # Seconds between page flips
HEADLESS = False            # Show browser window
OPENROUTER_MODEL = "qwen/qwen-2.5-coder-32b-instruct:free"
DASHBOARD_PORT = 8765       # Dashboard port
```

---

## 🔍 How It Works

### 1. Login
- Opens browser to LightSail
- Waits for manual Google login (or use credentials)
- Saves session for next time

### 2. Book Selection
- Searches for Power Text books first
- Falls back to any available book
- Takes screenshot of library

### 3. Reading Loop
- Flips pages forward every ~40 seconds
- Checks for questions every cycle
- Answers questions with AI
- Tracks progress

### 4. Question Answering
- Detects cloze (fill-in-blank) questions
- Detects multiple choice questions
- Takes screenshot
- Sends to AI for answer
- Clicks correct answer
- Submits

### 5. Book Completion
- Monitors progress percentage
- Detects when next button disappears
- Clicks exit button
- Confirms exit
- Auto-selects new book

### 6. Anti-AFK
- Overrides page visibility API
- Simulates mouse movement every 5 seconds
- Blocks blur/focus event listeners
- Prevents background timer throttling

---

## 🎯 Features Explained

### AI Question Answering
When a question is detected:
1. Takes screenshot
2. Extracts answer options
3. Sends to OpenRouter API
4. AI returns answer
5. Bot clicks matching option
6. Submits answer

### Anti-AFK Detection
Prevents LightSail from detecting AFK by:
- Making tab always appear visible
- Simulating mouse movements
- Blocking visibility change events
- Keeping background timers active

**You can switch to other programs without AFK detection!**

### Auto Book Selection
When a book is completed:
1. Detects 100% progress
2. Detects missing next button
3. Clicks exit button
4. Confirms exit dialog
5. Returns to library
6. Selects new Power Text book
7. Continues reading

### Forward-Only Mode
When AI is enabled:
- Only flips pages forward
- Never goes backward
- Maximizes reading progress
- More natural reading pattern

---

## 📊 Statistics Tracked

| Stat | Description |
|------|-------------|
| Pages Read | Number of forward page flips |
| Total Flips | All page flips (forward only when AI enabled) |
| Questions Detected | Number of questions found |
| Questions Answered | Number answered by AI |
| Books Completed | Number of books finished |
| Session Duration | Total reading time |

---

## 🐛 Troubleshooting

### Bot Won't Start
```bash
pip install -r requirements.txt --force-reinstall
playwright install chromium
```

### Login Issues
- Leave browser window visible
- Click Google sign-in button
- Wait for "Login detected!" message

### Questions Not Answered
- Check API key is valid
- Check dashboard logs for errors
- Verify question screenshots are saved

### Book Not Auto-Selecting
- Check for Power Text books in library
- Verify 100% progress detection
- Check exit button selectors

### Dashboard Not Loading
- Check port 8765 is not in use
- Try different port in config
- Access via http://127.0.0.1:8765

### AFK Detection Still Happens
- Keep browser window open (don't close)
- Don't minimize browser
- Check AFK prevention logs

---

## 📁 File Structure

```
lightsail-automation/
├── bot_with_dashboard.py    # Main bot (use this!)
├── config.py                # Configuration module
├── logger.py                # Logging module
├── dashboard.py             # Dashboard module
├── requirements.txt         # Python dependencies
├── run.bat                  # Windows launcher
├── README.md                # This file
├── storage_state.json       # Saved login session
├── progress.json            # Reading progress
├── logs/                    # Log files
│   ├── lightsail_bot.log
│   └── errors.log
├── *.png                    # Screenshots
│   ├── book_selection.png
│   ├── q_1.png
│   └── question_mc_1.png
└── exports/                 # Exported reports
```

---

## 🔐 Security Notes

- API key stored in bot file (keep private)
- Session cookies saved locally
- Screenshots saved to disk
- No data sent externally except to OpenRouter API

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**.

- Using automation may violate LightSail's Terms of Service
- Use at your own risk
- Educational institutions may detect automated behavior
- Authors not responsible for consequences

**Use responsibly and ethically.**

---

## 📄 License

MIT License - Free to use and modify

---

## 🆘 Support & Troubleshooting

### Quick Checks
1. Check dashboard logs at http://localhost:8765
2. Review log files in `logs/` directory
3. Check question screenshots
4. Verify API key is valid
5. Ensure Python 3.8+ installed

---

## ❌ Common Errors & Fixes

### Installation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `'python' is not recognized` | Python not installed or not in PATH | Install Python from python.org and check "Add to PATH" |
| `'pip' is not recognized` | pip not in PATH | Run `python -m pip install --upgrade pip` |
| `No module named 'playwright'` | Playwright not installed | Run `pip install playwright` then `playwright install chromium` |
| `No module named 'dotenv'` | python-dotenv not installed | Run `pip install python-dotenv` |
| `No module named 'requests'` | requests not installed | Run `pip install requests` |
| Installation fails | Permission issues | Run Command Prompt as Administrator |

### Runtime Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Bot won't start | Dependencies missing | Run option 4 in run.bat to install all dependencies |
| Browser opens then closes | Page navigation failed | Check internet connection, try again |
| `Navigation timeout` | Slow internet or site down | Wait and retry, check lightsailed.com is accessible |
| `Browser closed unexpectedly` | Browser crash | Restart bot, check for other Chrome instances |
| Black screen/flash then closes | Display/graphics issue | Update graphics drivers, run as Administrator |

### Login Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Login not detected | Bot checking too soon | Wait longer after login, check URL changed |
| `Login timed out` | Manual login not completed | Complete Google login in browser window |
| Still on login page | Wrong credentials | Use Google login instead of username/password |
| Session not saved | File permission issue | Run as Administrator, check storage_state.json |

### API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `API error: 401` | Invalid API key | Check .env file, get new key from openrouter.ai |
| `API error: 404` | Model not found | Change model in bot_with_dashboard.py to `meta-llama/llama-3-8b-instruct:free` |
| `API error: 429` | Rate limit exceeded | Wait a few minutes, upgrade API plan |
| `API error: 500` | API server error | Retry, API is temporarily down |
| `AI error: Connection timeout` | Internet issue | Check connection, increase timeout in code |
| AI accuracy is poor | No page context | Check logs for "Context length", should be 500+ chars |

### Book Selection Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Clicked assignment instead of book | Assignment filtering failed | Check logs for "Skipping assignment" messages |
| `No books found` | Library not loaded | Wait longer for library to load, refresh page |
| Book selected but didn't open | Read button not clicked | Check logs for "Clicking Read Book button" |
| `Read Book` button not clicked | Selector mismatch | Check logs for button text, update selectors |

### Reading Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Page not flipping | Selector not found | Check logs for "Flip error", update selectors |
| Flipping too fast/slow | Wrong interval | Change `FLIP_INTERVAL` in bot_with_dashboard.py |
| Bot stuck on one page | Page flip failed | Check for popup/dialog, close manually |
| `Health check failed` | Page unresponsive | Bot will auto-recover, wait for retry |

### Question Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Questions not detected | Selector mismatch | Check logs, update question selectors |
| `Context length: 0` | Text extraction failed | Check for iframe content, update selectors |
| AI gives wrong answers | No page context | Ensure context length is 500-2000 chars |
| `Cloze error` | SVG not found | Check if question is different type |
| Answer not submitted | Submit button not found | Check logs, update submit button selectors |

### Dashboard Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Dashboard won't open | Port already in use | Change `DASHBOARD_PORT` in bot_with_dashboard.py |
| `Access Denied` on dashboard | Bot not running | Start bot first, then open dashboard |
| Dashboard shows 0 for everything | Stats not updating | Check bot logs for errors |
| Logs not updating | WebSocket disconnected | Refresh dashboard page |

### Book Completion Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Book completion not detected | Progress selector changed | Update selectors in `check_book_completed()` |
| Exit button not clicked | Selector mismatch | Check logs for "Exit button not found" |
| New book not selected | Library empty | Add more books to account, check filters |
| Stuck after completion | Navigation failed | Manual intervention needed, restart bot |

### AFK Detection Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Still detected as AFK | AFK prevention not working | Keep browser window visible, don't minimize |
| Tab loses focus | Visibility API not overridden | Check browser console for errors |
| Mouse movement not simulated | Playwright issue | Restart bot, check for updates |

### File Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `.env` not found | File not created | Copy `.env.example` to `.env`, add API key |
| `config.json` not found | First run | Bot creates default config automatically |
| `storage_state.json` missing | Never logged in | Log in once, file will be created |
| `progress.json` missing | First run | Bot creates file after first session |
| Screenshots not saved | Permission issue | Run as Administrator, check folder permissions |
| Logs not written | Folder doesn't exist | Create `logs/` folder manually |

### Performance Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Bot runs slowly | Low RAM/CPU | Close other programs, reduce browser windows |
| High memory usage | Memory leak | Restart bot every few hours |
| Browser lag | Too many tabs | Close unnecessary tabs, reduce viewport size |
| Network timeout | Slow internet | Increase timeout values in code |

---

## 🔍 Debug Mode

To enable detailed debugging:

1. Edit `bot_with_dashboard.py`
2. Find log calls and change level to `"DEBUG"`
3. Restart bot
4. Check `logs/lightsail_bot.log` for detailed output

---

## 📞 Getting More Help

1. **Check logs** - Select option 6 in run.bat
2. **Review screenshots** - Check `q_*.png` files
3. **Test API key** - Visit https://openrouter.ai/keys
4. **Update bot** - Pull latest from GitHub
5. **Reinstall** - Run option 4 in run.bat

---

## 📥 First Time Downloading from GitHub?

**If you just downloaded this from GitHub, follow these steps:**

### Quick Setup for New Users

1. **Install Python** (if not already installed)
   - Go to https://www.python.org/downloads/
   - Download Python 3.8 or newer
   - ✅ Check "Add Python to PATH" during installation

2. **Open the downloaded folder**
   - Navigate to `lightsail automation\lightsail-automation`

3. **Run the launcher**
   - Double-click `run.bat`

4. **Install dependencies** (First time only - takes 5-10 minutes)
   - Select option **4. Install Dependencies**
   - Wait for installation to complete

5. **Run the bot**
   - Select option **1. Run Enhanced Bot with AI**
   - Browser opens automatically
   - Log in with Google
   - Bot starts reading!

### Common Issues for New Users

| Issue | Solution |
|-------|----------|
| "python is not recognized" | Install Python and add to PATH |
| "No module named 'playwright'" | Select option 4 in run.bat |
| Dashboard says "Access Denied" | Dashboard only works when bot is running |
| Bot won't open browser | Run option 4 to install dependencies |
| Black screen/flash then closes | Run as Administrator or check Python installation |

### Need More Help?

- Read `INSTALLATION_GUIDE.md` for detailed setup instructions
- Read `QUICKSTART.md` for quick start guide
- Check logs by selecting option 6 in run.bat

---

## 🎉 Features Summary

| Feature | Status |
|---------|--------|
| AI Question Answering | ✅ |
| Anti-AFK Detection | ✅ |
| Forward-Only Mode | ✅ |
| Auto Book Completion | ✅ |
| Power Text Priority | ✅ |
| Web Dashboard | ✅ |
| Screenshot Capture | ✅ |
| Session Persistence | ✅ |
| Progress Tracking | ✅ |
| Error Logging | ✅ |

---

**Happy Reading! 📚**
