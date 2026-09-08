"""
prism_moe.py — PRISM 交互专家 MoE 表征层（方案 A：表征级损失）

设计来源:
  - docs/prism_analysis.md §4（方案 A：专家在 64 维投影空间工作，损失算在专家输出嵌入上）
  - docs/prism_mixragrec_integration_plan.md §4（8 个工程坑，本文件逐条预修）
  - 上游移植源: baseline/PRISM/PRISM.py 的 Expert / InteractionExpertWrapper /
    Interaction_Expert_Layer / Adaptive_Fusion_Layer

===============================================================================
本文件已预修 §4 全部 8 个坑（移植必读，逐条对应）
===============================================================================
坑#1 epoch 缓存陷阱（最易踩）:
    本层**不做任何 epoch 级缓存**。输入必须是 mm_align.project_subset() 产出的
    「本 batch 子集、带梯度」的 64 维投影。专家层 128→64 很便宜，每 batch 实算。
    若照抄 mm_align.project() 的 epoch 缓存 → 20 epoch 仅 20 步梯度，专家训不动。
    => 本文件不提供 project()/refresh 类接口，从 API 层面就堵死这个坑。

坑#2 L_syn/L_rdn 数学对立（L_syn + L_rdn ≡ 1）:
    4 组专家参数**完全独立** —— 用 nn.ModuleDict，4 个各自的 Sequential，
    绝不共享任何 head。上游用 ModuleList + deepcopy(base_expert) 达到同样效果，
    这里改 ModuleDict 让 key 语义显式（uni_v/uni_t/syn/rdn），防后人误加共享层。

坑#3 余弦版 Triplet:
    上游 nn.TripletMarginLoss(margin=1.0, p=2) 是**欧氏距离**；LightGCN++ 有逐层
    L2 归一化，所有嵌入模长≈1，欧氏 margin=1.0 量纲无意义。
    => 本文件实现 _cos_triplet(): d = 1 - cos，默认 margin=0.2（cos 差值域 [-2,2]）。

坑#4 融合前 L2 归一化:
    专家输出先 F.normalize 再喂 AFL、再喂 e^(0)_item。否则尺度爆炸破坏图传播
    （表现为 conf_mean→1.0 门控失效）。见 fuse() 与 AdaptiveFusionLayer.forward()。

坑#5 三对比损失量纲打架:
    model.py:236 的 InfoNCE() 用 .sum() 而非 .mean()，量纲比本文件 λ 系列大约
    batch_size 倍。本文件所有损失一律 **.mean() 口径**，且在 loss_dict 里回传
    每项裸值（未乘 λ），便于 E18 逐个开、重校量纲。

坑#6 Dropout 死代码:
    上游 Expert.forward 里 `x = self.drop(x)` 作用在**输入 x** 上且赋值后不再使用
    → dropout 实际从未生效（死代码）。本文件真加 nn.Dropout 到 out 通路上，
    并用 dropout=0.0 作默认（保持"按原样=无 dropout"可复现），需要时显式开。

坑#7 num_experts_per_type 必须 =1:
    上游 forward 用 expert_outputs[-2]/[-1] 硬索引取 syn/rdn，>1 会索引错位。
    本文件用 4 个具名专家彻底消除该隐患（无 num_experts_per_type 参数）。

坑#8 图结构缓存命名:
    本层**不改图结构**，可安全复用 s_pre_adj_mat_{alpha}_{beta}.npz。
    若后续做"多模态 item-item 图"扩展，必须把新参数写进 npz 文件名防静默加载旧图。

===============================================================================
状态: B 骨架（已写）。E14/E14-bis 合成探针 + E15 原码复现已落地。
E15c 新增 ② 互补利用分支：PRISMExpertLayer.syn_complement()（syn 在单模态子空间正交补）
+ PRISMComplementarityNet（uni_head 主预测 + comp_head 残差预测，显式路由 syn 互补信号）。
===============================================================================
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

# 专家语义 key（顺序固定，AFL 权重维度与之对齐）
EXPERT_KEYS = ("uni_v", "uni_t", "syn", "rdn")


def _l2(x):
    return F.normalize(x, p=2, dim=-1)


class Expert(nn.Module):
    """单个交互专家: [2d] -> hidden -> [d]。

    对应上游 PRISM.py:10 Expert，修坑#6（dropout 死代码）:
    上游写 `x = self.drop(x)` 作用在输入并丢弃结果 → dropout 从未生效。
    这里把 dropout 正确放在激活后的 out 通路上。
    """

    def __init__(self, input_size, output_size, hidden_size, dropout=0.0):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.act = nn.GELU()
        # 坑#6: 默认 0.0 = "按原样=无 dropout"（可复现上游行为）; 需要时显式传值
        self.drop = nn.Dropout(dropout)
        self._init_weights()

    def _init_weights(self):
        for m in (self.fc1, self.fc2):
            nn.init.xavier_uniform_(m.weight)
            nn.init.zeros_(m.bias)

    def forward(self, x):
        out = self.act(self.fc1(x))
        out = self.drop(out)          # 坑#6 修复: 真正作用在前向通路上
        return self.fc2(out)


class InteractionExpertWrapper(nn.Module):
    """把「模态消融」前向封进专家（对应上游 PRISM.py:27）。

    forward_multiple 返回 [完整, 消融模态0, 消融模态1]:
      - 完整      = cat(img, txt) 全信息
      - 消融模态i = 第 i 路换成同形状高斯噪声（保尺度、去信息）
    三者对比即构成 uniqueness / synergy / redundancy 三种损失的素材。
    """

    def __init__(self, expert_model):
        super().__init__()
        self.expert_model = expert_model

    def _forward_with_replacement(self, inputs, replace_index=None):
        xs = list(inputs)
        if replace_index is not None:
            # 用高斯噪声替换该模态（与上游一致）; 不用 zeros 以免退化成 bias-only
            xs[replace_index] = torch.randn_like(xs[replace_index])
        return self.expert_model(torch.cat(xs, dim=-1))

    def forward(self, inputs):
        return self._forward_with_replacement(inputs, replace_index=None)

    def forward_multiple(self, inputs):
        outs = [self.forward(inputs)]
        for i in range(len(inputs)):
            outs.append(self._forward_with_replacement(inputs, replace_index=i))
        return outs


class AdaptiveFusionLayer(nn.Module):
    """AFL: 把 4 路专家嵌入自适应融合成物品多模态表示（对应上游 Adaptive_Fusion_Layer）。

    afl_mode（对应实验矩阵 A2-1/2/3，E15 只开 item，E17 再升级）:
      - 'item' (A2-1): 物品级权重，w = softmax(MLP(cat(4 专家)) / τ)   ← E15 起步
      - 'user' (A2-2): 额外接收用户嵌入，w 由 (item, user) 共同决定    ← E17
      - 'dual' (A2-3): item 与 user 两阶段权重相乘再归一化             ← E17

    坑#4: 输入的 4 路专家嵌入必须已 L2 归一化，本层内部再次 normalize 兜底；
          输出同样 L2 归一化后才允许喂 e^(0)_item。
    """

    def __init__(self, dim, n_experts=4, hidden=64, temperature=1.0,
                 afl_mode="item", dropout=0.0):
        super().__init__()
        assert afl_mode in ("item", "user", "dual")
        self.afl_mode = afl_mode
        self.temperature = temperature
        self.n_experts = n_experts

        in_dim = dim * n_experts
        self.item_gate = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hidden, n_experts),
        )
        # A2-2/A2-3 用户侧门控（E15 不启用，占位以免 E17 改结构）
        self.user_gate = None
        if afl_mode in ("user", "dual"):
            self.user_gate = nn.Sequential(
                nn.Linear(dim + in_dim, hidden), nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(hidden, n_experts),
            )
        self._init_weights()

    def _init_weights(self):
        for mod in (self.item_gate, self.user_gate):
            if mod is None:
                continue
            for m in mod:
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    nn.init.zeros_(m.bias)

    def forward(self, expert_embs, user_emb=None):
        """expert_embs: dict[key] -> [B, d]（已 L2）。返回 (fused[B,d], w[B,4])。"""
        stack = torch.stack([_l2(expert_embs[k]) for k in EXPERT_KEYS], dim=1)  # [B,4,d]
        flat = stack.flatten(1)                                                # [B,4d]

        logit = self.item_gate(flat)
        if self.afl_mode in ("user", "dual") and user_emb is not None:
            u_logit = self.user_gate(torch.cat([_l2(user_emb), flat], dim=-1))
            logit = u_logit if self.afl_mode == "user" else logit + u_logit

        w = torch.softmax(logit / max(self.temperature, 1e-6), dim=-1)         # [B,4]
        fused = (w.unsqueeze(-1) * stack).sum(1)                               # [B,d]
        return _l2(fused), w                                                   # 坑#4


class PRISMExpertLayer(nn.Module):
    """PRISM 交互专家层 + 3 类交互损失（对应上游 Interaction_Expert_Layer）。

    坑#2: 4 组专家用 ModuleDict 各自独立 Sequential，**绝不共享**。
    坑#7: 无 num_experts_per_type，4 个具名专家，杜绝硬索引错位。
    坑#1: 只接受 batch 子集输入，无 epoch 缓存接口。

    调用约定（E15 在 mm_align.use_prism 分支里）:
        out = prism(img_proj_sub, txt_proj_sub)      # 均为 [B, d] 带梯度
        out['expert_embs'] -> 4 路 [B,d]（已 L2）
        out['fused']       -> AFL 融合后 [B,d]（已 L2，可喂 e^(0)_item）
        out['loss']        -> 已按 λ 加权的标量
        out['loss_dict']   -> 各项**裸值**（未乘 λ），供 E18 重校量纲
        out['div']         -> 专家两两余弦均值（Idea-γ 分化度信号 / 决策门指标）
    """

    def __init__(self, dim=64, expert_hidden=128, dropout=0.0,
                 lambda_uni_v=0.1, lambda_uni_t=0.1,
                 lambda_syn=0.1, lambda_rdn=0.1,
                 margin=0.2, afl_mode="item", afl_temperature=1.0,
                 use_afl=True, syn_anchor_lambda=0.0, syn_anchor_mode="cos"):
        super().__init__()
        self.dim = dim
        self.n_modalities = 2                    # img, txt
        self.margin = margin                     # 坑#3: 余弦 margin，非欧氏 1.0
        # E14-bis 锚定: syn_anchor_lambda>0 时，forward 传 syn_target 加「真值重建」辅助损失，
        # 把 syn 专家锚定到真值协同信号（解决 E14 中 L_syn 仅几何 decorrelation 的缺陷）。
        # syn_anchor_mode: 'cos'（1-cos 距离，与 L_syn 同量纲，默认）| 'mse'（per-element 重建）。
        # 关键: naive MSE 锚定因 per-element 平均 + 单位向量，梯度量级比 L_syn(mean cos) 小 ~d 倍，
        # 即便 λ 同也会被 L_syn 淹没（E14-bis 诊断已证）→ 默认 cos 距离锚定。
        self.syn_anchor_lambda = syn_anchor_lambda
        self.syn_anchor_mode = syn_anchor_mode

        # ---- 坑#2 / 坑#7: 4 组完全独立的具名专家 ----
        self.experts = nn.ModuleDict({
            k: InteractionExpertWrapper(
                Expert(input_size=dim * self.n_modalities,
                       output_size=dim,
                       hidden_size=expert_hidden,
                       dropout=dropout)
            ) for k in EXPERT_KEYS
        })

        self.lambdas = {
            "uniqueness_v": lambda_uni_v,
            "uniqueness_t": lambda_uni_t,
            "synergy": lambda_syn,
            "redundancy": lambda_rdn,
        }

        self.use_afl = use_afl
        self.afl = AdaptiveFusionLayer(
            dim=dim, n_experts=len(EXPERT_KEYS), hidden=dim,
            temperature=afl_temperature, afl_mode=afl_mode, dropout=dropout,
        ) if use_afl else None

    # ---------------- 损失（坑#3 余弦化 / 坑#5 统一 .mean() 口径） ----------------
    def _cos_triplet(self, anchor, pos, neg):
        """坑#3: 余弦版 Triplet。d = 1 - cos，loss = relu(margin + d(a,p) - d(a,n))
                                            = relu(margin - cos(a,p) + cos(a,n))
        语义: anchor(完整) 应**远离** neg(该模态被毁) 而**靠近** pos(其他模态被毁)
              => 该专家的输出主要由本模态决定 = uniqueness。
        """
        a, p, n = _l2(anchor), _l2(pos), _l2(neg)
        cos_p = (a * p).sum(-1)
        cos_n = (a * n).sum(-1)
        return F.relu(self.margin - cos_p + cos_n).mean()

    def _synergy_loss(self, anchor, negatives):
        """Syn 专家: 完整输出要**远离**所有单模态残缺版（越协同越不可由单模态复原）。
        loss = mean cos(anchor, neg) —— 越小越好。"""
        a = _l2(anchor)
        return torch.stack([(a * _l2(n)).sum(-1).mean() for n in negatives]).mean()

    def _redundancy_loss(self, anchor, positives):
        """Rdn 专家: 完整输出要**贴近**单模态残缺版（任一模态都能复原 = 冗余）。
        loss = mean (1 - cos) —— 越小越好。
        注意坑#2: 与 _synergy_loss 数学对立，故两者必须是**不同参数**的专家。"""
        a = _l2(anchor)
        return torch.stack([(1 - (a * _l2(p)).sum(-1)).mean() for p in positives]).mean()

    @staticmethod
    def expert_divergence(expert_embs):
        """Idea-γ 分化度: 4 专家两两余弦均值 div。
        决策门: div > 0.95 = 四个一样的 MLP，无论 R@20 涨跌都不能声称解耦。
        也可当 early-stop 信号 / (1-div) 当正则项。"""
        mats = torch.stack([_l2(expert_embs[k]) for k in EXPERT_KEYS], dim=0)  # [4,B,d]
        sims = []
        for i in range(len(EXPERT_KEYS)):
            for j in range(i + 1, len(EXPERT_KEYS)):
                sims.append((mats[i] * mats[j]).sum(-1).mean())
        return torch.stack(sims).mean()

    def forward(self, img_proj, txt_proj, user_emb=None, syn_target=None):
        """img_proj/txt_proj: [B, dim]，必须来自 project_subset（带梯度、本 batch 子集）。

        坑#1: 这里没有任何缓存；每次调用都实算。B 通常 = cat(pos,neg).unique() ≈ 22% 物品。
        """
        assert img_proj.dim() == 2 and txt_proj.dim() == 2, \
            "prism_moe 只接受 [B, dim] 的 batch 子集投影（坑#1: 禁止全量/epoch 缓存）"
        inputs = [img_proj, txt_proj]

        # 每个专家各自跑 [完整, 消融img, 消融txt]
        outs = {k: self.experts[k].forward_multiple(inputs) for k in EXPERT_KEYS}

        # --- uniqueness: uni_v 由 img 主导 / uni_t 由 txt 主导 ---
        # outs[k] = [full, ablate_img, ablate_txt]; 消融索引 = 模态序号 + 1
        uni_losses = {}
        for mi, key in enumerate(("uni_v", "uni_t")):
            o = outs[key]
            anchor = o[0]
            neg = o[mi + 1]                                   # 毁掉本模态 → 应远离
            positives = [o[j + 1] for j in range(self.n_modalities) if j != mi]
            uni_losses[key] = torch.stack(
                [self._cos_triplet(anchor, p, neg) for p in positives]
            ).mean()

        syn_loss = self._synergy_loss(outs["syn"][0], outs["syn"][1:])
        rdn_loss = self._redundancy_loss(outs["rdn"][0], outs["rdn"][1:])

        # 坑#5: loss_dict 存**裸值**（未乘 λ），量纲一律 .mean()，便于 E18 重校
        loss_dict = {
            "uniqueness_v": uni_losses["uni_v"],
            "uniqueness_t": uni_losses["uni_t"],
            "synergy": syn_loss,
            "redundancy": rdn_loss,
        }
        total = sum(self.lambdas[k] * v for k, v in loss_dict.items())

        # 坑#4: 专家嵌入先 L2 再交给 AFL / e^(0)_item
        expert_embs = {k: _l2(outs[k][0]) for k in EXPERT_KEYS}

        # E14-bis 锚定辅助损失：syn 专家直接回归真值协同分量 syn_target。
        # 解决 E14 根因（L_syn 仅几何 decorrelation，未锚定真值 → syn 专家学任意正交方向）。
        # 仅当 syn_anchor_lambda>0 且训练期提供 syn_target（合成探针里 = 真值 c_syn）时生效；
        # 真实场景里 syn_target 应是残差/辅助任务构造的 proxy（E14-bis 证机制健全后另设计）。
        if syn_target is not None and self.syn_anchor_lambda > 0:
            st = _l2(syn_target.to(expert_embs["syn"].device).float())
            if self.syn_anchor_mode == "mse":
                anchor = F.mse_loss(expert_embs["syn"], st)
            else:  # 'cos'（默认）：1-cos 距离，与 L_syn(mean cos) 同量纲，梯度量级可比
                anchor = (1.0 - (expert_embs["syn"] * st).sum(-1).mean())
            loss_dict["syn_anchor"] = anchor
            total = total + self.syn_anchor_lambda * anchor

        fused, afl_w = (None, None)
        if self.use_afl:
            fused, afl_w = self.afl(expert_embs, user_emb=user_emb)

        with torch.no_grad():
            div = self.expert_divergence(expert_embs)
            # A2-2/3 决策门: 4 类权重熵 < 1.3 nats（非均分才算真"自适应"）
            ent = None
            if afl_w is not None:
                ent = -(afl_w.clamp_min(1e-9).log() * afl_w).sum(-1).mean()

        return {
            "loss": total,
            "loss_dict": {k: float(v.detach()) for k, v in loss_dict.items()},
            "expert_embs": expert_embs,
            "fused": fused,
            "afl_w": afl_w,
            "div": float(div),
            "afl_entropy": None if ent is None else float(ent),
        }


    # ────────────────────────────── ② 互补利用分支（E15c）──────────────────────────────
    def syn_complement(self, expert_embs):
        """syn 在单模态专家 {uni_v, uni_t} 张成子空间上的**正交补** = 纯互补/多样性信号。

        机制（对应观点②）：L_syn 把 syn 锁在「远离单模态残缺版」的正交子空间，
        这个残差本身不等于 PID 真值协同（E14-bis 已证），但它是**单模态独立专家给不出的
        互补信息**。本方法把 syn 投影到单模态子空间并取残差，得到「正交补」——
        即 syn 中**完全不能被 uni_v/uni_t 表达的**那部分，正是推荐可用的多样性信号。

        Gram-Schmidt 正交化 uni_v/uni_t 后取投影残差（避免 2×2 求逆，数值稳定）。
        """
        uv = _l2(expert_embs["uni_v"])
        ut = _l2(expert_embs["uni_t"])
        s = _l2(expert_embs["syn"])
        # 正交化：u_t' = u_t - (u_t·u_v) u_v
        utp = _l2(ut - (ut * uv).sum(-1, keepdim=True) * uv)
        proj = ((s * uv).sum(-1, keepdim=True)) * uv \
             + ((s * utp).sum(-1, keepdim=True)) * utp
        return _l2(s - proj)


