param(
    [string]$InstallDir = "C:\whisper_pulse"
)

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $InstallDir\run.bat >> $InstallDir\logs\task.log 2>&1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00AM"
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "SocialListeningPipeline" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest
