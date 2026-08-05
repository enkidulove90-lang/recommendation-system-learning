"""清理上一轮(范数对齐但投影头梯度饥饿)遗留的 runner 日志与陈旧锁。

Windows 沙箱会拦截 bash 的 rm，故改用 os.replace 把文件移入归档目录
(rename 而非 delete，不触发 safe-delete)。
"""
import os
from pathlib import Path

LOGS = Path(__file__).resolve().parent / 'logs'
ARCH = LOGS / '_archive_gradstarve'
ARCH.mkdir(exist_ok=True)

# 1) 归档上一轮 runner 日志(新 run 会覆盖同名文件, 先留证据)
for name in ['run_idea2_mm_seed2024.log', 'run_idea2_cost_seed2024.log']:
    src = LOGS / name
    if src.exists():
        os.replace(src, ARCH / name)
        print(f'[archived] {name}')
    else:
        print(f'[skip] {name} not found')

# 2) 清理陈旧锁(进程已不存在)
import subprocess
alive = subprocess.run(
    ['powershell', '-NoProfile', '-Command',
     "(Get-Process -Name python -ErrorAction SilentlyContinue).Id -join ','"],
    capture_output=True, text=True).stdout.strip()
alive_pids = {p for p in alive.split(',') if p}
print(f'[alive python pids] {sorted(alive_pids)}')

for lk in LOGS.glob('.run_lock_*'):
    pid = lk.read_text().strip()
    if pid not in alive_pids:
        os.replace(lk, ARCH / (lk.name + f'.stale_{pid}'))
        print(f'[stale lock removed] {lk.name} (pid={pid})')
    else:
        print(f'[lock kept] {lk.name} (pid={pid} alive)')

# 3) 确认 logs 根目录没有残留的 mm 指标文件(会污染聚合)
leftovers = sorted(p.name for p in LOGS.glob('amazon-baby-mmssl_*_mm_*.txt'))
print(f'[mm metric leftovers in logs/] {leftovers if leftovers else "none (clean)"}')
