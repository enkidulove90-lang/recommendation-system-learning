param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action = "status"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RuntimeRoot = Join-Path $RepoRoot ".paper-work"
$PidFile = Join-Path $RuntimeRoot "remote-worker.pid"
$OutLog = Join-Path $RuntimeRoot "remote-worker.out.log"
$ErrLog = Join-Path $RuntimeRoot "remote-worker.err.log"
$EnvFile = Join-Path $RepoRoot ".env"

function Get-ConfiguredValue([string]$Name) {
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if (-not $value) { $value = [Environment]::GetEnvironmentVariable($Name, "User") }
    if (-not $value -and (Test-Path -LiteralPath $EnvFile)) {
        $line = Get-Content -LiteralPath $EnvFile | Where-Object {
            $_ -match "^\s*$([regex]::Escape($Name))\s*="
        } | Select-Object -Last 1
        if ($line) {
            $value = ($line -split "=", 2)[1].Trim().Trim('"').Trim("'")
        }
    }
    return $value
}

function Get-WorkerProcess {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $null }
    $rawPid = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    if ($rawPid -notmatch "^\d+$") { return $null }
    $process = Get-Process -Id ([int]$rawPid) -ErrorAction SilentlyContinue
    if (-not $process) { return $null }
    if ($process.ProcessName -notmatch "^(python|pythonw|python3|py)$") { return $null }
    return $process
}

function Show-Status {
    $process = Get-WorkerProcess
    if ($process) {
        Write-Output "RUNNING pid=$($process.Id)"
        Write-Output "stdout=$OutLog"
        Write-Output "stderr=$ErrLog"
        return
    }
    if (Test-Path -LiteralPath $PidFile) {
        Write-Output "STOPPED (stale PID file detected)"
    } else {
        Write-Output "STOPPED"
    }
}

function Start-Worker {
    if (Get-WorkerProcess) {
        Show-Status | Out-Default
        return
    }
    $required = @(
        "PAPER_INTAKE_API_BASE",
        "PAPER_INTAKE_WORKER_TOKEN",
        "MINERU_API_KEY",
        "DEEPSEEK_API_KEY",
        "NOTION_TOKEN",
        "NOTION_DATABASE_ID"
    )
    $missing = @($required | Where-Object { -not (Get-ConfiguredValue $_) })
    if ($missing.Count -gt 0) {
        throw "Missing configuration: $($missing -join ', ')"
    }
    foreach ($name in $required) {
        [Environment]::SetEnvironmentVariable($name, (Get-ConfiguredValue $name), "Process")
    }
    New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
    if (Test-Path -LiteralPath $PidFile) { Remove-Item -LiteralPath $PidFile -Force }
    $python = (Get-Command python -ErrorAction Stop).Source
    $process = Start-Process `
        -FilePath $python `
        -ArgumentList @("-m", "paper_intake", "remote-worker") `
        -WorkingDirectory $RepoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $OutLog `
        -RedirectStandardError $ErrLog `
        -PassThru
    Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ascii
    Start-Sleep -Seconds 3
    $process.Refresh()
    if ($process.HasExited) {
        $details = if (Test-Path -LiteralPath $ErrLog) {
            (Get-Content -LiteralPath $ErrLog -Tail 20) -join [Environment]::NewLine
        } else { "No stderr log was created." }
        throw "Worker exited during startup (exit=$($process.ExitCode)).`n$details"
    }
    Show-Status | Out-Default
}

function Stop-Worker {
    $process = Get-WorkerProcess
    if ($process) {
        Stop-Process -Id $process.Id
        $process.WaitForExit(10000) | Out-Null
        if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
        Write-Output "STOPPED pid=$($process.Id)"
    } else {
        Write-Output "STOPPED (no active worker)"
    }
    if (Test-Path -LiteralPath $PidFile) { Remove-Item -LiteralPath $PidFile -Force }
}

switch ($Action) {
    "start" { Start-Worker }
    "stop" { Stop-Worker }
    "status" { Show-Status | Out-Default }
    "restart" { Stop-Worker; Start-Worker }
}

