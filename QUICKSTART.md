# LightSail Bot - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd "lightsail automation\lightsail-automation"
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure API Key (Recommended)

**IMPORTANT: Use .env file for security!**

1. Copy the example file:
   ```bash
   cd "lightsail automation\lightsail-automation"
   copy .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE
   ```

3. Get a free key at: https://openrouter.ai/keys

4. Use this model (in bot_with_dashboard.py):
   ```python
   OPENROUTER_MODEL = "google/gemma-3n-e2b-it:free"
   ```

**Why use AI?**
- ✅ Questions answered automatically
- ✅ Reads full page text (700-800 chars from iframes)
- ✅ Only flips forward (no going back)
- ✅ ~80%+ accuracy with context

### Step 3: Run the Bot

**Option A: Double-Click (Easiest)**
1. Double-click `run.bat`
2. Select option 1 (Enhanced Bot with AI)
3. Done!

**Option B: Command Line**
```bash
python bot_with_dashboard.py
```

### Step 4: Log In

1. Browser opens automatically
2. Click "Sign in with Google"
3. Complete login
4. Bot detects login and continues

### Step 5: Select a Book

The bot will:
1. Search for Power Text books automatically
2. Skip assignments (like "Retake Clozes")
3. Click on the first Power Text found
4. Click "Read Book" button
5. Start reading

**Or manually click any book** - bot will take over!

### Step 6: Monitor Progress

**Dashboard:** Open http://localhost:8765

Shows:
- Current book
- Pages read
- Questions answered
- Session duration
- Real-time logs

---

## 📋 Common Commands

```bash
# Normal run
python bot_with_dashboard.py

# Open dashboard only
start http://localhost:8765

# View logs
type logs\lightsail_bot.log

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
playwright install chromium
```

---

## ⚙️ Quick Configuration

Edit `bot_with_dashboard.py`:

### Change Flip Speed
```python
FLIP_INTERVAL = 30  # Seconds (default: 40)
```

### Enable/Disable AI
```python
OPENROUTER_API_KEY = "sk-or-v1-..."  # With AI
OPENROUTER_API_KEY = ""              # Without AI
```

### Change Dashboard Port
```python
DASHBOARD_PORT = 8766  # Default: 8765
```

### Headless Mode (No Browser Window)
```python
HEADLESS = True  # Warning: Login harder without window
```

---

## 🎯 What the Bot Does

### 1. Login
- Opens LightSail website
- Waits for Google login
- Saves session for next time

### 2. Book Selection
- Searches for Power Text books first
- Clicks book → Clicks "Read"
- Takes screenshot

### 3. Reading Loop
- Flips page every ~40 seconds
- Only goes forward (when AI enabled)
- Checks for questions

### 4. Question Answering
When question detected:
1. Takes screenshot
2. Extracts answer options
3. Sends to AI
4. Clicks correct answer
5. Submits

### 5. Book Completion
When book ends:
1. Detects 100% progress
2. Detects missing next button
3. Clicks exit → Confirms
4. Selects new Power Text book
5. Continues reading

### 6. Anti-AFK
- Simulates mouse movement
- Overrides visibility detection
- **You can switch to other programs!**

---

## 🔍 Understanding the Dashboard

### Stats Displayed

| Stat | What It Means |
|------|---------------|
| Book | Current book title |
| Pages | Forward page flips |
| Flips | Total flips |
| Duration | Session time |
| Questions | Questions found |
| Answered | Questions answered |

### Log Colors

- 🟢 **INFO** (Green) - Normal operation
- 🟡 **WARNING** (Yellow) - Attention needed
- 🔴 **ERROR** (Red) - Something went wrong

---

## 🐛 Quick Troubleshooting

### Bot Won't Start
```bash
pip install -r requirements.txt --force-reinstall
playwright install chromium
```

### "No module named playwright"
```bash
playwright install chromium
```

### Login Not Detected
- Keep browser window visible
- Don't minimize browser
- Wait for "Login detected!" in logs

### Questions Not Answered
- Check API key is correct
- Check dashboard logs
- Verify screenshots saved (`q_1.png`, etc.)

### Book Not Auto-Selecting
- Check library has Power Text books
- Look for "Progress at 100%!" in logs
- Check exit button clicked

### Dashboard Won't Load
- Check port 8765 not in use
- Try http://127.0.0.1:8765
- Restart bot

### AFK Detection Still Happens
- Don't close browser window
- Don't minimize browser
- Check AFK prevention in logs

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `storage_state.json` | Saved login session |
| `progress.json` | Reading progress |
| `book_selection.png` | Library screenshot |
| `q_1.png`, `q_2.png` | Question screenshots |
| `logs/lightsail_bot.log` | Main log file |
| `logs/errors.log` | Error log |

---

## 💡 Tips for Best Results

### ✅ Do:
- Keep browser window visible (don't minimize)
- Let bot auto-select books
- Use AI for better accuracy
- Check dashboard for real-time status
- Let book completion run automatically

### ❌ Don't:
- Close browser window manually
- Minimize browser (may trigger AFK)
- Interfere with bot while running
- Use without API key (less accurate)

---

## 🆘 Getting Help

1. **Check Dashboard** - http://localhost:8765
2. **View Logs** - Option 6 in run.bat
3. **Check Screenshots** - Look in project folder
4. **Verify API Key** - Get new key at openrouter.ai
5. **Reinstall** - Run option 4 in run.bat

---

## 🎉 Feature Checklist

All features implemented and working:

- [x] AI Question Answering
- [x] Anti-AFK Detection
- [x] Forward-Only Mode (with AI)
- [x] Auto Book Completion
- [x] Power Text Priority
- [x] Web Dashboard
- [x] Screenshot Capture
- [x] Session Persistence
- [x] Progress Tracking
- [x] Error Logging

---

## ⚠️ Important Notes

1. **Terms of Service**: Automation may violate LightSail's ToS
2. **Detection Risk**: No method is 100% undetectable
3. **Educational Use**: Use responsibly
4. **API Key**: Get free key at https://openrouter.ai/keys

---

**Happy Reading! 📚**

Need more help? Check `README.md` for full documentation.
