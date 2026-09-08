import torch, sys
sys.path.insert(0, r'C:/Users/xu.yan1/papers/recommendation-system-learning/baseline/LightGCNpp/code')
from prism_moe import PRISMExpertLayer, EXPERT_KEYS
torch.manual_seed(0)
p = PRISMExpertLayer(dim=64, expert_hidden=128)
img = torch.randn(37, 64, requires_grad=True)
txt = torch.randn(37, 64, requires_grad=True)
out = p(img, txt)
print('loss =', round(out['loss'].item(), 6))
print('loss_dict =', {k: round(v, 4) for k, v in out['loss_dict'].items()})
print('fused', tuple(out['fused'].shape), '| afl_w', tuple(out['afl_w'].shape))
print('afl_w rowsum =', round(out['afl_w'].sum(-1).mean().item(), 6))
print('div =', round(out['div'], 4), '| afl_entropy =', round(out['afl_entropy'], 4))
print('fused L2 norm (expect 1.0) =', round(out['fused'].norm(dim=-1).mean().item(), 6))
seen = set()
for k in EXPERT_KEYS:
    ids = {id(q) for q in p.experts[k].parameters()}
    assert not (seen & ids), 'SHARED PARAMS!'
    seen |= ids
print('param independence (kengt2): OK, 4 experts share 0 params')
out['loss'].backward()
print('grad reaches img/txt:', img.grad is not None, txt.grad is not None)
print('SMOKE TEST PASS')
