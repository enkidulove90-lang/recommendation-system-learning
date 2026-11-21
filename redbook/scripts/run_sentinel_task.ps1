[CmdletBinding()]
param(
    [ValidateSet("homepage", "xiaohongshu", "wechat")]
    [string]$Platform = "homepage",
    [switch]$NoDispatch,
    [string]$PythonPath = "",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
if (-not $PythonPath) {
    $PythonPath = (Get-Command python.exe -ErrorAction Stop).Source
}
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "Python executable not found: $PythonPath"
}

$arguments = @("-m", "redbook.sentinel", "run-once", "--platform", $Platform)
if ($NoDispatch) {
    $arguments += "--no-dispatch"
}
if ($WhatIf) {
    [pscustomobject]@{
        WorkingDirectory = $repoRoot
        PythonPath = $PythonPath
        Arguments = $arguments
    } | ConvertTo-Json -Compress
    exit 0
}

Push-Location -LiteralPath $repoRoot
try {
    & $PythonPath @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