class PRISMComplementarityNet(nn.Module):
    """② 互补利用网络：把 syn 正交残差**显式路由**成推荐预测的补项。

    与当前骨架（PRISMExpertLayer 仅把 syn 丢进 AFL）的关键区别：
      当前骨架 syn 是否被用，完全由 AFL 权重决定——E14-bis 证 AFL 可把 syn 压成弱权重
      → syn 退化为 decorrelated 噪声，无预测贡献。
      本网络额外加：
        (1) syn_complement = syn 在单模态子空间的正交补（纯互补信号，见 syn_complement）
        (2) comp_head: 把 syn_complement 映射为「残差预测」comp_logit
        (3) uni_head: 把 uni 三专家均值池(uni_base) 映射为「主预测」uni_logit
        (4) pred = uni_logit + comp_logit  （残差学习：syn 专补 uni 给不出的部分）
      → syn 拿到**独立于 AFL 权重的直接预测梯度**，被迫承载互补信息（不再只是 decorrelation 正则）。

    交互损失（L_syn 等）照常施加，保证 syn 仍是正交多样性残差；comp_head 则把它**用起来**。
    """

    def __init__(self, dim=64, expert_hidden=128, dropout=0.0, **kw_layer):
        super().__init__()
        self.prism = PRISMExpertLayer(
            dim=dim, expert_hidden=expert_hidden, dropout=dropout, **kw_layer)
        self.uni_head = nn.Linear(dim, dim)
        self.comp_head = nn.Linear(dim, dim)
        # 兼容 ex14/ex14bis 的 model.head(out["fused"]) 写法（冗余，但保留接口）
        self.head = nn.Linear(dim, dim)

    def forward(self, img_proj, txt_proj, syn_target=None):
        out = self.prism(img_proj, txt_proj, syn_target=syn_target)
        emb = out["expert_embs"]
        uni_base = _l2((emb["uni_v"] + emb["uni_t"] + emb["rdn"]) / 3.0)
        syn_c = self.prism.syn_complement(emb)
        pred = self.uni_head(uni_base) + self.comp_head(syn_c)
        return {
            "pred": pred,
            "fused": out["fused"],
            "expert_embs": emb,
            "syn_complement": syn_c,
            "loss": out["loss"],
            "loss_dict": out["loss_dict"],
            "div": out["div"],
            "afl_w": out["afl_w"],
        }

    def synergy_complementary_loss(self, syn_perp, y_proxy):
        """E14-ter 显式互补损失：comp_head 把 syn 正交补 syn_⊥ 映射为 y_proxy 的预测，
        直接监督 syn_⊥ 承载「与 y 相关、但在单模态子空间正交补方向」的互补内容。

        合成体制 y_proxy = c_syn（真值协同）；真实体制 y_proxy = 下一 item 推荐监督。
        关键不变量：syn_⊥ = syn − P_E(syn) 已强制 ∈ E^⊥（见 PRISMExpertLayer.syn_complement），
        故 L_comp 只能从 E 之外学 y 信息 → 与 L_syn(old) 几何一致、**无梯度抵消**
        （修复 E14-bis：旧锚定把 syn 直接回归 c_syn，与 L_syn 在参数空间冲突被锁死）。"""
        pred = self.comp_head(syn_perp)
        return F.mse_loss(pred, y_proxy)


