@echo off
title LightSail Automation Bot
color 0A

:menu
cls
echo ============================================================
echo   LightSail Automation Bot - Enhanced Edition
echo ============================================================
echo.
echo   Select an option:
echo.
echo   1. Run Enhanced Bot with AI (Recommended)
echo   2. Run Bot (No AI - Pattern Matching Only)
echo   3. Run Setup Wizard
echo   4. Install Dependencies
echo   5. Open Dashboard
echo   6. View Logs
echo   7. Exit
echo.
echo ============================================================
echo.

set /p choice="Enter choice (1-7): "

if "%choice%"=="1" goto run_ai
if "%choice%"=="2" goto run_basic
if "%choice%"=="3" goto setup
if "%choice%"=="4" goto install
if "%choice%"=="5" goto dashboard
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto end

echo Invalid choice! Please try again.
timeout /t 2 >nul
goto menu

:run_ai
cls
echo ============================================================
echo   Running Enhanced Bot with AI
echo ============================================================
echo.
echo   Starting bot with AI question answering...
echo   Dashboard: http://localhost:8765
echo.
echo   Press Ctrl+C to stop the bot
echo ============================================================
echo.
python bot_with_dashboard.py
goto menu

:run_basic
cls
echo ============================================================
echo   Running Bot (Pattern Matching Only)
echo ============================================================
echo.
echo   Note: Edit bot_with_dashboard.py and set:
echo   OPENROUTER_API_KEY = ""
echo.
python bot_with_dashboard.py
goto menu

:setup
cls
echo ============================================================
echo   Running Setup Wizard
echo ============================================================
echo.
python config.py --setup
echo.
echo   Setup complete!
timeout /t 2 >nul
goto menu

:install
cls
echo ============================================================
echo   Installing Dependencies
echo ============================================================
echo.
echo   Installing Python packages...
pip install -r requirements.txt
echo.
echo   Installing Playwright browser...
playwright install chromium
echo.
echo   Installation complete!
timeout /t 2 >nul
goto menu

:dashboard
cls
echo ============================================================
echo   Opening Dashboard
echo ============================================================
echo.
echo   Opening http://localhost:8765 in your browser...
start http://localhost:8765
echo.
echo   Dashboard opened!
timeout /t 2 >nul
goto menu

:logs
cls
echo ============================================================
echo   Viewing Logs
echo ============================================================
echo.
echo   Recent logs from lightsail_bot.log:
echo ============================================================
if exist logs\lightsail_bot.log (
    type logs\lightsail_bot.log
) else (
    echo No log file found.
)
echo.
echo ============================================================
pause
goto menu

:end
cls
echo Goodbye!
timeout /t 1 >nul
exit
