@echo off
cd /d "%~dp0backend"
:: Start uvicorn backend server
python -m uvicorn main:app --host 127.0.0.1 --port 8000
