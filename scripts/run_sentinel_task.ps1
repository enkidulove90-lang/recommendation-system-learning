param(
    [ValidateSet('homepage', 'xiaohongshu', 'wechat')]
    [string]$Platform = 'homepage',
    [switch]$NoDispatch,
    [string]$PythonPath = 'python',
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$pythonArgs = @('-m', 'redbook.sentinel', 'run-once', '--platform', $Platform)
if ($NoDispatch) {
    $pythonArgs += '--no-dispatch'
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
