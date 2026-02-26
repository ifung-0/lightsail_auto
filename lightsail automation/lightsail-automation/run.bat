@echo off
echo ==========================================
echo LightSail Automation Bot
echo ==========================================
echo.
echo Choose version:
echo 1. FREE Version (Recommended)
echo 2. OpenAI Version (Requires API key)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting FREE version...
    python lightsail_bot_free_ai.py
) else if "%choice%"=="2" (
    echo.
    echo Starting OpenAI version...
    python lightsail_bot.py
) else (
    echo Invalid choice. Please run again.
    pause
    exit /b
)

pause
