param(
    [ValidateSet('homepage', 'xiaohongshu', 'wechat')]
    [string]$Platform = 'homepage',
    [switch]$NoDispatch,
    [string]$PythonPath = 'python',
    [string]$AppRoot = '',
    [string]$DataRoot = '',
    [string]$ConfigPath = '',
    [string]$ExclusionsPath = '',
    [string]$EnvFilePath = '',
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
if ($EnvFilePath) {
    if (-not (Test-Path -LiteralPath $EnvFilePath -PathType Leaf)) {
        throw 'EnvFilePath does not exist.'
    }
    $resolvedEnvFile = (Resolve-Path -LiteralPath $EnvFilePath).Path
    if ($explicitAppRoot -and $resolvedEnvFile -match '(?i)([\\/])(?:\.worktrees|worktrees)([\\/])') {
        throw 'EnvFilePath must be outside a worktree for an installed release.'
    }
}

if ($WhatIf) {
    $preview = [ordered]@{
        WorkingDirectory = $projectRoot
        PythonPath = $PythonPath
        Arguments = $pythonArgs
    }
    if ($EnvFilePath) { $preview.EnvFilePath = $resolvedEnvFile }
    $preview | ConvertTo-Json -Compress -Depth 3
    exit 0
}

Push-Location -LiteralPath $projectRoot
try {
    if ($EnvFilePath) {
        foreach ($line in [IO.File]::ReadAllLines($resolvedEnvFile, [Text.Encoding]::UTF8)) {
            if (-not $line.Trim() -or $line.TrimStart().StartsWith('#')) { continue }
            if ($line -notmatch '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
                throw 'EnvFilePath contains an unsupported assignment.'
            }
            $name = $Matches[1]
            $value = $Matches[2].Trim()
            if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                    ($value.StartsWith("'") -and $value.EndsWith("'")))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
    & $PythonPath @pythonArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
