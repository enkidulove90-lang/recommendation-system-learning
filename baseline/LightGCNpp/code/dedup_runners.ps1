# dedup_runners.ps1 —— 修复版
# 杀掉后台框架对 run_idea2.py 起的重复副本(框架常起 2 份相互不可见的副本).
#
# 修复点(对应此前误杀合法训练树的 bug):
#   1) 只 dedupe "根" 训练进程 —— 即父进程命令行【不含】 run_idea2.py / main.py 的顶层副本.
#      run_idea2.py 自身的嵌套树(bash → orchestrator → worker → main.py)中,
#      worker / main.py 的父是 python, 一律排除, 绝不被当作去重候选.
#   2) 杀根时递归杀掉整棵子树(含其 worker / main.py), 不留孤儿.
#
# 分组键: --dataset --only --force_c --mm_reg --layer --epochs --seeds
# 每组只保留 PID 最小(最早)的根, 杀其余根 + 子树.

function Kill-Tree($rootPid) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$rootPid" -ErrorAction SilentlyContinue
    foreach ($c in $children) { Kill-Tree $c.ProcessId }
    try { Stop-Process -Id $rootPid -Force -ErrorAction Stop } catch { }
}

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*run_idea2.py*' }
if (-not $procs) { exit 0 }

# 仅"根"进程进入分组: 父不是 python run_idea2.py / main.py
$roots = @()
foreach ($p in $procs) {
    $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue
    $pcmd = if ($parent) { $parent.CommandLine } else { '' }
    if ($pcmd -notmatch 'run_idea2\.py|main\.py') { $roots += $p }
}

$groups = @{}
foreach ($p in $roots) {
    $c = $p.CommandLine
    $key = ""
    foreach ($flag in @('--dataset','--only','--force_c','--mm_reg','--layer','--epochs','--seeds')) {
        if ($c -match "$flag\s+(\S+)") { $key += "$flag=$($matches[1]);" }
    }
    if (-not $groups.ContainsKey($key)) { $groups[$key] = @() }
    $groups[$key] += $p
}

foreach ($k in $groups.Keys) {
    $g = $groups[$k] | Sort-Object ProcessId
    if ($g.Count -gt 1) {
        $keep = $g[0]
        Write-Output "DEDUP keep root PID=$($keep.ProcessId) key='$k' (roots=$($g.Count))"
        foreach ($p in $g[1..($g.Count - 1)]) {
            Write-Output "DEDUP kill root PID=$($p.ProcessId) key='$k' (tree)"
            Kill-Tree $p.ProcessId
        }
    }
}
