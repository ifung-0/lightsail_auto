# LightSail Automation Bot - Project Summary

## What This Tool Does

This is a **FREE, open-source browser automation tool** for the LightSail Education literacy platform that:

1. **Automatically logs in** to your LightSail account
2. **Selects a book** from your library (or a specific one you choose)
3. **Reads automatically** by flipping pages every 2 minutes (configurable)
4. **Detects and answers questions** using AI:
   - Multiple choice questions (4 options)
   - Fill-in-the-blank (Cloze) questions
   - Short answer questions
5. **Tracks progress** and provides session summaries

## Files Included

| File | Description |
|------|-------------|
| `lightsail_bot_free_ai.py` | **MAIN FILE** - Free version with pattern matching AI |
| `lightsail_bot.py` | Alternative version using OpenAI GPT (requires API key) |
| `config.json` | Your configuration (username, password, settings) |
| `config.template.json` | Template showing config structure |
| `requirements.txt` | Python packages to install |
| `setup.py` | One-click setup script |
| `test_selectors.py` | Test tool to verify website selectors |
| `run.bat` | Windows double-click runner |
| `run.sh` | Mac/Linux runner script |
| `README.md` | Full documentation |
| `QUICKSTART.md` | Quick start guide |
| `.vscode/launch.json` | VS Code run configurations |
| `.gitignore` | Git ignore rules |

## How to Use

### Option 1: VS Code (Recommended)
1. Open folder in VS Code
2. Edit `config.json` with your credentials
3. Press `F5` or click Run → "Run LightSail Bot (FREE Version)"

### Option 2: Command Line
```bash
# Setup (first time only)
python setup.py

# Edit config.json with your credentials

# Run
python lightsail_bot_free_ai.py
```

### Option 3: Double-Click (Windows)
1. Edit `config.json` with your credentials
2. Double-click `run.bat`
3. Select option 1 (FREE version)

## Key Features

### Automatic Question Detection
The bot continuously scans for:
- Radio buttons (multiple choice)
- Text inputs (fill-in-the-blank)
- Textareas (short answer)

### AI Answering (FREE Version)
- **Pattern matching** for intelligent guessing
- **Context analysis** for cloze questions
- **Question type detection** for appropriate responses
- **Optional Hugging Face API** integration (free tier available)

### Session Management
- Logs all actions with timestamps
- Saves screenshots of questions
- Tracks pages read and questions answered
- Provides summary on exit

## Configuration

Edit `config.json`:

```json
{
  "username": "your_lightsail_username",
  "password": "your_lightsail_password",
  "headless": false,
  "page_flip_interval": 120,
  "auto_answer_questions": true,
  "preferred_book_title": "",
  "screenshot_on_question": true,
  "use_ai": true
}
```

### Settings Explained

| Setting | Description | Default |
|---------|-------------|---------|
| `username` | Your LightSail login username | (required) |
| `password` | Your LightSail login password | (required) |
| `headless` | Run without browser window | false |
| `page_flip_interval` | Seconds between page flips | 120 (2 min) |
| `auto_answer_questions` | Automatically answer questions | true |
| `preferred_book_title` | Specific book to read | "" (auto) |
| `screenshot_on_question` | Save question screenshots | true |
| `use_ai` | Use AI (vs random answers) | true |

## Safety & Detection

⚠️ **Important Considerations:**

1. **Terms of Service**: Automation may violate LightSail's ToS
2. **Detection Risk**: Automated behavior can potentially be detected
3. **Educational Use**: Tool is for educational assistance, not cheating
4. **Responsibility**: Use at your own risk

## Technical Details

### Technologies Used
- **Python 3.8+** - Programming language
- **Playwright** - Browser automation
- **Pattern Matching** - Free AI alternative
- **OpenAI API** - Optional (paid) AI enhancement

### Browser Automation
- Uses Chromium browser (installed automatically)
- Mimics human-like interactions
- Handles dynamic page elements
- Takes screenshots for debugging

### Question Answering Logic

**Multiple Choice:**
1. Detects radio buttons or clickable options
2. Extracts question text and options
3. Uses pattern matching or AI to select answer
4. Clicks option and submits

**Fill-in-the-Blank:**
1. Detects text input fields
2. Analyzes surrounding context
3. Determines appropriate word type
4. Fills in answer and submits

**Short Answer:**
1. Detects textarea fields
2. Analyzes question type (what/why/how/when/where/who)
3. Generates appropriate response
4. Fills in and submits

## Troubleshooting

### Login Issues
- Verify credentials in `config.json`
- Run `python test_selectors.py` to check selectors
- Check `login_failed.png` screenshot

### Book Not Selected
- Check `dashboard.png` to see available books
- Specify exact title in `preferred_book_title`
- Try different book selection methods

### Questions Not Detected
- LightSail may have updated their UI
- Check question screenshots
- Update selectors in code if needed

## Free vs OpenAI Version

| Feature | FREE Version | OpenAI Version |
|---------|-------------|----------------|
| Cost | $0 | ~$0.002 per question |
| Accuracy | Good | Excellent |
| Setup | None | API key required |
| Speed | Fast | Slightly slower |
| Recommended For | Most users | Best accuracy |

## Updates & Maintenance

LightSail may update their website, requiring selector updates. If bot stops working:

1. Check error messages
2. Run `test_selectors.py`
3. Update selectors in bot code
4. Test and verify

## Support

This is an open-source tool. For help:
1. Read README.md
2. Check error logs
3. Review screenshots
4. Update selectors if website changed

## Legal Disclaimer

This tool is provided for **educational purposes only**. Users are responsible for complying with LightSail's Terms of Service. The authors assume no liability for misuse or consequences of using this tool.

---

**Created**: 2024
**License**: MIT
**Free to use and modify**
