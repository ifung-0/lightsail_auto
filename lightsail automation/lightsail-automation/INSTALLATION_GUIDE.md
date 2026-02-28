# LightSail Bot - Installation Guide for Windows

## ⚠️ IMPORTANT: First Time Setup

If you just downloaded this from GitHub, **follow these steps**:

---

## Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.8 or newer (3.12 recommended)
3. **IMPORTANT:** Check ✅ "Add Python to PATH" during installation
4. Click "Install Now"

**Verify Python is installed:**
```
Open Command Prompt and type: python --version
You should see: Python 3.x.x
```

---

## Step 2: Install Bot Dependencies

### Option A: Using run.bat (Easiest)

1. Navigate to the downloaded folder
2. Double-click `run.bat`
3. Select option **4. Install Dependencies**
4. Wait for installation to complete (may take 5-10 minutes first time)
5. After installation, select option **1. Run Enhanced Bot with AI**

### Option B: Manual Installation

1. Open Command Prompt in the bot folder
2. Run these commands:

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## Step 3: Configure API Key (Optional but Recommended)

1. Open `bot_with_dashboard.py` in a text editor
2. Find line 18:
   ```python
   OPENROUTER_API_KEY = ""
   ```
3. Get a free API key from https://openrouter.ai/keys
4. Paste your key:
   ```python
   OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
   ```
5. Save the file

**Why?** With AI enabled:
- ✅ Questions answered automatically
- ✅ Only flips forward (no going back)
- ✅ Better accuracy

---

## Step 4: Run the Bot

### Method 1: Double-Click (Recommended)

1. Double-click `run.bat`
2. Select option **1. Run Enhanced Bot with AI**
3. Browser opens automatically
4. Log in with Google
5. Bot starts reading

### Method 2: Command Line

```bash
python bot_with_dashboard.py
```

---

## 🌐 Dashboard

Once the bot is running, access the dashboard at:
**http://localhost:8765**

The dashboard shows:
- Current book
- Pages read
- Questions answered
- Session duration
- Real-time logs

---

## ❌ Common Errors & Fixes

### "python is not recognized"
**Fix:** Install Python and check "Add to PATH" during installation

### "No module named 'playwright'"
**Fix:** 
```bash
pip install playwright
playwright install chromium
```

### "Access Denied" on dashboard
**Fix:** The dashboard only works when the bot is running. Start the bot first!

### Bot won't open browser
**Fix:** 
1. Check if Python is installed correctly
2. Run `pip install -r requirements.txt`
3. Run `playwright install chromium`

### "ModuleNotFoundError"
**Fix:** Run option 4 in run.bat to install all dependencies

---

## 📁 Folder Structure

After downloading, your folder should look like:

```
lightsail_auto/
├── bot_with_dashboard.py    ← Main bot file
├── run.bat                  ← Double-click this!
├── requirements.txt         ← Dependencies
├── README.md               ← Full documentation
├── QUICKSTART.md           ← Quick start guide
└── ... (other files)
```

---

## 🆘 Need Help?

1. **Check logs**: Select option 6 in run.bat
2. **Reinstall**: Select option 4 in run.bat
3. **Read docs**: Check README.md and QUICKSTART.md

---

## ✅ Quick Checklist

Before running the bot, make sure:

- [ ] Python 3.8+ installed
- [ ] Python added to PATH
- [ ] Dependencies installed (option 4 in run.bat)
- [ ] Playwright browser installed
- [ ] API key configured (optional but recommended)

---

**That's it! You're ready to use the LightSail Bot!** 🎉

For more details, see `README.md` and `QUICKSTART.md`.
