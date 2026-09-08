#!/bin/bash
# Phase B 启动器 —— 放弃学 conf, 锁 force_c=0.8, 转"对齐/特征验证"
#
# 决策依据(用户 2026-08-10):
#   - 学 conf 使档位区分度消失(learned c 把所有 force_c 档塌成同一行为)
#   - AL 对偶 ≈ 软惩罚 λ=1 (E6 增广拉格朗日无增量价值)
#   => 放弃 E6/idea3 的自适应 c 学习, 冻结 c=0.8(E1 经验最优 +4.5%),
#      转 Phase B: 验证并强化"固定 c=0.8 + 三级对齐"这一最终方法本身。
#
# 口径铁律: 一律 --mm_proj_refresh 32 (_pr32); 绝不 --mm_eval_fresh。
# 靶子: idea2_mm_fc0.8_pr32 = 0.08740 (logs/e6_analysis.json, A0 同口径重测)。
#
# 当前批次 = E8 单模态拆解(image-only / text-only),
#   定位哪种模态驱动了 +4.5%, 决定后续是投图像特征(E10)还是文本对齐(E3)。
#   实现: 把单模态 .npy 放进独立 data 子目录, contrastive_loss 在 1 类型时自动返 0(安全)。
#
# 扩展位(后续批次, 按需取消注释并由对应 hook 支持):
#   E11 长训练:   EP=50 bash run_phaseB.sh            (同配置更久, 看是否收敛更高)
#   E3  对齐信号: 需 run_idea2.py 转发 --mm_reg 扫描 {1e-2,1e-1}
#   E12 层数:     需 run_idea2.py 转发 --layer 扫 {2,3}
#   E9  对齐探针: 无训练诊断(pid_diagnostic.py CCA/MI)
#   E10 真实特征: fetch_mm_data.py + item 映射(沙箱可能无外网)
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

LOG=/tmp/phaseB.log
EP=${EP:-20}
PR=32
DS_IMG=amazon-baby-mmssl_imgonly
DS_TXT=amazon-baby-mmssl_txtonly

echo "PHASEB_START $(date)  (EP=$EP PR=$PR force_c=0.8)" > "$LOG"

run () {   # run <tag> <dataset> <seeds> <extra...>
  local tag="$1" ds="$2" seeds="$3"; shift 3
  echo "--- $tag ($ds) seeds=$seeds START $(date) ---" >> "$LOG"
  "$VENV_PY" run_idea2.py --only idea2 --epochs "$EP" --dataset "$ds" \
      --seeds "$seeds" --mm_proj_refresh "$PR" --force_c 0.8 "$@" >> "$LOG" 2>&1
  echo "--- $tag END $(date) rc=$? ---" >> "$LOG"
}

# ===== E8 单模态拆解(定位增益来源) =====
run "E8_imgonly" "$DS_IMG" 2024,2025,2026
run "E8_txtonly" "$DS_TXT" 2024,2025,2026

echo "PHASEB_E8_DONE $(date)" >> "$LOG"
