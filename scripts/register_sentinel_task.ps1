param(
    [string]$TaskName = 'Paper Sentinel Discovery',
    [ValidateSet('homepage', 'xiaohongshu', 'wechat')]
    [string]$Platform = 'homepage',
    [switch]$NoDispatch,
    [string]$PythonPath = 'python',
    [string]$InstallRoot = '',
    [string]$DataRoot = '',
    [string]$ConfigPath = '',
    [string]$ExclusionsPath = '',
    [ValidatePattern('^([01][0-9]|2[0-3]):[0-5][0-9]$')]
    [string]$At = '11:00',
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
if (-not $InstallRoot -and -not $WhatIf) {
    throw 'Actual task registration requires an independent InstallRoot.'
}
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$runner = Join-Path $PSScriptRoot 'run_sentinel_task.ps1'
if ($InstallRoot) {
    $projectRoot = (Resolve-Path -LiteralPath $InstallRoot).Path
    if ($projectRoot -match '(?i)([\\/])(?:\.worktrees|worktrees)([\\/])') {
        throw 'InstallRoot must not be a worktree.'
    }
    if (-not $DataRoot -or -not $ConfigPath -or -not $ExclusionsPath) {
        throw 'Stable registration requires DataRoot, ConfigPath, and ExclusionsPath.'
    }
    $runner = Join-Path $projectRoot 'scripts/run_sentinel_task.ps1'
}
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw 'Sentinel task runner is missing.'
}

$actionArgs = '-NoProfile -ExecutionPolicy Bypass -File "' + $runner + '" -Platform ' + $Platform
$actionArgs += ' -PythonPath "' + $PythonPath + '"'
if ($InstallRoot) {
    $actionArgs += ' -AppRoot "' + $projectRoot + '"'
    $actionArgs += ' -DataRoot "' + $DataRoot + '"'
    $actionArgs += ' -ConfigPath "' + $ConfigPath + '"'
    $actionArgs += ' -ExclusionsPath "' + $ExclusionsPath + '"'
}
if ($NoDispatch) {
    $actionArgs += ' -NoDispatch'
}

if ($WhatIf) {
    [ordered]@{
        TaskName = $TaskName
        Schedule = $At
        NoDispatch = [bool]$NoDispatch
        WorkingDirectory = $projectRoot
        ActionArguments = $actionArgs
    } | ConvertTo-Json -Compress
    exit 0
}

$triggerTime = [datetime]::ParseExact($At, 'HH:mm', [Globalization.CultureInfo]::InvariantCulture)
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $actionArgs -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $triggerTime
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Principal $principal -Force | Out-Null
$registered = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
if ($registered.Actions[0].Arguments -ne $actionArgs) {
    throw 'Registered task arguments do not match the requested action.'
}
[ordered]@{
    TaskName = $TaskName
    State = [string]$registered.State
    Schedule = $At
    NoDispatch = [bool]$NoDispatch
    WorkingDirectory = $projectRoot
    ActionArguments = $actionArgs
} | ConvertTo-Json -Compress
