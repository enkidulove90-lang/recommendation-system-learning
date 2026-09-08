# guard_ultra.ps1 —— E11_ultra 重复启动守卫.
# 返回 0 = 可启动; 返回 2 = 已有同键根训练在跑(禁止启动); 返回 3 = 已完成(禁止启动).
# 目的: 防止自动化每小时重触发时, 新副本在去重生效前就启动并覆盖/归档正在写的 eval txt.

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*run_idea2.py*' }
$roots = @()
foreach ($p in $procs) {
    $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue
    $pcmd = if ($parent) { $parent.CommandLine } else { '' }
    if ($pcmd -notmatch 'run_idea2\.py|main\.py') { $roots += $p }
}
$ultraKey = '*--only idea2*--epochs 100*--dataset amazon-baby-mmssl*--seeds 2024,2025,2026*--force_c 0.8*'
$found = $roots | Where-Object { $_.CommandLine -like $ultraKey }
if ($found) { Write-Output "GUARD_BLOCK_RUNNING PID=$($found[0].ProcessId)"; exit 2 }

# 完成判定: seed2024 eval txt 含 >=20 个 test 行(EP=100, 每 5ep 一评)即视为已完成
$logdir = 'C:\Users\xu.yan1\papers\recommendation-system-learning\baseline\LightGCNpp\code\logs'
$txt = Join-Path $logdir 'amazon-baby-mmssl_seed2024_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_gamma0.2_nl2_mm_mr0.001_mt0.1_fc0.8_pr32.txt'
if (Test-Path $txt) {
    $n = (Get-Content $txt | Where-Object { $_ -match '^\s*test\s' }).Count
    if ($n -ge 20) { Write-Output "GUARD_BLOCK_DONE testlines=$n"; exit 3 }
}
exit 0
