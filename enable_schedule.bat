@echo off
powershell -Command "Enable-ScheduledTask -TaskName 'SCMJobAutomation'"
echo =================================================================
echo [OK] SCM Job Automation Schedule has been turned ON!
echo The system will run automatically at 8:00 AM and 8:00 PM daily.
echo =================================================================
pause