def build_prism_moe(args=None, dim=64, **kw):
    """工厂: 从 args（run_prism.py / parse.py 传入）构造 PRISMExpertLayer。

    E15 λ 网格（§6，固定 λ_rdn=0.1，λ_uni_i=λ_uni_t=λ_uni）:
        λ_uni × λ_syn ∈ {0.05, 0.1, 0.5}² = 9 组，单 seed 20 ep 选优 → +3 seed 出终数。
    """
    def _g(name, default):
        return getattr(args, name, default) if args is not None else kw.get(name, default)

    lam_uni = _g("prism_lambda_uni", 0.1)
    return PRISMExpertLayer(
        dim=dim,
        expert_hidden=_g("prism_expert_hidden", 128),
        dropout=_g("prism_dropout", 0.0),
        lambda_uni_v=lam_uni,
        lambda_uni_t=lam_uni,
        lambda_syn=_g("prism_lambda_syn", 0.1),
        lambda_rdn=_g("prism_lambda_rdn", 0.1),
        margin=_g("prism_margin", 0.2),
        afl_mode=_g("afl_mode", "item"),
        afl_temperature=_g("afl_temperature", 1.0),
        # E16 消融 w/o L_exp: 保留 4 专家（容量不变）但不加 prism_loss
        use_afl=_g("prism_use_afl", True),
    )


