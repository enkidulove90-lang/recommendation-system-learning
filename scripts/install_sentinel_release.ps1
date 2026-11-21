param(
    [Parameter(Mandatory=$true)][string]$InstallBase,
    [Parameter(Mandatory=$true)][string]$DataRoot,
    [Parameter(Mandatory=$true)][string]$ExclusionsSource,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$sourceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$installBasePath = [IO.Path]::GetFullPath($InstallBase)
$dataRootPath = [IO.Path]::GetFullPath($DataRoot)
if (-not [IO.Path]::IsPathRooted($InstallBase) -or -not [IO.Path]::IsPathRooted($DataRoot)) {
    throw 'InstallBase and DataRoot must be absolute paths.'
}
foreach ($target in @($installBasePath, $dataRootPath)) {
    if ($target -match '(?i)([\\/])(?:\.worktrees|worktrees)([\\/])') {
        throw 'Installed code and persistent state must not be inside a worktree.'
    }
    if ($target.StartsWith($sourceRoot.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Installed code and state must not be inside the source checkout.'
    }
}
if (-not (Test-Path -LiteralPath $ExclusionsSource -PathType Leaf)) {
    throw 'ExclusionsSource does not exist.'
}
$commit = (& git -C $sourceRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $commit -notmatch '^[0-9a-f]{40}$') {
    throw 'Cannot identify a committed release.'
}
$release = Join-Path $installBasePath "releases/$commit"
$exclusionsTarget = Join-Path $dataRootPath 'exclusions.json'
if ($WhatIf) {
    [ordered]@{Commit=$commit; Release=$release; DataRoot=$dataRootPath;
               ExclusionsTarget=$exclusionsTarget; Source=$sourceRoot} | ConvertTo-Json -Compress
    exit 0
}
if (Test-Path -LiteralPath $release) {
    throw 'Immutable release already exists; choose a new commit.'
}
New-Item -ItemType Directory -Path $release -Force | Out-Null
New-Item -ItemType Directory -Path $dataRootPath -Force | Out-Null
$archive = Join-Path ([IO.Path]::GetTempPath()) ("paper-sentinel-$commit.zip")
try {
    & git -C $sourceRoot archive --format=zip --output=$archive $commit
    if ($LASTEXITCODE -ne 0) { throw 'git archive failed.' }
    Expand-Archive -LiteralPath $archive -DestinationPath $release
    Copy-Item -LiteralPath $ExclusionsSource -Destination $exclusionsTarget -Force
    Set-Content -LiteralPath (Join-Path $release 'RELEASE_COMMIT') -Value $commit -Encoding ascii
} finally {
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
}
[ordered]@{Commit=$commit; Release=$release; DataRoot=$dataRootPath;
           ExclusionsTarget=$exclusionsTarget} | ConvertTo-Json -Compress
