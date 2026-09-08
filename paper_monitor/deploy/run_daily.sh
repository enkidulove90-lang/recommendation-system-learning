#!/usr/bin/env bash
# 每日摄入调度脚本（设计文档§6 调度）。
# 用法: bash paper_monitor/deploy/run_daily.sh
# 依赖: 已创建 venv 且安装 pyalex/semanticscholar/requests/pytest
set -euo pipefail

# ---- 可改：指向你的 python / venv ----
PY="${PM_PYTHON:-python}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "[run_daily] $(date -u +%FT%TZ) 开始摄入 DAG"
"$PY" -m paper_monitor.cli ingest --limit "${PM_MAX_PER_SOURCE:-200}"
echo "[run_daily] 摄入完成，统计如下"
"$PY" -m paper_monitor.cli analyze --limit 10
echo "[run_daily] done"
