#!/bin/bash
# launch_safe.sh —— 安全启动单次 run_idea2.py.
# 后台拉起训练, 然后在 12s/25s/38s 调用 dedup_runners.ps1, 杀掉后台框架可能对同一命令
# 起的第二份副本(单实例纪律, 防并发 OOM —— 见 run_idea2.acquire_lock 注释).
# 用法: bash launch_safe.sh <run_idea2.py 的全部参数>
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE
HERE="C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
"$VENV_PY" run_idea2.py "$@" &
PID=$!
for T in 12 25 38; do
  "$VENV_PY" -c "import time; time.sleep($T)"
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HERE/dedup_runners.ps1" 2>/dev/null
done
wait $PID
