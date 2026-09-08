# run_e15_tf.ps1 - One-click E15-TE-free (TF group) 500-epoch full run on a persistent machine
# Usage:  powershell -ExecutionPolicy Bypass -File run_e15_tf.ps1
# Expect: ~3-5h per 2 seeds on the persistent box (same budget as A/T groups).

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

Write-Host "===== 1/3 Clean stale TF leftovers ====="
$dirs = @("$PSScriptRoot\outputs\amazon-baby-mmssl\TF_seed42",
          "$PSScriptRoot\outputs\amazon-baby-mmssl\TF_seed2025")
foreach ($d in $dirs) {
    if (Test-Path -LiteralPath $d) {
        Get-ChildItem -LiteralPath $d -Filter "SASRec*" -ErrorAction SilentlyContinue |
            ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -Confirm:$false }
        Write-Host "  cleaned: $d"
    }
}
$logs = Get-ChildItem "$PSScriptRoot\logs\e15_TF_seed*.log" -ErrorAction SilentlyContinue
if ($logs) { $logs | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -Confirm:$false }; Write-Host "  cleaned old TF logs" }

Write-Host "`n===== 2/3 Launch TF full run (500 ep x 2 seeds, ~3-5h) ====="
Write-Host "  config: lambda_uni/syn/red=0, lambda_comp=0.1, seeds 42,2025"
& .\run_e15.ps1 -Groups TF -LambdaComp 0.1 -Seeds "42,2025"

Write-Host "`n===== 3/3 JUDGMENT (Recall@20 at best epoch, compare per seed) ====="
Write-Host "  seed42  : A=0.0408  T=0.0361  -> TF must beat BOTH"
Write-Host "  seed2025: A=0.0377  T=0.0393  -> TF must beat BOTH"
Write-Host "  both seeds beat -> claim-2 holds (PRISM line continues: E16/E17)"
Write-Host "  otherwise -> E15 closes as negative (PRISM = fusion regularizer only)"
