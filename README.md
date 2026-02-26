# LightSail Automation Bot

An automated tool for LightSail Education literacy platform that automatically reads books by alternating page flips every 40 seconds to simulate continuous reading activity.

## Features

- **Automatic Login**: Logs into LightSail with your credentials or Google OAuth
- **Book Selection**: Automatically selects a book from your library
- **Alternating Page Flips**: 
  - Flips RIGHT every 40 seconds (counts as "page read")
  - Flips LEFT every 40 seconds in alternation
  - Creates reading activity to accumulate reading time
- **Reading Session Tracking**:
  - Tracks pages read (right flips)
  - Tracks total flips (both directions)
  - Tracks actual elapsed reading time (hours/minutes/seconds)
- **Session Logging**: Displays detailed statistics when stopped
- **Minimal Interaction**: No question answering - pure page flipping automation

## How It Works

The bot uses a simple alternating page flip strategy to simulate active reading:

1. **Login**: Bot logs into LightSail (manual Google OAuth or credentials)
2. **Book Selection**: Automatically opens a book from your library
3. **Reading Loop**:
   - Flips RIGHT (pages_read counter +1)
   - Waits 40 seconds
   - Flips LEFT
   - Waits 40 seconds
   - Repeats infinitely until stopped
4. **Tracking**: 
   - Live stats shown after each flip
   - Total elapsed time calculated in real-time
5. **Stopping**: Press `Ctrl+C` to stop and see final session summary

## Installation

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed.

