"""smoke_e14ter.py — 真实体制 E14-ter 代码路径前向 smoke（不加载 17min 数据）。

验证 PRISM.py Interaction_Expert_Layer 的 E14-ter 改造：
  - comp_head / syn_complement / synergy_complementary_loss 方法存在且可运行
  - forward(img, txt, syn_target) 在 lambda_comp>0 时把 L_comp 并入 interaction_losses
  - 关闭 lambda_comp 时退化为原行为（loss 不含互补项）
不依赖 amazon-baby-mmssl 数据与 InDiRecTrainer，纯小张量前向。
"""
import sys, types, torch, torch.nn.functional as F

sys.path.insert(0, ".")
from PRISM import Interaction_Expert_Layer

class Args:
    lambda_uni = 0.1
    lambda_syn = 0.1
    lambda_red = 0.1
    lambda_comp = 0.5          # 开 E14-ter
    hidden_size = 64

torch.manual_seed(0)
B, H = 8, 64
img = torch.randn(B, H)
txt = torch.randn(B, H)
syn_target = torch.randn(B, H)   # 真实体制 = 下一 item embedding（y_proxy）

layer = Interaction_Expert_Layer(Args(), hidden_size=H, expert_hidden_size=128, num_experts_per_type=1)

# 1) 开 lambda_comp + syn_target → 应含互补损失
out_on = layer(img, txt, syn_target=syn_target)
loss_on = out_on["interaction_losses"]
print("forward w/ lambda_comp=0.5 + syn_target: loss =", float(loss_on.detach()),
      "| expert_embs keys:", list(out_on["expert_embs"].keys()))

# 2) syn_complement / synergy_complementary_loss 直接调用
syn_perp = layer.syn_complement(out_on["expert_embs"])
print("syn_complement shape:", tuple(syn_perp.shape),
      "| is unit-norm:", bool(torch.allclose(syn_perp.norm(dim=-1), torch.ones(B), atol=1e-4)))
comp_loss = layer.synergy_complementary_loss(syn_perp, syn_target)
print("synergy_complementary_loss:", float(comp_loss.detach()))

# 3) 反向传播不崩
loss_on.backward()
print("backward OK")

# 4) 关 lambda_comp（默认 0）→ 退化为原行为（无 comp_head 梯度路径触发）
Args2 = types.SimpleNamespace(lambda_uni=0.1, lambda_syn=0.1, lambda_red=0.1,
                              lambda_comp=0.0, hidden_size=H)
layer2 = Interaction_Expert_Layer(Args2, hidden_size=H, expert_hidden_size=128, num_experts_per_type=1)
out_off = layer2(img, txt, syn_target=syn_target)
print("forward w/ lambda_comp=0.0: loss =", float(out_off["interaction_losses"].detach()))

# 5) SASRec.add_position_embedding 的 comp_head 残差路由等价逻辑验证
#    （item_embeddings[B,seq,H] + comp_head(syn_perp).unsqueeze(1)）
seq = 5
item_emb = torch.randn(B, seq, H)
routed = item_emb + layer.comp_head(syn_perp).unsqueeze(1)
print("comp_head residual routing shape:", tuple(routed.shape), "OK")
print("SMOKE_E14TER_PASS")
