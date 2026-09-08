"""
E14-ter 真实体制接线冒烟（SASRec 路径，对应 run_e15.ps1 的 TF 组）
验证链：SASRecTrainer.iteration 构造 y_proxy=item_embeddings(target_pos[:,-1]).detach()
        → model.finetune(input_ids, syn_target=y_proxy)
        → SASRecModel.add_position_embedding → Interaction_Expert_Layer.forward(syn_target)
        → total_interaction_loss 含 L_comp；残差路由 comp_head(syn_perp) 进 item_embeddings。

用例（均用真实 amazon-baby-mmssl 特征 + item_size）：
  TF 开 L_comp : λ_uni=λ_syn=λ_red=0, λ_comp=0.1 → total_interaction_loss 仅含 L_comp 且 >0，comp_head 拿梯度
  安全闸门 OFF : λ_comp=0 → total_interaction_loss ≈ 0（其他 λ 也为 0），无随机残差注入
"""
import sys, os, types
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from SASRec import SASRecModel

DATA = "./data/amazon-baby-mmssl"
IMG = os.path.join(DATA, "image_features_amazon-baby-mmssl.pt")
TXT = os.path.join(DATA, "text_features_amazon-baby-mmssl.pt")


def build_args(lambda_comp, uni=0.0, syn=0.0, red=0.0):
    img_feat = torch.load(IMG)              # [N, 4096]
    txt_feat = torch.load(TXT)              # [N, 384]
    assert img_feat.shape[0] == txt_feat.shape[0], "img/txt 特征行数不一致"
    # replace_embedding 将特征写到 weight.data[1:-1]，故 item_size = 行数 + 2（与原始 PRISM 一致）
    item_size = img_feat.shape[0] + 2
    a = types.SimpleNamespace()
    a.item_size = item_size
    a.hidden_size = 256
    a.max_seq_length = 100
    a.image_emb_dim = 4096
    a.text_emb_dim = 384
    a.initializer_range = 0.02
    a.hidden_dropout_prob = 0.3
    a.num_attention_heads = 4
    a.attention_probs_dropout_prob = 0.0
    a.hidden_act = "gelu"
    a.num_hidden_layers = 1
    a.distance_metric = "wasserstein"
    a.kernel_param = 1.0
    a.lambda_uni = uni
    a.lambda_syn = syn
    a.lambda_red = red
    a.lambda_comp = lambda_comp
    a.disable_mm = False
    a.cuda_condition = False
    a.device = torch.device("cpu")
    a.image_emb_path = IMG
    a.text_emb_path = TXT
    return a


def make_batch(item_size, B=4, L=100):
    input_ids = torch.randint(1, item_size - 1, (B, L))
    next_ids = torch.randint(1, item_size - 1, (B,))
    return input_ids, next_ids


def run_case(lambda_comp, uni, syn, red, label, pass_syn_target=True):
    a = build_args(lambda_comp, uni, syn, red)
    model = SASRecModel(a)
    model.train()
    input_ids, next_ids = make_batch(a.item_size)
    y_proxy = model.item_embeddings(next_ids).detach()          # [B, H]
    if pass_syn_target:
        seq_out, _, total_loss = model.finetune(input_ids, syn_target=y_proxy)
    else:
        seq_out, _, total_loss = model.finetune(input_ids)
    ok_finite = torch.isfinite(total_loss).item() and torch.isfinite(seq_out).all().item()
    loss = total_loss + seq_out[:, -1, :].sum()                 # 拉通梯度到 comp_head（若路由开启）
    model.zero_grad()
    loss.backward()
    cg = model.interaction_expert_layer.comp_head.weight.grad
    comp_grad_nonzero = (cg is not None) and (cg.abs().sum().item() > 0)
    print(f"[{label}] λ_comp={lambda_comp} total_interaction_loss={total_loss.item():.6f} "
          f"finite={ok_finite} comp_head_grad_nonzero={comp_grad_nonzero}")
    return total_loss.item(), ok_finite, comp_grad_nonzero


if __name__ == "__main__":
    print("=== E14-ter 真实接线冒烟 (TF 组配置: uni=syn=red=0) ===")
    # 1) TF 开 L_comp：应与合成 ter_free 同构（互补路由 + L_comp，关 L_syn）
    lc, fin, gn = run_case(0.1, 0.0, 0.0, 0.0, "TF(comp=0.1)")
    assert fin, "FAIL: loss 非有限"
    assert lc > 0, "FAIL: L_comp 未生效 (total_interaction_loss 应>0)"
    assert gn, "FAIL: comp_head 未拿到梯度（残差路由/L_comp 未激活）"
    # 2) 安全闸门：λ_comp=0 时 total_interaction_loss ≈ 0（无随机 syn 残差注入）
    lc0, fin0, _ = run_case(0.0, 0.0, 0.0, 0.0, "OFF(comp=0)")
    assert fin0, "FAIL: loss 非有限"
    assert abs(lc0) < 1e-7, f"FAIL: 关 L_comp 后 total_interaction_loss 应≈0，实得 {lc0}"
    # 3) 真实 trainer 的 else 分支（不传 syn_target，λ_comp=0）：同应为 0，且不崩溃
    lc0b, fin0b, _ = run_case(0.0, 0.0, 0.0, 0.0, "OFF(no_syn_target)", pass_syn_target=False)
    assert fin0b and abs(lc0b) < 1e-7, "FAIL: 不传 syn_target 的 OFF 分支异常"
    print("\nSMOKE_E14TER_REAL_PASS")
