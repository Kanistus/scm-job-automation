@echo off
cd /d "c:\Users\kanis\Documents\explore with ai\AI AUTOMATION\Nakuri job auto"
echo =================================================================
echo [*] Starting SCM Telegram Bot Command Listener...
echo [*] You can now control the bot via Telegram from your phone!
echo =================================================================
python -u backend/services/telegram_bot.py
pause
