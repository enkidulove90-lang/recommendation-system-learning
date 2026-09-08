#!/bin/bash
# 看守脚本: 等 fc1.0-s2026 训练(29488)结束后, 杀掉 run_e1_missing.sh 的 bash(29356)
# 阻止 fc0.5 启动, 并接力启动 E2 (idea2 + --mm_conf_reg 0, 3 seed)。
# 由自动化在后台拉起, 精确在 ~14:17 切断队列。
TRAIN_PID=29488
BASH_PID=29356
LOG=/tmp/e2_cutover.log
echo "E2_CUTOVER_WATCHER_START $(date)" > "$LOG"

# 等 fc1.0-s2026 训练进程退出(兜底: 最多等 150 分钟)
DEADLINE=$(date -d '+150 minutes' +%s 2>/dev/null || echo 9999999999)
while tasklist /FI "PID eq $TRAIN_PID" 2>/dev/null | grep -q "$TRAIN_PID"; do
  now=$(date +%s)
  if [ "${now:-0}" -gt "$DEADLINE" ]; then echo "WATCHER TIMEOUT, 强制 cutover" >> "$LOG"; break; fi
  sleep 15
done
echo "TRAIN_PID $TRAIN_PID exited/killed at $(date)" >> "$LOG"

# 杀掉 run_e1_missing.sh 的 bash, 阻止 fc0.5 启动
if tasklist /FI "PID eq $BASH_PID" 2>/dev/null | grep -q "$BASH_PID"; then
  taskkill /PID $BASH_PID /F >> "$LOG" 2>&1
  echo "killed bash $BASH_PID" >> "$LOG"
else
  echo "bash $BASH_PID 已不在, 跳过" >> "$LOG"
fi
sleep 4

# 安全阀: 杀掉任何已冒头的 fc0.5 训练进程
powershell -NoProfile -ExecutionPolicy Bypass -File "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code/kill_fc05.ps1" >> "$LOG" 2>&1
sleep 2

# 接力启动 E2: 用 exec 让本进程 PID 直接变成 E2 运行器,
# 避免后台框架在 watcher 退出时连坐杀掉 E2 子进程。
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
echo "E2_LAUNCHED $(date)" >> "$LOG"
exec bash run_e2_confreg0.sh
