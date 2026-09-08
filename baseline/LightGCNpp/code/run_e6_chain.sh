#!/bin/bash
# 等决断跑(20ep, seed2024, pr32)退出后, 自动接力启动 E6 全量队列。
#
# 用法: bash run_e6_chain.sh <要等待的PID>
#
# 为什么可以放心接力(而不是等人看完决断结果再手动起):
#   机制判据在 ep5 已经 PASS(FRESH conf=0.800 / std=0.256 / budget_loss≈0),
#   而后续 4 个 stage 无论 E6 在 R@20 上最终输赢, 产出的证据都是结论必需的:
#     A0 = 同口径 fc0.8 靶子(没有它, Stage A 的数字无法解读)
#     B  = 双向控制(t=0.2 能把 c 压下去 -> 排除"惩罚强度不对"的混淆)
#     C  = 软惩罚欠冲量, 用来反推 BPR 等效下压强度 A
#   所以最坏情况也不是白跑。
#
# 环境坑(踩过, 别再踩):
#   1. 本 bash 无 sleep / 无 nohup -> 用 python 的 time.sleep 顶替
#   2. MSYS 会把 `tasklist /FI` 的 /FI 转成路径 F:\I, 过滤器静默失效并永远返回空,
#      导致"误判进程已退出"立刻接力 -> 必须改用 awk 匹配第 2 列(PID)
#   3. 杀进程链时 Windows 上 python 启动器会多套一层, 只杀叶子/只杀根都不彻底
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"

WAIT_PID="${1:?用法: bash run_e6_chain.sh <PID>}"
LOG=/tmp/e6_chain.log
MAX_ITER=180        # 180 * 20s = 60 min 上限
DECIDE_LOG="logs/run_idea2_mm_mcr0_mb0.8l1d0.05_pr32_seed2024.log"

echo "CHAIN_START $(date)  等待 PID=$WAIT_PID" > "$LOG"

alive () { tasklist | awk -v p="$WAIT_PID" '$2==p{f=1} END{exit !f}'; }

i=0
while [ "$i" -lt "$MAX_ITER" ]; do
  if alive; then
    i=$((i + 1))
    "$VENV_PY" -c "import time;time.sleep(20)"
  else
    break
  fi
done

if alive; then
  echo "CHAIN_TIMEOUT $(date)  PID=$WAIT_PID 超过 60min 仍存活, 放弃接力" >> "$LOG"
  exit 1
fi

echo "CHAIN_PID_GONE $(date)  等待了约 $((i * 20))s" >> "$LOG"

# 决断跑的成绩记录一笔(不作为是否接力的门槛 —— 即使它挂了,
# run_e6_budget.sh 的 Stage A 会检测到日志不完整并自动重跑 seed2024)
if [ -f "$DECIDE_LOG" ]; then
  if grep -q "EPOCH\[20/20\]" "$DECIDE_LOG"; then
    echo "决断跑: 完整跑完 20 epoch" >> "$LOG"
  else
    echo "决断跑: !! 未跑满 20 epoch, Stage A 会自动重跑 seed2024" >> "$LOG"
  fi
  {
    echo "--- 决断跑 FRESH conf 轨迹 ---"
    grep "FRESH conf_mean" "$DECIDE_LOG" | sed 's/\x1b\[[0-9;]*m//g'
  } >> "$LOG" 2>&1
fi

echo "E6_FULL_LAUNCH $(date)" >> "$LOG"
exec bash run_e6_budget.sh
