# Register only; apply from Mouse Properties when you choose.
$ErrorActionPreference = 'Stop'
$scheme = 'Ryoma Crimson v2.0.0'
$cursorDir = Join-Path $PSScriptRoot 'cursors'
$files = @(
    'normal.cur'
    'help.cur'
    'working.ani'
    'busy.ani'
    'precision.cur'
    'text.cur'
    'handwriting.cur'
    'unavailable.cur'
    'resize-ns.cur'
    'resize-ew.cur'
    'resize-nwse.cur'
    'resize-nesw.cur'
    'move.cur'
    'alternate.cur'
    'link.cur'
    'location.cur'
    'person.cur'
)
$paths = @($files | ForEach-Object { Join-Path $cursorDir $_ })
foreach ($cursorPath in $paths) {
    if (-not (Test-Path -LiteralPath $cursorPath)) { throw "Missing cursor: $cursorPath" }
}
$key = 'HKCU:\Control Panel\Cursors\Schemes'
New-Item -Path $key -Force | Out-Null
New-ItemProperty -Path $key -Name $scheme -Value ($paths -join ',') -PropertyType String -Force | Out-Null
Write-Host 'Registered Ryoma Crimson v2.0.0. Select it in Mouse Properties > Pointers, then Apply.'
Start-Process control.exe -ArgumentList 'main.cpl,,1'
