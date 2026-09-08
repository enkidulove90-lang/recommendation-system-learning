#!/bin/bash
# E11 超长训练(经 launch_safe.sh, 带去重 + 启动守卫) —— 锁 force_c=0.8, 全模态, EP=100
# 修复:
#   - 此前直接拉 run_idea2.py 不走 launch_safe.sh, 后台框架起的 2 份副本无去重 → 互相抢资源被静默 kill,
#     且 run_idea2.py 不校验退出码, 把截断结果当终值写库 (seed2024 仅跑到 ~10ep 即被记为完成).
#   - 现统一经 launch_safe.sh(12/25/38s 调 dedup 杀副本), 并加 guard_ultra.ps1 防自动化每小时重触发竞态.
# 资源纪律: 单进程; 空闲>2GB 可开训. 口径铁律: --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh.
# run_idea2.py 会自动把同名 E11(EP=50) eval txt / per-seed log 归档到 *.prevMMDDHHMMSS, 旧结果不丢.
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
HERE="C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
EP=${EP:-100}
PR=32
DS_FULL=amazon-baby-mmssl
LOG=/tmp/phaseB_e11_ultra.log

# 启动守卫: 已有同键根训练 / 已完成 → 禁止重复启动
if ! powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HERE/guard_ultra.ps1"; then
  echo "--- E11_ultra GUARD BLOCK $(date) ---" >> "$LOG"
  exit 0
fi

echo "--- E11_ultra (EP=$EP PR=$PR force_c=0.8 dataset=$DS_FULL) START $(date) ---" >> "$LOG"
bash launch_safe.sh --only idea2 --epochs "$EP" --dataset "$DS_FULL" \
    --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c 0.8 >> "$LOG" 2>&1
echo "--- E11_ultra END $(date) rc=$? ---" >> "$LOG"
echo "PHASEB_E11_ULTRA_DONE $(date)" >> "$LOG"
