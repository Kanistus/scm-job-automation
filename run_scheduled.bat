@echo off
cd /d "c:\Users\kanis\Documents\explore with ai\AI AUTOMATION\Job appilcation auto"
echo ================================================================= >> scheduler.log
echo Scheduled Run Started: %date% %time% >> scheduler.log
echo ================================================================= >> scheduler.log
python -u backend/automate_apply.py >> scheduler.log 2>&1
