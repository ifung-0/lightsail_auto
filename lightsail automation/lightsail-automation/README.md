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
Edit `bot_with_dashboard.py` and update:
```python
OPENROUTER_API_KEY = "your-api-key-here"  # Get free key at openrouter.ai
```

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

Edit `bot_with_dashboard.py` to customize:

```python
# Bot Settings
FLIP_INTERVAL = 40          # Seconds between page flips
HEADLESS = False            # Show browser window

# AI Settings
OPENROUTER_API_KEY = "sk-or-v1-..."  # Your API key
OPENROUTER_MODEL = "qwen/qwen-2.5-coder-32b-instruct:free"

# Dashboard
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

## 🆘 Support

1. Check dashboard logs at http://localhost:8765
2. Review log files in `logs/` directory
3. Check question screenshots
4. Verify API key is valid
5. Ensure Python 3.8+ installed

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
