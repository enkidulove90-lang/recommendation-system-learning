import os
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OMP_DYNAMIC', 'FALSE')

import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)
n, d = 2000, 64
id_emb = nn.Parameter(torch.empty(n, d).normal_(0, 0.1))
pooled = F.normalize(torch.randn(n, d), dim=-1)

id_scale = id_emb.norm(dim=-1, keepdim=True).detach()
pooled_scaled = pooled * id_scale

print('pooled  norm mean/std: %.4f / %.4f' % (pooled.norm(dim=-1).mean(), pooled.norm(dim=-1).std()))
print('id_emb  norm mean/std: %.4f / %.4f' % (id_emb.norm(dim=-1).mean(), id_emb.norm(dim=-1).std()))
print('scaled  norm mean/std: %.4f / %.4f' % (pooled_scaled.norm(dim=-1).mean(), pooled_scaled.norm(dim=-1).std()))
print()
for c in (0.0, 0.25, 0.5, 1.0):
    f_old = id_emb + c * (pooled - id_emb)
    f_new = id_emb + c * (pooled_scaled - id_emb)
    print('c=%.2f | OLD norm %.4f (std %.4f) | NEW norm %.4f (std %.4f)' % (
        c,
        f_old.norm(dim=-1).mean(), f_old.norm(dim=-1).std(),
        f_new.norm(dim=-1).mean(), f_new.norm(dim=-1).std()))

print()
# 流行度信息保持度: 融合后模长与原 ID 模长的相关性(越高 = 流行度信号保留越好)
base_rank = id_emb.norm(dim=-1).detach()
for c in (0.25, 0.5, 1.0):
    f_old = (id_emb + c * (pooled - id_emb)).norm(dim=-1).detach()
    f_new = (id_emb + c * (pooled_scaled - id_emb)).norm(dim=-1).detach()
    r_old = torch.corrcoef(torch.stack([base_rank, f_old]))[0, 1].item()
    r_new = torch.corrcoef(torch.stack([base_rank, f_new]))[0, 1].item()
    print('c=%.2f | corr(|id|, |fused|)  OLD %.4f  ->  NEW %.4f' % (c, r_old, r_new))
