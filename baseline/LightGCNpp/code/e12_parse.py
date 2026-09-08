import re, os
D = "logs"

def best_r20(log):
    if not os.path.exists(log):
        return None
    lines = open(log, encoding='utf-8', errors='ignore').read().splitlines()
    r20 = {}; cur = None; nxt = False
    def grab(l):
        m = re.search(r"'recall':\s*array\(\[\s*([\d.eE+-]+)", l)
        return float(m.group(1)) if m else None
    for l in lines:
        me = re.search(r'EPOCH\[(\d+)/', l)
        if me:
            cur = int(me.group(1))
        if '[TEST]' in l:
            v = grab(l)
            if v is not None and cur is not None:
                r20[cur] = v
            else:
                nxt = True
            continue
        if nxt:
            v = grab(l)
            if v is not None and cur is not None:
                r20[cur] = v
            nxt = False
    return max(r20.values()) if r20 else None

for tag in ["nl3", "nl4", "nl5"]:
    print(f"--- {tag} ---")
    for s in [2024, 2025, 2026]:
        f = f"{D}/run_idea2_mm_fc0.8_{tag}_pr32_seed{s}.log"
        v = best_r20(f)
        mx = 0
        if os.path.exists(f):
            for l in open(f, encoding='utf-8', errors='ignore'):
                m = re.search(r'EPOCH\[\d+/(\d+)\]', l)
                if m:
                    mx = max(mx, int(m.group(1)))
        if v is not None:
            print(f"  s{s}: R@20={v:.5f}  (EP={mx})")
        else:
            print(f"  s{s}: NO TEST YET (EP={mx})")
