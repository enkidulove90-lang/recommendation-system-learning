#!/bin/bash
# E11 长训练 —— 锁 force_c=0.8, 全模态(amazon-baby-mmssl), EP=50
#
# 目的(用户 2026-08-10 决策): 放弃学 conf / 锁 c=0.8 后,
#   用更长训练判 c=0.8 是"天花板"( plateau ≈ 0.08740 )还是"地板"(仍在上爬)。
#   - 若 50ep 明显高于 0.08740 => 简单冻结法有效, 只是欠训练, 后续统一拉长 EP。
#   - 若 plateau 在 0.08740 => 对齐模块本身有硬上限, 投入方向转 E10(真特征)/E3(对齐权重)/E7(逐物品预算)。
#
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh(已证伪)。
# 靶子: idea2_mm_fc0.8_pr32 = 0.08740 (3-seed 均值, logs/e6_analysis.json A0 同口径重测)。
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

LOG=/tmp/phaseB_e11.log
EP=${EP:-50}
PR=32
DS_FULL=amazon-baby-mmssl

echo "E11_START $(date)  (EP=$EP PR=$PR force_c=0.8 dataset=$DS_FULL)" > "$LOG"

echo "--- E11_full (amazon-baby-mmssl) seeds=2024,2025,2026 START $(date) ---" >> "$LOG"
"$VENV_PY" run_idea2.py --only idea2 --epochs "$EP" --dataset "$DS_FULL" \
    --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c 0.8 >> "$LOG" 2>&1
echo "--- E11_full END $(date) rc=$? ---" >> "$LOG"

echo "PHASEB_E11_DONE $(date)" >> "$LOG"
