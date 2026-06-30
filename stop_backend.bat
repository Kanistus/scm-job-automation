@echo off
echo [*] Stopping background uvicorn server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a
    echo [OK] Killed PID %%a
)
echo [OK] Stop command finished.
pause
