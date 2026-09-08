# -*- coding: utf-8 -*-
"""Parse best Recall@20 from E15-TF logs (both seeds)."""
import re, json

def load_clean(p):
    raw = open(p, 'rb').read().replace(b'\x00', b'').decode('utf-8', 'ignore')
    return raw

def find_dicts(raw):
    # match lines like {'Epoch': 'best', 'Recall@10': '0.0207', ...}
    pat = re.compile(r"\{[^{}]*'Epoch'[^{}]*\}")
    return pat.findall(raw)

for seed in ['42', '2025']:
    p = f'logs/e15_TF_seed{seed}.log'
    raw = load_clean(p)
    rows = find_dicts(raw)
    best_rows = [r for r in rows if "'best'" in r]
    evals = [r for r in rows if "'best'" not in r]
    print(f'=== seed{seed}: total rows {len(rows)}, best rows {len(best_rows)} ===')
    for b in best_rows:
        print(b)
    if evals:
        print('last eval:', evals[-1])
