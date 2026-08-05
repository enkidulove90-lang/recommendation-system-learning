"""冒烟测试: 验证投影头梯度饥饿修复正确生效。

检查项:
  1. 全量 project() 走 no_grad 缓存, 同 epoch 内复用、换 epoch 才重算
  2. contrastive_loss(idx, feats=...) 能给 proj 头梯度
  3. 旧调用 contrastive_loss(idx) 不给 proj 梯度(确认梯度确实来自新路径)
  4. fuse() 仍能给 type_emb / conf_mlp / id_emb 梯度
  5. 实测每 batch 额外开销
"""
import os
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OMP_DYNAMIC', 'FALSE')

import time
import torch
import torch.nn as nn
from mm_align import MultiModalAligner

torch.manual_seed(0)
N, D = 18357, 64
feats = {'image_feat': torch.randn(N, 4096), 'text_feat': torch.randn(N, 384)}
al = MultiModalAligner(N, D, {'image_feat': 4096, 'text_feat': 384})
id_emb = nn.Parameter(torch.empty(N, D).normal_(0, 0.1))

ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(f'  [{"PASS" if cond else "FAIL"}] {name} {extra}')


print('1) 全量投影缓存行为')
al.set_epoch(1)
p1 = al.project(feats)
p2 = al.project(feats)
check('同 epoch 内复用同一份缓存', p1['image_feat'] is p2['image_feat'])
check('缓存不带梯度 (no_grad)', not p1['image_feat'].requires_grad)
al.set_epoch(2)
p3 = al.project(feats)
check('换 epoch 后重算', p3['image_feat'] is not p1['image_feat'])

print()
print('2) contrastive_loss(feats=...) 给 proj 头梯度')
al.zero_grad()
idx = torch.randint(0, N, (2048,)).unique()
loss = al.contrastive_loss(idx, feats=feats)
loss.backward()
g_img = al.proj['image_feat'][0].weight.grad
g_txt = al.proj['text_feat'][0].weight.grad
check('image proj 有梯度', g_img is not None and g_img.abs().sum() > 0,
      f'|g|={g_img.abs().sum():.4f}' if g_img is not None else '')
check('text  proj 有梯度', g_txt is not None and g_txt.abs().sum() > 0,
      f'|g|={g_txt.abs().sum():.4f}' if g_txt is not None else '')

print()
print('3) 旧调用(不传 feats)确认无 proj 梯度')
al.zero_grad()
al.set_epoch(3)
fused, info = al.fuse(feats, id_emb)
loss_old = al.contrastive_loss(idx)
if loss_old.requires_grad:
    loss_old.backward()
g_img2 = al.proj['image_feat'][0].weight.grad
check('旧路径 proj 无梯度(证明梯度确来自 project_subset)',
      g_img2 is None or g_img2.abs().sum() == 0)

print()
print('4) fuse() 仍训练 type_emb / conf_mlp / id_emb')
al.zero_grad()
if id_emb.grad is not None:
    id_emb.grad = None
al.set_epoch(4)
fused, info = al.fuse(feats, id_emb)
fused.sum().backward()
check('type_emb 有梯度', al.type_emb['image_feat'].grad is not None
      and al.type_emb['image_feat'].grad.abs().sum() > 0)
check('conf_mlp 有梯度', al.conf_mlp[0].weight.grad is not None
      and al.conf_mlp[0].weight.grad.abs().sum() > 0)
check('id_emb 有梯度', id_emb.grad is not None and id_emb.grad.abs().sum() > 0)
print(f'  conf_mean(初始化时应约 0.5) = {info["conf_mean"]:.3f}')
check('初始 conf_mean 接近 0.5', 0.4 < info['conf_mean'] < 0.6)

print()
print('5) 每 batch 额外开销实测')
al.set_epoch(9)
al.project(feats)          # 预热缓存


def one_batch():
    al.zero_grad()
    f, _ = al.fuse(feats, id_emb)
    l = al.contrastive_loss(idx, feats=feats)
    l.backward()


one_batch()
t0 = time.time()
for _ in range(3):
    one_batch()
dt = (time.time() - t0) / 3
n_batch = 94
print(f'  fuse + 带梯度子集投影: {dt*1000:.0f} ms/batch  ->  +{dt*n_batch:.1f} s/epoch '
      f'({dt*n_batch/132*100:.0f}% 相对 132s 基准)')
print(f'  proj 梯度步数: 每 epoch {n_batch} 步, 20 epoch 共 {n_batch*20} 步 (修复前仅 20 步)')

print()
print('=' * 50)
print('全部通过' if ok else '存在失败项, 需修正')
