import re, os
def best_r20(log):
    if not os.path.exists(log): return None
    lines=open(log,encoding='utf-8',errors='ignore').read().splitlines()
    r20={}; cur=None; nxt=False
    def grab(l):
        m=re.search(r"'recall':\s*array\(\[\s*([\d.eE+-]+)",l)
        return float(m.group(1)) if m else None
    for l in lines:
        me=re.search(r'EPOCH\[(\d+)/',l)
        if me: cur=int(me.group(1))
        if '[TEST]' in l:
            v=grab(l)
            if v is not None and cur is not None: r20[cur]=v
            else: nxt=True
            continue
        if nxt:
            v=grab(l)
            if v is not None and cur is not None: r20[cur]=v
            nxt=False
    return (max(r20.values()), r20) if r20 else (None,{})
print("=== EP=50 (current logs) best R@20 ===")
for ly in [4,5]:
    for sd in [2024,2025,2026]:
        f=f"logs/run_idea2_mm_fc0.8_nl{ly}_pr32_seed{sd}.log"
        if not os.path.exists(f):
            print(f"nl{ly}s{sd}: NO FILE"); continue
        v,d=best_r20(f)
        if v is None:
            print(f"nl{ly}s{sd}: EP=20 backup (no EP=50 yet)")
        else:
            print(f"nl{ly}s{sd}: EP=50 bestR20={v:.5f} @ep{max(d,key=d.get)}  (tests={len(d)})")
