#!/bin/bash
# E11 超长训练 —— 锁 force_c=0.8, 全模态(amazon-baby-mmssl), EP=100(默认, EP=200 可覆盖)
#
# 目的: 在 E11(EP=50) 验证 c=0.8 是否 plateau 之后, 进一步把训练拉到超长,
#   确认"冻结 c=0.8 + 三级对齐"的最终方法到底有没有更多收敛空间。
#   - 若 50ep 已 plateau(≈0.08740) 而 100ep 仍不涨 => 对齐模块硬上限, 转 E10/E3/E7。
#   - 若 100ep 继续上爬 => 简单冻结法只是欠训练, 统一拉长 EP 即可。
#
# 资源纪律(路线图 §5.6): 本机同时最多 1 个训练进程(各 ~1.1GB, 空闲<2GB 触发 OOM 静默杀)。
#   => 本脚本先用看门狗阻塞, 等 E11(EP=50) 写出 PHASEB_E11_DONE 后才开训, 绝不并发。
#
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh(已证伪)。
# 靶子: idea2_mm_fc0.8_pr32 = 0.08740 (logs/e6_analysis.json A0 同口径重测)。
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

LOG=/tmp/phaseB_e11_ultra.log
E11_LOG=/tmp/phaseB_e11.log
EP=${EP:-100}
PR=32
DS_FULL=amazon-baby-mmssl
MARKER="PHASEB_E11_DONE"

echo "E11_ULTRA_WAIT $(date)  (EP=$EP PR=$PR force_c=0.8 dataset=$DS_FULL, waits for $MARKER)" > "$LOG"

# 看门狗: 轮询 E11 收官标记(最多等 18h, 防异常挂死); 命中即退出让 bash 继续开训
"$VENV_PY" - "$E11_LOG" "$MARKER" <<'PY'
import sys, time, os
e11_log, marker = sys.argv[1], sys.argv[2]
cap, elapsed = 18*3600, 0
while elapsed < cap:
    try:
        with open(e11_log, encoding="utf-8", errors="ignore") as f:
            if marker in f.read():
                break
    except FileNotFoundError:
        pass
    time.sleep(60); elapsed += 60
else:
    print("E11_ULTRA_WAIT_TIMEOUT: E11 未在 18h 内收官, 放弃自动启动"); sys.exit(2)
PY
echo "E11_ULTRA_START_TRAIN $(date)" >> "$LOG"

echo "--- E11_ultra (amazon-baby-mmssl) seeds=2024,2025,2026 START $(date) ---" >> "$LOG"
"$VENV_PY" run_idea2.py --only idea2 --epochs "$EP" --dataset "$DS_FULL" \
    --seeds 2024,2025,2026 --mm_proj_refresh "$PR" --force_c 0.8 >> "$LOG" 2>&1
echo "--- E11_ultra END $(date) rc=$? ---" >> "$LOG"

echo "PHASEB_E11_ULTRA_DONE $(date)" >> "$LOG"
