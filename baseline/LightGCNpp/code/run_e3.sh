#!/bin/bash
# E3: 对齐信号权重(mm_reg)扫描 —— 锁 force_c=0.8, 全模态, pr32.
# 目的: 验证 idea2 的增益是否对对比损失权重敏感(plateau 是否因对齐被压太弱).
#   调试理由: 默认 1e-3 下对齐项贡献过小, 接近纯 ID 基线(增益封顶 +4.5%~+6.9%);
#    需向上扫描看能否"拉起"对齐. 原 {1e-2,1e-1} 跨度太粗(跳过 3e-3/3e-2),
#    无法区分"平滑爬升(正则受限→继续加大)"还是"有甜点后崩塌(存在最优)".
#    故改为对数密扫 {3e-3,1e-2,3e-2,1e-1}; 如需观察过强崩塌可加 3e-1.
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh(已证伪).
# 资源纪律: 顺序跑(每个 mm_reg 经 launch_safe.sh 阻塞等待), 同时仅 1 个训练进程.
#   EP 默认 20(快读方向定位甜点); 定位后必须用 EP=50 复跑最优 1~2 个值, 与 E11(0.09004) 对齐比较:
#     EP=50 bash run_e3.sh
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
EP=${EP:-20}
PR=32
DS=amazon-baby-mmssl
FC=0.8
LOG=/tmp/phaseB_e3.log
echo "E3 mm_reg scan START $(date)  EP=$EP force_c=$FC pr$PR dataset=$DS" | tee -a "$LOG"
for MR in 3e-3 1e-2 3e-2 1e-1; do
  echo "=== E3 mm_reg=$MR ===" | tee -a "$LOG"
  bash launch_safe.sh --only idea2 --epochs "$EP" --dataset "$DS" \
      --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c "$FC" --mm_reg "$MR" | tee -a "$LOG"
done
echo "E3_DONE $(date)" | tee -a "$LOG"
