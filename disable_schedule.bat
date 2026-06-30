@echo off
powershell -Command "Disable-ScheduledTask -TaskName 'SCMJobAutomation'"
echo =================================================================
echo [OK] SCM Job Automation Schedule has been turned OFF!
echo Background jobs are paused and will not run automatically.
echo =================================================================
pause
