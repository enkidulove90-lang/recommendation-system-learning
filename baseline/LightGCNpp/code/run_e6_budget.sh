#!/bin/bash
# E6: 全局预算约束 (batch-mean budget on the G3 confidence gate)
#
# 背景链条:
#   E1  force_c=0.8 冻结融合 -> R@20 0.08798 (+4.5%)  => 多模态特征本身有用
#   E2  mm_conf_reg=0        -> c 塌到 0.006, R@20 0.0847 (-3.7% vs fc0.8)
#                            => conf_reg 非元凶, BPR 局部梯度自己就要丢弃多模态
#   E6  用全局预算把 mean(c) 顶在 c_target, 同时保留逐物品分化(自适应应优于冻结)
#
# 机制选择(重要):
#   固定 lambda 的二次惩罚是**软**惩罚, 驻点 c_bar = t - A/(2*lambda), A=BPR 等效下压强度.
#   _smoke_e6_budget.py 实测与解析解三位小数吻合 => 只扫固定 lambda 会系统性欠冲,
#   可能得到 "conf_mean<0.6 -> E6 无效" 的假阴性. 故主实验用增广拉格朗日(--mm_budget_dual),
#   对偶乘子自适应, 精确命中 t 且与 A 无关(实测 A 翻 4 倍仍稳在 0.7997).
#
# 训练/评测口径(--mm_proj_refresh 32, 阻断级修正):
#   曾经的错误方案是 --mm_eval_fresh(只在 eval 前刷新投影), 已实测证伪并废弃:
#   它让 R@20 从 0.06968 崩到 0.05775(valid 同步崩, loss 反升), 因为模型是在
#   c~0.06 的图传播下训练的, 评测却切到 c~0.83 的前向 -> 训练/评测错配.
#
#   真实根因: 预算经 fuse_subset(每 batch 带梯度)推 proj 头, 而图传播读的
#   project() 全量缓存每 epoch 只刷一次 -> 结构上永远追不上.
#   实测 seed2024: 图传播 c=0.055 vs 预算 batch_c=0.823(差 0.77),
#   即模型其实是在"几乎不融合多模态"的图上训练, E6 等于没生效.
#
#   正解: 训练途中每 32 batch 刷新全量投影, 让两条路径同步.
#   实测 seed9997 ep5: 图传播 c=0.793 / batch_c=0.808 / 新鲜 0.796(滞后仅 0.003),
#   且 conf_std=0.227(远高于错误方案的 0.073) -> 判别性反而更强.
#   开销 ~+7.5s/epoch.
#   ==> fc0.8 靶子必须在**同一 pr32 口径**下重测(Stage A0).
#
# 判据:
#   主判据 FRESH conf_mean @最优 test epoch >= 0.6   (缓存版仅作滞后诊断, 不作判据)
#   效果   R@20 >= fc0.8(pr32 同口径重测值 = Stage A0), 理想再高一截
#          注意: 旧的 0.08798 是"每 epoch 只刷一次投影"口径, 不可直接当靶子
#   保判别 conf_std 明显 > 0 (否则退化成 force_c, 自适应无从谈起)
#
# 执行顺序: 先出主结果, 再出同口径靶子, 最后补机制验证. 任一阶段失败可提前止损.
set -u
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
export KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_DYNAMIC=FALSE

LOG=/tmp/e6_budget.log
DS=amazon-baby-mmssl
# EP 可用环境变量覆盖: `EP=30 bash run_e6_budget.sh`
# 为什么留这个口子: 代码库内**没有任何 torch.save**(已核实), checkpoints/ 恒空,
#   --load 永远走 "not exists, start from beginning" -> **不存在续跑能力**。
#   且 AL 的对偶乘子 model._mm_dual 是普通 float(非 buffer/parameter), 即便有
#   state_dict 也带不走 -> 续跑会把 nu 清零, 破坏约束连续性。
#   结论: 一旦判定 20ep 不够, 只能**从头重跑**, 没有便宜的续跑路径。
#   因此 epoch 数必须一次拍准, 这里做成可覆盖以便一键切档。
EP=${EP:-20}
LAM=1.0      # 增广项系数
ETA=0.05     # 对偶上升步长
PR=32        # 每 32 batch 刷新一次全量投影(见下方口径说明)

