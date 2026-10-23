# Reversible workaround for display-dependent cursor color washout.
# Usage: .\cursor-color-workaround.ps1 [-NoTrail | -Restore | -Status]
[CmdletBinding()]
param(
    [switch]$NoTrail,
    [switch]$Restore,
    [switch]$Status
)
$ErrorActionPreference = 'Stop'
if (($Restore -and $Status) -or ($Restore -and $NoTrail) -or ($Status -and $NoTrail)) { throw 'Choose only one mode.' }
if (-not ('RyomaCursorColor.Native' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace RyomaCursorColor {
    public static class Native {
        [DllImport("user32.dll", EntryPoint="SystemParametersInfoW", SetLastError=true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool Get(uint action, uint parameter, out uint value, uint flags);
        [DllImport("user32.dll", EntryPoint="SystemParametersInfoW", SetLastError=true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool Set(uint action, uint parameter, IntPtr value, uint flags);
    }
}
'@
}
function Get-Trails {
    [uint32]$value = 0
    if (-not [RyomaCursorColor.Native]::Get(0x005E, 0, [ref]$value, 0)) {
        throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastWin32Error())
    }
    return $value
}
$backupPath = Join-Path $PSScriptRoot 'cursor-color-backup.local.json'
$before = Get-Trails
if ($Status) {
    Write-Output "Mouse trails: $before (0/1 = disabled; 2 = shortest; 4294967295 = experimental no-trail workaround)."
    Write-Output "Backup available: $(Test-Path -LiteralPath $backupPath)"
    return
}
if ($Restore) {
    if (-not (Test-Path -LiteralPath $backupPath)) { throw 'No saved setting to restore.' }
    $backup = Get-Content -LiteralPath $backupPath -Raw | ConvertFrom-Json
    if ($backup.UserSid -ne [Security.Principal.WindowsIdentity]::GetCurrent().User.Value) {
        throw 'This backup belongs to a different Windows user.'
    }
    [uint32]$target = $backup.MouseTrails
    if ($target -gt 16 -and $target -ne [uint32]::MaxValue) { throw 'Invalid saved mouse trails value.' }
} else {
    if (-not (Test-Path -LiteralPath $backupPath)) {
        @{
            MouseTrails = $before
            UserSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
            SavedAt = (Get-Date).ToString('o')
        } | ConvertTo-Json | Set-Content -LiteralPath $backupPath -Encoding UTF8
    }
    [uint32]$target = 2
    # Undocumented -1 bit pattern: reported to use software drawing without trails.
    # Opt-in only; verify colors and responsiveness on the affected PC.
    if ($NoTrail) { $target = [uint32]::MaxValue }
}
# SPIF_UPDATEINIFILE | SPIF_SENDCHANGE: save the setting and notify applications.
if (-not [RyomaCursorColor.Native]::Set(0x005D, $target, [IntPtr]::Zero, 3)) {
    throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastWin32Error())
}
$after = Get-Trails
if ($after -ne $target) { throw "Setting did not take effect: expected $target, read $after." }
if ($Restore) { Remove-Item -LiteralPath $backupPath }
Write-Output "Mouse trails changed: $before -> $after."
Write-Output 'Check cursor colors while idle, moving, holding and releasing the mouse button.'
