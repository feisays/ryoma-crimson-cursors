# Reapply the no-trail workaround after this Windows user signs in.
# Keep this folder in a fixed location while the task is enabled.
[CmdletBinding()]
param(
    [switch]$Remove,
    [switch]$Status
)
$ErrorActionPreference = 'Stop'
if ($Remove -and $Status) { throw 'Choose either -Remove or -Status.' }
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$taskName = "RyomaCrimson-CursorColor-$sid"
$description = "Ryoma Crimson cursor color workaround for $sid"
$scriptPath = Join-Path $PSScriptRoot 'cursor-color-workaround.ps1'
$existing = Get-ScheduledTask -TaskPath '\' -ErrorAction Stop |
    Where-Object { $_.TaskName -eq $taskName }
if ($Status) {
    if ($existing) {
        $existing | Select-Object TaskName, State, Description
        $existing.Actions | Select-Object Execute, Arguments
        Get-ScheduledTaskInfo -TaskName $taskName -TaskPath '\' |
            Select-Object LastRunTime, LastTaskResult
    } else {
        Write-Output 'No cursor color logon task is installed for this user.'
    }
    return
}
if ($existing -and $existing.Description -ne $description) {
    throw "Another task already uses the name $taskName; it was not changed."
}
if ($Remove) {
    if ($existing) {
        # Stop an in-flight run before removing it, so it cannot reapply later.
        Stop-ScheduledTask -TaskName $taskName -TaskPath '\'
        Unregister-ScheduledTask -TaskName $taskName -TaskPath '\' -Confirm:$false
    }
    Write-Output 'Cursor color logon task removed; current cursor settings were not changed.'
    return
}
if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Missing workaround script: $scriptPath"
}
$powershellPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$action = New-ScheduledTaskAction -Execute $powershellPath -Argument (
    '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -NoTrail' -f $scriptPath
)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $sid
$trigger.Delay = 'PT15S'
$principal = New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
Register-ScheduledTask -TaskName $taskName -TaskPath '\' -Description $description `
    -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
& $scriptPath -NoTrail
Write-Output 'Installed: reapply without a visible window 15 seconds after this user signs in.'
Write-Output 'To remove automatic application, run cursor-color-logon.ps1 -Remove.'