echo "E6_BUDGET_START $(date)" > "$LOG"

run () {   # run <tag> <seeds> <extra...>
  local tag="$1" seeds="$2"; shift 2
  echo "--- $tag seeds=$seeds START $(date) ---" >> "$LOG"
  "$VENV_PY" run_idea2.py --only idea2 --epochs "$EP" --dataset "$DS" \
      --seeds "$seeds" --mm_proj_refresh "$PR" "$@" >> "$LOG" 2>&1
  echo "--- $tag END $(date) rc=$? ---" >> "$LOG"
}

# ============ Stage A: 主实验 t=0.8 增广拉格朗日, 3 seed(先出 headline) ============
# 决断跑可能已经单独跑完 seed2024(同参数同口径), 跑完了就跳过, 省 33min。
# 判"跑完"的唯一标准 = 日志里出现 EPOCH[20/20] 且无 Traceback, 与 run_idea2.py 的
# run_complete() 同口径; 截断日志一律当没跑过, 重跑。
A_SEEDS=2024,2025,2026
A_LOG="logs/run_idea2_mm_mcr0_mb0.8l1d0.05_pr32_seed2024.log"
if [ -f "$A_LOG" ] && grep -q "EPOCH\[${EP}/${EP}\]" "$A_LOG" && ! grep -q "Traceback" "$A_LOG"; then
  A_SEEDS=2025,2026
  echo "--- A_main_t0.8: seed2024 已由决断跑完成($A_LOG), 本次只跑 $A_SEEDS ---" >> "$LOG"
fi
run "A_main_t0.8" "$A_SEEDS" \
    --mm_conf_reg 0 --mm_budget 0.8 --mm_budget_lambda "$LAM" --mm_budget_dual "$ETA"

# ============ Stage A0: fc0.8 同口径重测(新靶子) ============
# 旧的 0.08798 是在"每 epoch 只刷一次投影"口径下测的, 与 Stage A(pr32) 不可直接比. force_c 档 c 被直接覆写为常数,
# 两条路径本来就一致, 但注入的 pooled 方向仍受投影新鲜度影响 -> 必须同口径重测.
run "A0_fc0.8_ref" 2024,2025,2026 --force_c 0.8

# ============ Stage B: c_target 扫描, 单 seed(机制验证) ============
# 0.2 = 双向控制验证(证明能把 c 压下去, 排除"惩罚太弱/太强"的混淆)
# t=1.0 已知退化(单元冒烟 std->0.0002, 等价 fc1.0), 且 E1 已有 fc1.0 数据, 故不跑.
run "B_t0.2" 2024 --mm_conf_reg 0 --mm_budget 0.2 --mm_budget_lambda "$LAM" --mm_budget_dual "$ETA"
run "B_t0.6" 2024 --mm_conf_reg 0 --mm_budget 0.6 --mm_budget_lambda "$LAM" --mm_budget_dual "$ETA"

# ============ Stage C: 软惩罚对照, 单 seed ============
# 不加对偶项 => 用实测欠冲量反推真实 BPR 下压强度 A = 2*LAM*(t - c_bar),
# 同时在真实数据上验证"固定 lambda 够不到 target"的理论预测.
run "C_soft_t0.8" 2024 --mm_conf_reg 0 --mm_budget 0.8 --mm_budget_lambda "$LAM"

echo "E6_TRAIN_ALL_END $(date)" >> "$LOG"
"$VENV_PY" analyze_e6.py >> "$LOG" 2>&1
echo "E6_BUDGET_DONE $(date)" >> "$LOG"
