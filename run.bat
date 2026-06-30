@echo off
title "Antigravity JobBot | Job Application Automation Assistant"

echo =================================================================
echo        🚀 STARTING ANTIGRAVITY JOB APPLICATION BOT 🚀
echo =================================================================
echo.

cd /d "%~dp0"

:: 1. Setup Backend Environment
echo [*] Checking Backend Python dependencies...
python -m pip install -r backend\requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Failed to install some Python dependencies. Please verify your Python environment.
)

echo [*] Initializing Playwright browser engines...
python -m playwright install chromium
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Playwright browser engines couldn't be installed. Headless browser automation may require manual installation.
)

:: 2. Launch Backend FastAPI Server
echo [*] Starting FastAPI Backend on http://localhost:8000...
start "JobBot API Server" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000"


:: 3. Launch Frontend Vite Server
echo [*] Checking Node packages in frontend...
cd frontend
if not exist node_modules (
    echo [*] Installing Node packages...
    call npm install
)

echo [*] Starting React Dashboard on http://localhost:5173...
start "JobBot Dashboard" cmd /k "call npm run dev"

:: 4. Open browser to the workspace
echo [*] Opening dashboard in your default browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo =================================================================
echo           🎉 JOBLIST ENGINE AND DASHBOARD RUNNING! 🎉
echo   Keep this command prompt open to see server and browser activity.
echo =================================================================
pause
