"""E1 数据恢复: 从已完成的 eval .txt 日志中回填 seed2024 的 R@20/N@20,
避免对 fc0.3/0.8/1.0 重跑 seed2024 (节省 ~2.25h)。纯读 eval txt + 写 results_idea2.json。
"""
import os, re, json

CODE = os.path.dirname(os.path.abspath(__file__))
DATASET = 'amazon-baby-mmssl'
# config 文件名模板 (与 main.py config_name 对齐)
def cfg_name(seed, fc):
    return (f'{DATASET}_seed{seed}_lgn_dim64_lr0.001_dec0.0001_alpha0.6_beta-0.1_'
            f'gamma0.2_nl2_mm_mr0.001_mt0.1_fc{fc}')

def parse_best_test(seed, fc):
    txt = os.path.join(CODE, 'logs', cfg_name(seed, fc) + '.txt')
    best_r = best_n = -1
    try:
        with open(txt) as f:
            for line in f:
                if line.strip().startswith('test '):
                    nums = re.findall(r'[-+]?\d*\.?\d+', line.strip()[5:])
                    if len(nums) >= 6:
                        ndcg20, _, recall20, _, _, _ = map(float, nums[:6])
                        if ndcg20 > best_n:
                            best_n, best_r = ndcg20, recall20
    except FileNotFoundError:
        pass
    return best_r, best_n

out = os.path.join(CODE, 'results_idea2.json')
with open(out) as f:
    d = json.load(f)
configs = d.setdefault('configs', {})

recovered = []
for fc in [0.3, 0.8, 1.0]:
    fc_str = f'{fc:.6g}'
    r, n = parse_best_test(2024, fc_str)
    if r > 0:
        configs.setdefault(f'idea2_mm_fc{fc_str}', {})['2024'] = {
            'R@20': round(r, 4), 'N@20': round(n, 4)}
        recovered.append((fc_str, r, n))
        print(f"fc{fc_str} seed2024 recovered R@20={r:.4f} N@20={n:.4f}")
    else:
        print(f"fc{fc_str} seed2024 NOT found in eval txt -> will re-run")

# 清理 fc0.5 的陈 Smoke 条目 (来自 --epochs 1 冒烟, R@20<=0 无效)
fc05 = configs.get('idea2_mm_fc0.5')
if fc05 and all(v.get('R@20', 0) <= 0 for v in fc05.values()):
    del configs['idea2_mm_fc0.5']
    print("removed stale fc0.5 smoke entry (will full re-run)")

with open(out, 'w') as f:
    json.dump(d, f, indent=2)
print("results_idea2.json updated; recovered", recovered)