[Download Python](https://www.python.org/downloads/) - Get version 3.8 or newer

### Step 2: Install Dependencies

```bash
# Navigate to the project folder
cd lightsail-automation

# Install required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 3: Configure Your Credentials

Edit `config.json` with your preferences:

```json
{
  "username": "",
  "password": "",
  "headless": false,
  "page_flip_interval": 40,
  "auto_answer_questions": false,
  "preferred_book_title": "",
  "screenshot_on_question": false,
  "use_ai": false,
  "use_openrouter": true,
  "openrouter_api_key": "sk-or-v1-...",
  "openrouter_model": "meta-llama/llama-3.2-3b-instruct:free"
}
```

**Note**: Leave `username` and `password` blank to use manual Google OAuth login in browser.

---

## Quick Start Guide

Follow these steps to get the bot running:

### Step 1: Prepare Your Environment

1. **Install Python** (if not already installed)
2. **Open Terminal/PowerShell** and navigate to the project folder:
   ```bash
   cd "c:\Users\Isaac\OneDrive\Desktop\lsauto\lightsail automation\lightsail-automation"
   ```
3. **Install dependencies** (one-time setup):
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### Step 2: Configure the Bot

Edit `config.json` in the project folder:

**Option A: Google OAuth Login (Recommended)**
- Leave `username` and `password` blank
- The bot will wait for you to manually click "Sign in with Google" in the browser

**Option B: Username/Password Login**
- Enter your LightSail username in `"username"`
- Enter your LightSail password in `"password"`

### Step 3: Run the Bot

Execute this command:
```bash
python lightsail_bot_free_ai.py
```

### Step 4: Watch It Work

When you run the bot:

1. **Browser Window Opens** - A Chrome window will appear
2. **Login Prompt** - If using Google login, sign in manually
3. **Book Selection** - Bot automatically picks a book (first available)
4. **Reading Starts** - Page flips begin automatically

### Step 5: Monitor Progress

You'll see live stats after each flip:
```
✓ Pages read: 1 | Total flips: 2 | Reading time: 1m 20s
✓ Pages read: 2 | Total flips: 4 | Reading time: 2m 40s
```

### Step 6: Stop the Bot

Press `Ctrl+C` in the terminal to stop anytime. You'll see:
```
==================================================
SESSION SUMMARY
==================================================
  Book: The Great Gatsby
  Pages read (flipped right): 15
  Total flips (both directions): 30
  Reading time: 15m 42s
==================================================
```

---

## Common Tasks

### Task: Change How Often Pages Flip

1. Open `config.json`
2. Find this line: `"page_flip_interval": 40,`
3. Change 40 to your desired seconds:
   - `20` = flip every 20 seconds (faster)
   - `60` = flip every 60 seconds (slower)
4. Save and restart the bot

### Task: Use a Specific Book

1. Open `config.json`
2. Find this line: `"preferred_book_title": "",`
3. Replace with your book name: `"preferred_book_title": "The Great Gatsby",`
4. Save and restart the bot

### Task: Run Without Seeing Browser

1. Open `config.json`
2. Change: `"headless": false,` to `"headless": true,`
3. Save and restart
4. Bot will run in background (note: first login still needs manual interaction)

### Task: Specify Your Own Book

If you want to read a specific book instead of auto-selecting:

1. Log into LightSail manually in your browser
2. Find the exact book title
3. Open `config.json` and set: `"preferred_book_title": "Exact Book Title"`
4. Run the bot

---

## Troubleshooting Guide

### Problem: Bot Won't Start

**Error**: `ModuleNotFoundError: No module named 'playwright'`
```bash
# Solution:
pip install -r requirements.txt
playwright install chromium
```

### Problem: Can't Connect to LightSail

**Error**: `Navigation failed` or `Timeout`
- Check your internet connection
- Verify LightSail website is accessible
- Try again after 1-2 minutes

### Problem: Google Login Not Working

**What to do**:
1. Leave `username` and `password` blank in config
2. Run the bot: `python lightsail_bot_free_ai.py`
3. When browser opens, manually click "Sign in with Google"
4. Complete the Google login in the browser
5. Bot will detect successful login and continue automatically

### Problem: Book Not Being Selected

**Solution**:
1. Open `config.json`
2. Add your preferred book:
   ```json
   "preferred_book_title": "The Hunger Games"
   ```
3. Save and run again

### Problem: Page Flips Not Working

**Checklist**:
- Make sure browser window is visible and not minimized
- Check if LightSail page has loaded (wait a few seconds)
- Verify network connection is stable
- Try restarting the bot

---

## Tips for Best Results

✓ **Run at normal speed** - Don't maximize browser to fullscreen
✓ **Keep internet stable** - Don't interrupt network connection
✓ **Check logs** - Watch the terminal output for any errors
✓ **First time?** - Run with `headless: false` to see what's happening
✓ **Long sessions** - The bot can run for hours without stopping
✓ **Session persistence** - Once you log in, it saves your session for next time

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `username` | LightSail username (leave blank for Google OAuth) | "" |
| `password` | LightSail password (leave blank for Google OAuth) | "" |
| `headless` | Run browser in background (no window) | false |
| `page_flip_interval` | Seconds between page flips | 40 |
| `auto_answer_questions` | Automatically answer questions (disabled for page flip mode) | false |
| `preferred_book_title` | Specific book to read (empty = auto-select first) | "" |
| `screenshot_on_question` | Save screenshots of questions | false |
| `use_ai` | Use AI or random answers (disabled) | false |

## Usage

### Run the Bot

```bash
python lightsail_bot_free_ai.py
```

When the bot starts:
1. A browser window opens automatically
2. You may need to manually log in with Google (if credentials left blank)
3. Bot will automatically select a book
4. Page flips begin (right, left, right, left, ...)
5. Stats are displayed after each flip
6. Press `Ctrl+C` to stop and see session summary

## Example Session Output

```
[12:34:56] [INFO] Flipping RIGHT...
✓ Pages read: 1 | Total flips: 1 | Reading time: 0m 1s
[12:35:01] [INFO] Waiting 40 seconds before next flip...

[12:35:42] [INFO] Flipping LEFT...
✓ Pages read: 1 | Total flips: 2 | Reading time: 0m 46s
[12:35:47] [INFO] Waiting 40 seconds before next flip...

[12:36:28] [INFO] Flipping RIGHT...
✓ Pages read: 2 | Total flips: 3 | Reading time: 1m 32s
```

When you stop (Ctrl+C):
```
==================================================
SESSION SUMMARY
==================================================
  Book: The Great Gatsby
  Pages read (flipped right): 15
  Total flips (both directions): 30
  Reading time: 15m 42s
==================================================
```

## Stopping the Bot

Press `Ctrl+C` at any time to gracefully stop the bot. It will display:
- Total pages flipped right
- Total flips in both directions
- Actual elapsed reading time

## Troubleshooting

### Login Issues
- Leave `username` and `password` blank for manual Google OAuth login
- Follow the Google login prompt in the browser window
- If using credentials, verify they're correct in `config.json`

### Book Not Found
- Try specifying exact book title in `preferred_book_title` in config
- Allow sufficient time for the book library to load

### Page Flip Not Working
- Check browser window is visible and active
- Verify the page navigation buttons are visible
- Check LightSail website hasn't changed their button selectors

### Incorrect Time Calculation
- Time is calculated from when reading starts (first page flip)
- Ensure system clock is accurate

## Safety & Ethics

⚠️ **Important Notes:**

1. **Educational Purpose**: This tool is for educational purposes and helping students with reading disabilities or time constraints.

2. **Terms of Service**: Using automation may violate LightSail's Terms of Service. Use at your own risk.

3. **Learning**: This tool should complement, not replace, actual reading and learning.

4. **Detection**: Automated behavior may be detectable by the platform.

## Customization

### Change Page Flip Speed
Edit `config.json` to adjust the time between flips:
```json
{
  "page_flip_interval": 20  // 20 seconds instead of 40
}
```

### Specify a Book
```json
{
  "preferred_book_title": "The Great Gatsby"
}
```

### Run in Background (Headless)
```json
{
  "headless": true
}
```
Note: Still requires initial manual Google login if credentials are blank.

## How It Works (Technical)

The bot uses Playwright (headless browser automation) to:

1. **Launch Chrome** with custom flags to avoid detection
2. **Navigate to LightSail** reading interface
3. **Authenticate** via provided credentials or manual Google OAuth
4. **Select a book** from the library
5. **Enter reading loop** that alternates:
   - Clicks the "Next Page" button (ArrowRight or button selector)
   - Waits 40 seconds
   - Clicks the "Previous Page" button (ArrowLeft or button selector)
   - Waits 40 seconds
   - Repeats infinitely
6. **Track statistics** in real-time:
   - Pages read (right flips only)
   - Total flips (both directions)
   - Elapsed time since start

## Requirements

- Python 3.8+
- Playwright
- Internet connection
- LightSail account
- ~100MB disk space for browser

## File Structure

```
lightsail-automation/
├── lightsail_bot_free_ai.py   # Main bot (page flipping mode)
├── config.json                # Your configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── storage_state.json         # Saved session (auto-generated)
└── *.png                      # Screenshots (if enabled)
```

## Updates

LightSail may update their website, which could break selectors. If the bot stops working:

1. Check error messages in terminal
2. Verify network connection
3. Try updating button selectors if website changed
4. Check if LightSail's page structure has changed

## Support

For issues:
1. Check troubleshooting section above
2. Review error messages in terminal output
3. Verify `config.json` settings
4. Check network connectivity

## License

MIT License - Free to use and modify

---

## Disclaimer

⚠️ **Important**: This tool is provided as-is for educational purposes only. 

- Using automation may violate LightSail's Terms of Service
- Use at your own risk and responsibility
- Educational institutions may detect automated behavior
- This tool should not replace actual reading and learning
- The authors are not responsible for any consequences

Use this tool responsibly and ethically.
