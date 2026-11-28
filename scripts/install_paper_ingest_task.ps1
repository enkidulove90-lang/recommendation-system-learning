[CmdletBinding()]
param(
    [string]$ConfigPath = '',
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
if (-not $ConfigPath) { $ConfigPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'config\paper_ingest_schedule.yaml' }
if (-not (Test-Path -LiteralPath $ConfigPath)) { throw "ConfigPath does not exist: $ConfigPath" }
$values = @{}
Get-Content -LiteralPath $ConfigPath | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_]+):\s*["'']?([^#"'']+?)["'']?\s*$') { $values[$matches[1]] = $matches[2].Trim() }
}
foreach ($name in 'time','working_dir','python','entrypoint','log_file') {
    if (-not $values.ContainsKey($name) -or -not $values[$name]) { throw "Schedule config is missing $name" }
}
$repoRoot = Split-Path -Parent (Split-Path -Parent (Resolve-Path -LiteralPath $ConfigPath))
$workingDir = if ([System.IO.Path]::IsPathRooted($values.working_dir)) {
    [System.IO.Path]::GetFullPath($values.working_dir)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $repoRoot $values.working_dir))
}
$entry = Join-Path $workingDir $values.entrypoint
$log = Join-Path $workingDir $values.log_file
if (-not (Test-Path -LiteralPath $entry)) { throw "Entrypoint does not exist: $entry" }
if (-not (Test-Path -LiteralPath $values.python)) { throw "Python does not exist: $($values.python)" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $log) | Out-Null
# schtasks /TR rejects values longer than 261 chars, so the full command lives
# in a generated wrapper batch file and the task only references it by path.
$wrapper = Join-Path $PSScriptRoot 'run_paper_ingest.cmd'
$wrapperLines = @(
    '@echo off',
    "cd /d `"$workingDir`"",
    "set PAPER_INTAKE_DB_PATH=$workingDir\data\paper_catalog\catalog.sqlite3",
    "`"$($values.python)`" $($values.entrypoint) >> `"$log`" 2>&1"
)
[System.IO.File]::WriteAllLines($wrapper, $wrapperLines)
$taskCommand = "cmd.exe /c `"$wrapper`""
$arguments = @('/Create','/TN','PaperDailyIngest','/SC','DAILY','/ST',$values.time,'/F','/TR',$taskCommand)
if ($WhatIf) { [pscustomobject]@{ TaskName='PaperDailyIngest'; Arguments=$arguments; Command=$taskCommand } | ConvertTo-Json -Compress; exit 0 }
& schtasks.exe @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& schtasks.exe /Query /TN PaperDailyIngest /FO LIST
exit $LASTEXITCODE