def build_prism_complementarity(args=None, dim=64, **kw):
    """② 互补利用网络工厂（E15c）：把 syn 正交残差显式路由成推荐预测的补项。"""
    def _g(name, default):
        return getattr(args, name, default) if args is not None else kw.get(name, default)
    lam_uni = _g("prism_lambda_uni", 0.1)
    return PRISMComplementarityNet(
        dim=dim,
        expert_hidden=_g("prism_expert_hidden", 128),
        dropout=_g("prism_dropout", 0.0),
        lambda_uni_v=lam_uni,
        lambda_uni_t=lam_uni,
        lambda_syn=_g("prism_lambda_syn", 0.1),
        lambda_rdn=_g("prism_lambda_rdn", 0.1),
        margin=_g("prism_margin", 0.2),
        afl_mode=_g("afl_mode", "item"),
        afl_temperature=_g("afl_temperature", 1.0),
        use_afl=_g("prism_use_afl", True),
    )


def export_pid_components(prism_layer, img_proj_full, txt_proj_full, path,
                          batch_size=4096):
    """把训好的 4 路专家嵌入落盘为 pid_diagnostic.load_prism_moe() 期望的 npz。

    期望键（见 pid_diagnostic.py:270 load_prism_moe）: unq_img / unq_txt / red / syn。
    这是 P6 钩子：落盘后 E-X1 诊断即可用**真实分解分量**替换代理信号做真实归因。
    注意此处是**推理导出**（no_grad + 全量），与训练期坑#1 无冲突。
    """
    import numpy as np
    prism_layer.eval()
    buf = {k: [] for k in EXPERT_KEYS}
    with torch.no_grad():
        for s in range(0, img_proj_full.shape[0], batch_size):
            e = prism_layer(img_proj_full[s:s + batch_size],
                            txt_proj_full[s:s + batch_size])["expert_embs"]
            for k in EXPERT_KEYS:
                buf[k].append(e[k].cpu().numpy())
    out = {k: np.concatenate(v, axis=0) for k, v in buf.items()}
    np.savez(path,
             unq_img=out["uni_v"], unq_txt=out["uni_t"],
             red=out["rdn"], syn=out["syn"])
    prism_layer.train()
    return path
