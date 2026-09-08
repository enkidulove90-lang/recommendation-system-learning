#!/bin/bash
# E6 接力启动器
# 作用: 等诊断跑(seed9998, 10ep)退出后, 自动开跑正式 E6 全量(run_e6_budget.sh)
# 注意: 本 bash 环境无 `sleep`、无 `nohup`, 轮询用 venv python 的 time.sleep 代替
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
WAIT_PID="${1:-10160}"
CUT=/tmp/e6_cutover.log

echo "E6_CUTOVER_START $(date) waiting_pid=$WAIT_PID" > "$CUT"

# 最多等 30 分钟(90 * 20s), 超时也照常启动(诊断跑挂了不该阻塞正式实验)
for i in $(seq 1 90); do
  # 坑: Git Bash(MSYS) 会把 `/FI` 当路径转换成 `F:\I`, tasklist 过滤器直接失效 ->
  # grep 必空 -> 误判"进程已退出"并立即接力. 改用无参 tasklist + awk 精确比对第 2 列 PID.
  if ! tasklist 2>/dev/null | awk -v p="$WAIT_PID" '$2==p{f=1} END{exit !f}'; then
    echo "PID $WAIT_PID gone at $(date) (poll #$i)" >> "$CUT"
    break
  fi
  "$VENV_PY" -c "import time;time.sleep(20)"
done

echo "E6_LAUNCH $(date)" >> "$CUT"
bash run_e6_budget.sh >> "$CUT" 2>&1
echo "E6_CUTOVER_END $(date) rc=$?" >> "$CUT"
