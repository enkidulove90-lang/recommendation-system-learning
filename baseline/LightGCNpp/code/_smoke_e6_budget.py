"""
_smoke_e6_budget.py — E6 全局预算机制的轻量单元验证(不跑真实训练, 秒级, <100MB)

验证三件事(对应 E6 三个判据):
  T1 顶得住 : 在模拟 BPR 收缩压力下(E2 实测 c 塌到 0.005), 加预算项能把 mean(c) 顶到 c_target 附近
  T2 双向控 : c_target=0.2 时应把 c 压**下去**(证明不是"惩罚太弱/太强", 而是真的在控制)
  T3 保判别 : 预算项只约束 batch 均值 -> conf_std 显著 >0(物品间仍分化);
              对照 idea3 的逐物品 (c_i-t)^2 -> conf_std 塌向 0(退化成软 force_c)

T3 是 E6 与 idea3 cost_reg 的分水岭, 也是"自适应应优于冻结 c"的前提.
用法: python _smoke_e6_budget.py
"""
import torch
import torch.nn as nn

from mm_align import MultiModalAligner

torch.manual_seed(0)

N, D = 400, 16
FEAT_DIMS = {'image_feat': 64, 'text_feat': 32}
STEPS = 400
# 模拟 BPR 的下压梯度: E2 证明 BPR 局部偏好丢弃多模态, 等效于对 c 的线性征税.
ADV_W = 0.5


def make_batch_c(aligner, feats, id_emb, idx):
    """走真实的 fuse_subset 通路拿到带梯度的 c(与 model.bpr_loss 完全一致)."""
    _, c = aligner.fuse_subset(feats, id_emb, idx)
    return c.squeeze(-1)


def run_arm(name, budget_t=0.0, budget_lam=0.0, dual_eta=0.0,
            per_item_t=0.0, per_item_w=0.0, adv_w=ADV_W):
    torch.manual_seed(0)
    aligner = MultiModalAligner(n_items=N, id_dim=D, feat_dims=FEAT_DIMS,
                                proj_hidden=32, conf_hidden=16)
    feats = {t: torch.randn(N, d) for t, d in FEAT_DIMS.items()}
    id_emb = torch.randn(N, D) * 0.3          # 冻结, 隔离出门控自身的行为
    opt = torch.optim.Adam(aligner.parameters(), lr=1e-2)

    idx = torch.arange(N)
    nu, nu_max = 0.0, 5.0
    for _ in range(STEPS):
        c = make_batch_c(aligner, feats, id_emb, idx)
        loss = adv_w * c.mean()                       # 模拟 BPR 收缩压力
        gap = budget_t - c.mean()
        if budget_lam > 0:                            # E6: 只约束批均值(二次/软)
            loss = loss + budget_lam * gap.pow(2)
        if dual_eta > 0:                              # E6: 增广拉格朗日乘子项
            loss = loss + nu * gap
            nu = max(-nu_max, min(nu_max, nu + dual_eta * float(gap.detach())))
        if per_item_w > 0:                            # idea3 对照: 逐物品
            loss = loss + per_item_w * (c - per_item_t).pow(2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()

    with torch.no_grad():
        c = make_batch_c(aligner, feats, id_emb, idx)
    return name, float(c.mean()), float(c.std()), float(c.min()), float(c.max())


def main():
    soft = [
        run_arm('soft t=0.8 lam=0.5', budget_t=0.8, budget_lam=0.5),
        run_arm('soft t=0.8 lam=1.0', budget_t=0.8, budget_lam=1.0),
        run_arm('soft t=0.8 lam=2.0', budget_t=0.8, budget_lam=2.0),
        run_arm('soft t=0.2 lam=1.0', budget_t=0.2, budget_lam=1.0),
    ]
    rows = [run_arm('无约束(模拟 E2)')] + soft + [
        run_arm('AL t=0.8 lam=1 eta=0.05', budget_t=0.8, budget_lam=1.0, dual_eta=0.05),
        run_arm('AL t=0.6 lam=1 eta=0.05', budget_t=0.6, budget_lam=1.0, dual_eta=0.05),
        run_arm('AL t=1.0 lam=1 eta=0.05', budget_t=1.0, budget_lam=1.0, dual_eta=0.05),
        run_arm('AL t=0.2 lam=1 eta=0.05', budget_t=0.2, budget_lam=1.0, dual_eta=0.05),
        run_arm('AL t=0.8 强压 A=2.0', budget_t=0.8, budget_lam=1.0, dual_eta=0.05, adv_w=2.0),
        run_arm('对照 idea3 逐物品 t=0.8', per_item_t=0.8, per_item_w=1.0),
    ]
    print(f"\n{'arm':28s} {'c_mean':>8s} {'c_std':>8s} {'c_min':>8s} {'c_max':>8s}")
    print('-' * 64)
    for n, m, s, lo, hi in rows:
        print(f'{n:28s} {m:8.4f} {s:8.4f} {lo:8.4f} {hi:8.4f}')

    print('\n--- 固定 lambda 的解析欠冲 c_bar = t - A/(2*lam) ---')
    for (n, m, *_), lam in zip(soft[:3], (0.5, 1.0, 2.0)):
        print(f'  {n:22s} 实测 {m:.4f}  预测 {0.8 - ADV_W / (2 * lam):.4f}')

    base = rows[0]
    al_08, al_06, al_10, al_02, al_hard = rows[5], rows[6], rows[7], rows[8], rows[9]
    per_item = rows[10]

    print('\n--- 判据 ---')
    t1 = al_08[1] >= 0.6
    print(f'T1 顶得住   mean {base[1]:.4f} -> {al_08[1]:.4f} (需 >=0.6): {"PASS" if t1 else "FAIL"}')
    t2 = abs(al_02[1] - 0.2) < 0.1 and al_02[1] < al_06[1] < al_08[1] < al_10[1]
    print(f'T2 双向控   t=0.2/0.6/0.8/1.0 -> '
          f'{al_02[1]:.3f}/{al_06[1]:.3f}/{al_08[1]:.3f}/{al_10[1]:.3f} '
          f'(需单调且 0.2 档命中): {"PASS" if t2 else "FAIL"}')
    t3 = al_08[2] > 3 * per_item[2]
    print(f'T3 保判别   E6 std {al_08[2]:.4f}  vs  逐物品 std {per_item[2]:.4f} '
          f'(需 E6 明显更大): {"PASS" if t3 else "FAIL"}')
    t4 = al_hard[1] >= 0.6
    print(f'T4 抗压强   A 从 0.5 加到 2.0 仍得 {al_hard[1]:.4f} (需 >=0.6, 证明与 A 无关): '
          f'{"PASS" if t4 else "FAIL"}')
    print(f'\n总体: {"ALL PASS" if (t1 and t2 and t3 and t4) else "有 FAIL, 需检查"}')


if __name__ == '__main__':
    main()
