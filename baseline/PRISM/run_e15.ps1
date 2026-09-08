# E15 训练启动器（PowerShell；torch 在 Git Bash 下 segfault，必须 PowerShell）
# 用 baseline/PRISM 原码（仅 P1-P5 最小补丁 + E14-ter 互补损失钩子）在 amazon-baby-mmssl 复现论文增益。
# 组：
#   T  (treatment 默认 λ=0.1，L_syn 开)
#   A  (ablation λ=0)
#   V  (vanilla id-only, --disable_mm)
#   TE (T + E14-ter 互补损失 λ_comp，保留 L_syn) —— 合成机制预测 FAIL（同根因 c_syn 与 uni 相关）
#   TF (关 L_syn + λ_comp，互补路由)           —— 合成侧 ter_free 对应，唯一可能胜出变体
# 用法：
#   .\run_e15.ps1 -Groups T,A                 # 原复现
#   .\run_e15.ps1 -Groups TE,TF -LambdaComp 0.1   # E14-ter 真实裁决（带/关 L_syn）
#   .\run_e15.ps1 -Groups T,A,TE,TF -Seeds "42,2025" -LambdaComp 0.1
# 注意：-Seeds 必须加引号（如 "42,2025"），否则 PowerShell 会把逗号当成数组构造符。

param(
    [string]$Groups = "T,A",
    [string]$Seeds = "42,2025",
    [string]$LambdaComp = "0.1",
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Continue"
$py = "C:\Program Files\Python311\python.exe"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# 归一化：若 -Seeds/-Groups 未加引号被当成数组，先 join 回字符串再按逗号 split
$Seeds = (@($Seeds) -join ',')
$Groups = (@($Groups) -join ',')

$data_dir = "./data/amazon-baby-mmssl/"
$img = "data/amazon-baby-mmssl/image_features_amazon-baby-mmssl.pt"
$txt = "data/amazon-baby-mmssl/text_features_amazon-baby-mmssl.pt"

function Run-Group {
    param($group, $seed)
    $g = ($group.ToString()).Trim().ToUpper()
    $lc = $script:LambdaComp
    $extra = @()
    if ($g -eq 'A')  { $extra = @('--lambda_uni','0','--lambda_syn','0','--lambda_red','0') }
    elseif ($g -eq 'V') { $extra = @('--disable_mm') }
    elseif ($g -eq 'TE') { $extra = @('--lambda_comp',$lc) }
    elseif ($g -eq 'TF') { $extra = @('--lambda_uni','0','--lambda_syn','0','--lambda_red','0','--lambda_comp',$lc) }

    $out_dir = "outputs/amazon-baby-mmssl/$($group)_seed$($seed)"
    $log = "logs/e15_$($group)_seed$($seed).log"
    New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
    $allargs = @(
        "main.py","--model_name","SASRec","--data_name","amazon-baby-mmssl","--no_cuda",
        "--image_emb_dim","4096","--text_emb_dim","384",
        "--epochs","500","--patience","10","--log_freq","5","--seed",$seed,
        "--data_dir",$data_dir,"--output_dir",$out_dir,
        "--image_emb_path",$img,"--text_emb_path",$txt
    ) + $extra
    Write-Host "===== START group=$group seed=$seed out=$out_dir ====="
    Write-Host "  resolved extra args: $($extra -join ' ')"
    if ($script:DryRun) {
        Write-Host "  [DRYRUN] would run: $py $($allargs -join ' ')"
        return
    }
    # 用 * 全流重定向到 log，避免 tqdm 的 stderr 触发 PowerShell 误判进程失败
    & $py @allargs *> $log
    Write-Host "===== END   group=$group seed=$seed (see $log) ====="
}

foreach ($g in $Groups.Split(',')) {
    foreach ($s in $Seeds.Split(',')) {
        Run-Group -group $g.Trim() -seed $s.Trim()
    }
}

# 汇总判定
Write-Host "`n===== AGGREGATE (best Recall@20 per group) ====="
foreach ($g in $Groups.Split(',')) {
    foreach ($s in $Seeds.Split(',')) {
        $log = "logs/e15_$($g.Trim())_seed$($s.Trim()).log"
        if (Test-Path $log) {
            $rec = Select-String -Path $log -Pattern "Recall@20" | Select-Object -Last 1
            Write-Host "$($g.Trim()) seed=$($s.Trim()): $rec"
        }
    }
}
