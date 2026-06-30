# Create the action pointing to our scheduled batch file wrapper
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument '/c "c:\Users\kanis\Documents\explore with ai\AI AUTOMATION\Job appilcation auto\run_scheduled.bat"'

# Create daily triggers for 8:00 AM and 8:00 PM
$triggerMorning = New-ScheduledTaskTrigger -Daily -At 8:00AM
$triggerEvening = New-ScheduledTaskTrigger -Daily -At 8:00PM

# Enable WakeToRun so the PC wakes from sleep to execute
$settings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
Register-ScheduledTask -TaskName "SCMJobAutomation" -Action $action -Trigger $triggerMorning, $triggerEvening -Settings $settings -Force

Write-Host "[OK] Scheduled Task 'SCMJobAutomation' registered successfully with Sleep Mode wake support!" -ForegroundColor Green
