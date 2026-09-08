#!/bin/bash
# E2: idea2 + --mm_conf_reg 0 (关掉 (1-|2c-1|) 把 c 往 0 推的正则)
# 3 seed x 20 epoch, amazon-baby-mmssl. 跑完自动后处理(取 conf_mean@最优test epoch).
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
echo "E2_CONFREG0_START $(date)" > /tmp/e2_confreg0.log
"$VENV_PY" run_idea2.py --only idea2 --epochs 20 --seeds 2024,2025,2026 --mm_conf_reg 0 --dataset amazon-baby-mmssl >> /tmp/e2_confreg0.log 2>&1
echo "E2_CONFREG0_TRAIN_END $(date) rc=$?" >> /tmp/e2_confreg0.log
"$VENV_PY" analyze_e2.py >> /tmp/e2_confreg0.log 2>&1
echo "E2_ANALYSIS_DONE $(date)" >> /tmp/e2_confreg0.log
