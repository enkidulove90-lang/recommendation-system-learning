#!/bin/bash
# E1 补跑: 仅跑缺失的 seed, 已有的 seed2024 (fc0.3/0.8/1.0) 已从 eval txt 回填
# save() 已加重试+退路, 不再因安全删除钩子丢结果。
cd "C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code"
export VENV_PY="C:/Users/xu.yan1/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
echo "E1_MISSING_START $(date)" > /tmp/e1_missing.log
for C in 0.3 0.8 1.0; do
  echo "===== E1 force_c=$C SEEDS 2025,2026 START $(date) =====" >> /tmp/e1_missing.log
  "$VENV_PY" run_idea2.py --only idea2 --epochs 20 --seeds 2025,2026 --force_c $C --dataset amazon-baby-mmssl >> /tmp/e1_missing.log 2>&1
  echo "===== E1 force_c=$C END $(date) rc=$? =====" >> /tmp/e1_missing.log
done
echo "===== E1 force_c=0.5 SEEDS 2024,2025,2026 START $(date) =====" >> /tmp/e1_missing.log
"$VENV_PY" run_idea2.py --only idea2 --epochs 20 --seeds 2024,2025,2026 --force_c 0.5 --dataset amazon-baby-mmssl >> /tmp/e1_missing.log 2>&1
echo "===== E1 force_c=0.5 END $(date) rc=$? =====" >> /tmp/e1_missing.log
echo "E1_MISSING_DONE $(date)" >> /tmp/e1_missing.log

# 最终聚合: 每个 fc 档对所有已存 seed 取均值 (不限于本次 seeds 参数)
"$VENV_PY" - <<'PY' >> /tmp/e1_missing.log 2>&1
import json, os
d = json.load(open('results_idea2.json'))
cfgs = d['configs']
base = cfgs.get('baseline', {})
br = [v['R@20'] for v in base.values() if v.get('R@20',0)>0]
bn = [v['N@20'] for v in base.values() if v.get('N@20',0)>0]
print("\n=== E1 FINAL AGGREGATION (mean over stored seeds) ===")
print(f"baseline      : R@20={sum(br)/len(br):.4f}  N@20={sum(bn)/len(bn):.4f}  (n={len(br)})")
for k in ['idea2_mm','idea2_mm_fc0.3','idea2_mm_fc0.5','idea2_mm_fc0.8','idea2_mm_fc1']:
    m = cfgs.get(k, {})
    rs = [v['R@20'] for v in m.values() if v.get('R@20',0)>0]
    ns = [v['N@20'] for v in m.values() if v.get('N@20',0)>0]
    if rs:
        r=sum(rs)/len(rs); n=sum(ns)/len(ns)
        delta = (r - sum(br)/len(br)) / (sum(br)/len(br)) * 100 if br else 0
        print(f"{k:16s}: R@20={r:.4f}  N@20={n:.4f}  rel_vs_base={delta:+.1f}%  (n={len(rs)}, seeds={sorted(m.keys())})")
PY
