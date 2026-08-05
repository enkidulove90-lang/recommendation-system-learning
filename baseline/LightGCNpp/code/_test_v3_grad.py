"""v3 梯度通路单元测试: 验证 BPR 风格损失能经 fuse_subset 把梯度送回 proj/type_emb/conf_mlp."""
import torch
from mm_align import MultiModalAligner

torch.manual_seed(0)
n, d = 200, 16
feats = {'img': torch.randn(n, 64), 'txt': torch.randn(n, 32)}
id_emb = torch.nn.Parameter(torch.randn(n, d))
aligner = MultiModalAligner(n_items=n, id_dim=d, feat_dims={'img': 64, 'txt': 32}, proj_hidden=32)

u = torch.randn(8, d)                       # 固定用户嵌入(无梯度需求)
pos = torch.arange(8)
neg = torch.arange(8, 16)
cat_pn = torch.cat([pos, neg])
idx, inverse = cat_pn.unique(return_inverse=True)

fused, c = aligner.fuse_subset(feats, id_emb, idx)
# 模拟 bpr_loss 的 gamma 拼接 + BPR 分数(BPR 不要求 u 有梯度)
gamma = 0.2
ep_pos = torch.randn(8, d)
ep_neg = torch.randn(8, d)
pos_emb = gamma * fused[inverse[:8]] + (1 - gamma) * ep_pos
neg_emb = gamma * fused[inverse[8:]] + (1 - gamma) * ep_neg
scores = (u * pos_emb).sum(1) - (u * neg_emb).sum(1)
loss = torch.nn.functional.softplus(-scores).mean()   # BPR 风格

loss.backward()

ok = True
for t in aligner.types:
    g = aligner.proj[t][0].weight.grad
    s = None if g is None else float(g.abs().sum())
    print(f"[proj:{t}] grad_sum = {s}")
    if g is None or float(g.abs().sum()) == 0.0:
        ok = False
te = aligner.type_emb['img'].grad
se = None if te is None else float(te.abs().sum())
print(f"[type_emb] grad_sum = {se}")
if te is None or se == 0.0:
    ok = False
cm = aligner.conf_mlp[0].weight.grad
sc = None if cm is None else float(cm.abs().sum())
print(f"[conf_mlp] grad_sum = {sc}")
if cm is None or sc == 0.0:
    ok = False

print("V3_GRAD_OK" if ok else "V3_GRAD_FAIL")
