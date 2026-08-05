"""诊断: 投影头梯度饥饿 + 各修复方案的 CPU 成本 benchmark."""
import os
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OMP_DYNAMIC', 'FALSE')

import time
import torch
import torch.nn as nn

torch.manual_seed(0)
N_ITEMS = 18357
N_INTER = 190930
BATCH = 2048
N_BATCH = N_INTER // BATCH + 1
D = 64
HID = 256

print(f'items={N_ITEMS}  interactions={N_INTER}  batch={BATCH}  batches/epoch={N_BATCH}')
print()
print('=== 梯度更新次数对比 (20 epoch 全程) ===')
print(f'  id_emb / conf_mlp / type_emb : {N_BATCH * 20:>6d} 次')
print(f'  proj 投影头 (epoch 级缓存)   : {20:>6d} 次   <-- 相差 {N_BATCH}x')
print()

img = torch.randn(N_ITEMS, 4096)
txt = torch.randn(N_ITEMS, 384)
proj_i = nn.Sequential(nn.Linear(4096, HID), nn.ReLU(), nn.Dropout(0.1), nn.Linear(HID, D))
proj_t = nn.Sequential(nn.Linear(384, HID), nn.ReLU(), nn.Dropout(0.1), nn.Linear(HID, D))


def timeit(fn, n=3):
    fn()  # warmup
    t = time.time()
    for _ in range(n):
        fn()
    return (time.time() - t) / n


def full_fwd_bwd():
    a = proj_i(img); b = proj_t(txt)
    (a.sum() + b.sum()).backward()
    proj_i.zero_grad(); proj_t.zero_grad()


idx = torch.randint(0, N_ITEMS, (BATCH * 2,))


def batch_fwd_bwd():
    a = proj_i(img[idx]); b = proj_t(txt[idx])
    (a.sum() + b.sum()).backward()
    proj_i.zero_grad(); proj_t.zero_grad()


t_full = timeit(full_fwd_bwd)
t_batch = timeit(batch_fwd_bwd)

print('=== 单次投影 fwd+bwd 耗时 (单线程 CPU) ===')
print(f'  全量 {N_ITEMS} 物品 : {t_full * 1000:8.1f} ms')
print(f'  batch {BATCH*2} 物品 : {t_batch * 1000:8.1f} ms')
print()
print('=== 每 epoch 额外开销 (当前 epoch 约 132 s) ===')
print(f'  方案A 每 batch 全量投影   : +{t_full * N_BATCH:7.1f} s/epoch  ({t_full*N_BATCH/132*100:6.0f}% 增幅)  -> 不可行')
print(f'  方案B 每 batch 仅投影本批 : +{t_batch * N_BATCH:7.1f} s/epoch  ({t_batch*N_BATCH/132*100:6.0f}% 增幅)')
for k in (4, 8, 16):
    print(f'  方案C 每 {k:2d} batch 刷新全量  : +{t_full * N_BATCH / k:7.1f} s/epoch  ({t_full*N_BATCH/k/132*100:6.0f}% 增幅)')

print()
print('=== 方案D: InfoNCE 用「小批新鲜投影」(propagation 仍用 epoch 缓存) ===')
print('   -> proj 恢复每 batch 梯度 (94x), 成本只与子采样规模成正比')
for sub in (256, 512, 1024, 2048):
    sidx = torch.randint(0, N_ITEMS, (sub,))

    def _f(si=sidx):
        a = proj_i(img[si]); b = proj_t(txt[si])
        (a.sum() + b.sum()).backward()
        proj_i.zero_grad(); proj_t.zero_grad()

    t = timeit(_f, n=5)
    print(f'   子采样 {sub:5d} 物品 : {t*1000:6.1f} ms/batch  -> +{t*N_BATCH:5.1f} s/epoch  ({t*N_BATCH/132*100:5.1f}% 增幅)  | proj 梯度步 {N_BATCH*20} 次')
