#!/bin/bash
# E12: GCN 层数(layer)扫描 —— 锁 force_c=0.8, 全模态, pr32.
# 目的: 验证 idea2 的增益是否对图卷积深度敏感(layer=2 是否已够, 还是更深更好).
#   调试理由: LightGCN 在 2~3 层后易过平滑(over-smoothing), 默认 nl2 是已知甜点.
#    原 {3,4} 缺过平滑探针, 无法区分"3 最优/更深变差"与"仍在爬升需 5+".
#    故加 nl=5 作过平滑探针: 若 3→4→5 单调下滑, 说明瓶颈不在深度→转 E3/E7;
#    若 5 仍涨, 说明深度确有空间. (可选: 加 nl=1 验 2 是否已过深, 但改 baseline 对比, 默认不加)
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh(已证伪).
# 资源纪律: 顺序跑, 同时仅 1 个训练进程. layer=2 已由 E11/ultra 覆盖, 这里扫 {3,4,5}.
#   EP 默认 20(快读方向); 与 E11 对齐比较用 EP=50:
#     EP=50 bash run_e12.sh
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
EP=${EP:-50}
PR=32
DS=amazon-baby-mmssl
FC=0.8
LOG=/tmp/phaseB_e12.log
echo "E12 layer scan START $(date)  EP=$EP force_c=$FC pr$PR dataset=$DS" >> "$LOG"
for LY in 4 5; do
  echo "=== E12 layer=$LY ===" >> "$LOG"
  bash launch_safe.sh --only idea2 --epochs "$EP" --dataset "$DS" \
      --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c "$FC" --layer "$LY" >> "$LOG"
done
echo "E12_DONE $(date)" >> "$LOG"
