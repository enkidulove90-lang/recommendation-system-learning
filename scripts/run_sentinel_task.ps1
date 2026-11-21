param(
    [ValidateSet('homepage', 'xiaohongshu', 'wechat')]
    [string]$Platform = 'homepage',
    [switch]$NoDispatch,
    [string]$PythonPath = 'python',
    [string]$AppRoot = '',
    [string]$DataRoot = '',
    [string]$ConfigPath = '',
    [string]$ExclusionsPath = '',
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$explicitAppRoot = [bool]$AppRoot
if ($explicitAppRoot) {
    $projectRoot = (Resolve-Path -LiteralPath $AppRoot).Path
    if ($projectRoot -match '(?i)([\\/])(?:\.worktrees|worktrees)([\\/])') {
        throw 'AppRoot must be an installed release, not a worktree.'
    }
}
$pythonArgs = @('-m', 'redbook.sentinel', 'run-once', '--platform', $Platform)
if ($NoDispatch) {
    $pythonArgs += '--no-dispatch'
}
if ($DataRoot) {
    $pythonArgs += @('--data-root', $DataRoot)
}
if ($ConfigPath) {
    $pythonArgs += @('--config', $ConfigPath)
}
if ($ExclusionsPath) {
    if (-not (Test-Path -LiteralPath $ExclusionsPath -PathType Leaf)) {
        throw 'ExclusionsPath does not exist.'
    }
    $pythonArgs += @('--exclusions', $ExclusionsPath)
}

if ($WhatIf) {
    [ordered]@{
        WorkingDirectory = $projectRoot
        PythonPath = $PythonPath
        Arguments = $pythonArgs
    } | ConvertTo-Json -Compress -Depth 3
    exit 0
}

Push-Location -LiteralPath $projectRoot
try {
    & $PythonPath @pythonArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
