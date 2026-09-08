#!/bin/bash
# E13: GCN 层数深度验证 —— 锁 force_c=0.8, 仅 nl4, 全模态, pr32, EP=100.
# 目的: 与 E11(nl2@EP=100=0.09039) 构成同预算单变量对照, 判深度是否真正抬高天花板.
#   依据(E12 结论): nl4@EP=50 均值 0.09071 > E11 但仅 0.6σ 不显著, 且 nl4 有 seed 在 ep50 边界取最优
#   → EP=100 仍有上探空间. 故补 nl4@EP=100 单档深训.
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh(已证伪).
# 资源纪律: 顺序跑, 同时仅 1 个训练进程. 只跑 nl4(单档, 与 E11 同预算对照).
#   EP 默认 100(同 E11 公平). 启动: bash run_e13.sh
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
EP=${EP:-100}
PR=32
DS=amazon-baby-mmssl
FC=0.8
LOG=/tmp/phaseC_e13.log
echo "E13 nl4@EP=100 START $(date)  EP=$EP force_c=$FC pr$PR dataset=$DS" >> "$LOG"
for LY in 4; do
  echo "=== E13 layer=$LY ===" >> "$LOG"
  bash launch_safe.sh --only idea2 --epochs "$EP" --dataset "$DS" \
      --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c "$FC" --layer "$LY" >> "$LOG"
done
echo "E13_DONE $(date)" >> "$LOG"
