"""
mm_align.py — idea2: 知识对齐（结构化 → 统一表示）的中间步骤

设计来源: docs/lightgcnpp_migration_design.md §2 (MixRAGRec Knowledge Alignment Agent 迁移)
核心原则: 不要直接把异构视觉特征拼进 LightGCN++ 的传播; 先做显式对齐再融合, 并附置信度.
原因: LightGCN++ 每层做逐节点 L2 归一化, 对嵌入尺度/分布极度敏感, 直接 concat 会破坏尺度假设.

三级对齐(本文件实现):
  G1 类型级  —— 每种特征类型(如 CNN / CLIP / 多视角)有独立投影头 + 可学习类型嵌入
  G2 物品级  —— 类型感知门控(不简单平均) 把多类型视图聚合成物品统一视觉表示
  G3 跨模态  —— 置信度门控 c_i = σ(cos(P(v_i), e_i^ID)), 图文不符物品自动退化为纯 ID

训练期对比损失(视图一致性 InfoNCE): 同一物品的不同类型/视角应彼此靠近, 不同物品应远离.
这与 idea4 NLGCL 的层间对比互补, 但作用在"模态轴"而非"层轴".

数据约定: feats 是 {type_name: Tensor[n_items, feat_dim]} 的字典, 第 i 行 = item i 的特征.
           image_feat.npy 行序与 dataloader 的 item 索引 1:1 对齐(MMSSL/LATTICE 约定).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiModalAligner(nn.Module):
    def __init__(self, n_items, id_dim, feat_dims, proj_hidden=256,
                 temperature=0.1, conf_hidden=64, dropout=0.1, types_order=None):
        """
        Args:
            n_items:    物品数(= dataset.m_items)
            id_dim:     LightGCN++ 嵌入维度 d
            feat_dims:  dict, 例如 {'cnn': 4096, 'clip': 64}  (与 MMSSL 维度一致)
            proj_hidden:投影头中间维度
            temperature:InfoNCE 温度
            conf_hidden:置信度 MLP 隐藏维度
            types_order:类型顺序(决定门控维度), 默认按 feat_dims 键序
        """
        super().__init__()
        self.n_items = n_items
        self.id_dim = id_dim
        self.types = types_order or list(feat_dims.keys())
        self.temperature = temperature

        # ---- G1 类型级: 每种类型独立投影头 + 可学习类型嵌入 ----
        # 投影: 视觉特征 → ID 空间(两层 MLP + L2 归一化, 对齐尺度)
        self.proj = nn.ModuleDict()
        self.type_emb = nn.ParameterDict()
        for t in self.types:
            fd = feat_dims[t]
            self.proj[t] = nn.Sequential(
                nn.Linear(fd, proj_hidden),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(proj_hidden, id_dim),
            )
            # 每个类型一个可学习原型嵌入, 用于类型感知门控打分.
            # 注意: 不能初始化为 0 —— F.normalize(0)=0 会使 gate_scores 恒为 0,
            # softmax 退化为均匀平均(门控失效). 用小幅随机初始化让各类型起步即有区分.
            self.type_emb[t] = nn.Parameter(torch.randn(id_dim) * 0.1)

        # ---- G3 置信度头: 由 (视觉表示 - ID嵌入) 预测对齐置信度 ----
        self.conf_mlp = nn.Sequential(
            nn.Linear(id_dim * 2, conf_hidden),
            nn.ReLU(),
            nn.Linear(conf_hidden, 1),
        )

        self._init_weights()

        # 全量投影的 epoch 级缓存(no_grad, 仅供图传播读取).
        # proj 头的梯度不走这条路, 而由 project_subset() 每 batch 提供, 见 project() 注释.
        self._proj_cache = None
        self._proj_epoch = -1
        self._epoch = 0

    def set_epoch(self, e):
        """由 model.mm_new_epoch() 在每个训练 epoch 开始时调用, 触发全量投影缓存刷新."""
        self._epoch = e

    def _init_weights(self):
        for t in self.types:
            for m in self.proj[t]:
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    nn.init.zeros_(m.bias)
        for m in self.conf_mlp:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    @staticmethod
    def _l2(x):
        return F.normalize(x, p=2, dim=-1)

    def _compute_proj(self, feats):
        """G1: 每种类型投影 + L2 归一化(实际计算, 带梯度)."""
        out = {}
        for t in self.types:
            if t not in feats or feats[t] is None:
                continue
            v = self.proj[t](feats[t].float())          # [n, d]
            out[t] = self._l2(v)
        return out

    def project(self, feats, epoch=None):
        """全量投影(no_grad + epoch 级缓存), 仅供 fuse() 生成全部物品的 e^(0) 给图传播.

        ## 为什么这里不带梯度
        图传播需要全部 n_items 个物品的投影. 本数据集 18357 物品 × 4096 维 CNN 特征,
        单线程 CPU 实测一次带梯度的全量 fwd+bwd 约 2502ms; 若每 batch 都算,
        94 batch × 2502ms = +235s/epoch(单轮从 132s 涨到 367s, +178%), 不可接受.

        ## proj 头的梯度从哪来
        v2 的实现里 project_subset 只接进了 contrastive_loss(InfoNCE, 权重 1e-3),
        而 BPR 用的 e^(0)_item 来自本方法返回的 no_grad 缓存 -> BPR 完全够不到 proj 头,
        proj 头 100% 由 InfoNCE 驱动, conf_mean 反而跌到 0.026(实测).
        v3 修复: fuse_subset() 用 project_subset 对本 batch 子集做带梯度融合,
        并把结果拼回 light_out 的 gamma·embs_zero 项, BPR 梯度即可沿直通路回到 proj 头;
        type_emb / conf_mlp 也借此收梯度. 开销: project_subset 每 batch 只算一次(~280ms),
        InfoNCE 与 BPR 复用同一份子集投影.

        ## 历史缺陷记录
        原实现返回 detach 缓存却仍把「刷新 batch」的带梯度结果透出, 导致 proj 头
        20 个 epoch 全程只走 20 个 Adam step, 等效冻结; 而 conf_mlp / type_emb / id_emb
        每 batch 都更新(1880 步). 门控因此在 5 个 epoch 内就把 c 从 0.5 压到 0.09
        —— 它关掉的确实是一堆近似随机的投影噪声. 这才是 idea2 零增益的根因
        (尺度失配虽真实存在, 修复后 conf_mean 仅 0.093 -> 0.091, 并非主因).
        """
        if epoch is None:
            epoch = self._epoch
        if self._proj_cache is None or self._proj_epoch != epoch:
            with torch.no_grad():
                self._proj_cache = self._compute_proj(feats)
            self._proj_epoch = epoch
        return self._proj_cache

    def project_subset(self, feats, idx):
        """仅对本 batch 参与 loss 的物品做**带梯度**的新鲜投影 —— proj 头唯一的梯度来源.

        成本与 len(idx) 成正比: 2048 物品约 280ms(全量 18357 是 2502ms).
        注意必须重新前向, 不能从 self._proj_cache 里切片(那是 no_grad 结果, 无梯度).
        """
        out = {}
        for t in self.types:
            if t not in feats or feats[t] is None:
                continue
            out[t] = self._l2(self.proj[t](feats[t][idx].float()))   # [len(idx), d]
        return out

    def gate_weights(self, proj_feats):
        """G2 类型感知门控: 不简单平均.
        每个物品按 '各类型投影与对应类型原型的余弦相似度' 做 softmax,
        使信息密度高的类型(如主图/CNN)获得更高权重.
        返回 {t: [n_items, 1]} 门控权重(已归一化, 和为1)."""
        scores = {}
        for t, vt in proj_feats.items():
            proto = self._l2(self.type_emb[t])                 # [d]
            sim = (vt * proto.unsqueeze(0)).sum(-1, keepdim=True)  # [n,1] 余弦(已归一化)
            scores[t] = sim
        # 拼接后 softmax(按类型维)
        stacked = torch.cat([scores[t] for t in proj_feats.keys()], dim=-1)  # [n, n_types]
        w = torch.softmax(stacked, dim=-1)                    # [n, n_types]
        return {t: w[:, i:i + 1] for i, t in enumerate(proj_feats.keys())}

    def fuse(self, feats, id_emb):
        """主前向: 投影 → 门控池化 → 置信度门控残差融合.
        Args:
            feats:  {t: [n_items, feat_dim]}
            id_emb: [n_items, d]  ID 嵌入(通常传 embedding_item.weight, 计算置信度时 detach 防捷径)
        Returns:
            fused:      [n_items, d]  融合后 e^(0)_item
            info:       dict          诊断量(置信度均值/分布/各类型门控均值)
        """
        proj_feats = self.project(feats)
        # 缓存投影结果, 供 contrastive_loss 复用(避免每个 batch 重复投影全量物品)
        self._last_proj_feats = proj_feats
        if not proj_feats:
            # 无可用特征 → 原样返回 ID 嵌入
            return id_emb, {'conf_mean': 0.0, 'n_types': 0}

        gates = self.gate_weights(proj_feats)
        # G2 池化: 加权求和(不是平均)
        pooled = sum(gates[t] * proj_feats[t] for t in proj_feats.keys())  # [n, d]
        pooled = self._l2(pooled)

        # G3 置信度门控: c_i = σ(cos(P(v_i), e_i^ID))
        id_det = self._l2(id_emb.detach())
        v_norm = pooled                                            # 146 行已 L2 归一化
        cos = (v_norm * id_det).sum(-1, keepdim=True)              # [n,1]
        conf_in = torch.cat([v_norm, id_det], dim=-1)              # [n, 2d]
        conf_logit = self.conf_mlp(conf_in)                        # [n,1]
        # 让余弦相似度本身也参与门控信号(可解释): c = σ(conf_logit + 2*cos)
        c = torch.sigmoid(conf_logit + 2.0 * cos)                 # [n,1] ∈ (0,1)

        # 范数对齐(尺度修复): pooled 经 L2 后模长恒为 1 且全物品相同,
        # 而 id_emb 模长≈0.8 且随流行度分化. 直接残差会让 c→1 抹掉流行度信息、
        # 与 CF 方向冲突, 迫使 BPR 把 c 压到极小(实测 conf_mean=0.088).
        # 这里只让多模态提供"方向", 模长沿用该物品自身的 ID 嵌入模长
        # (detach 防止模型通过缩小 id_emb 范数走捷径).
        id_scale = id_emb.norm(dim=-1, keepdim=True).detach()      # [n,1]
        pooled_scaled = pooled * id_scale                          # [n,d] 同模长, 仅换方向

        # 残差融合: 图文相符(c→1)则引入视觉; 不符(c→0)则退化为纯 ID
        fused = id_emb + c * (pooled_scaled - id_emb)

        info = {
            'conf_mean': float(c.mean().item()),
            'conf_std': float(c.std().item()),
            'conf_min': float(c.min().item()),
            'conf_max': float(c.max().item()),
            'gate_mean': {t: float(gates[t].mean().item()) for t in gates},
            'n_types': len(proj_feats),
            'conf_vec': c,                 # [n_items, 1] 逐物品知识引入权重(供 idea3 成本项使用)
        }
        return fused, info

    def fuse_subset(self, feats, id_emb, idx):
        """对本 batch 参与 loss 的物品(pos+neg 去重后)做**带梯度**的融合 e^(0)_item,
        并把投影结果缓存供 contrastive_loss 复用(避免二次 project_subset).

        ## 关键: 这是 BPR 梯度回到 proj 头 / type_emb / conf_mlp 的唯一通道
        v2 只用 project() 的 no_grad 全量缓存喂 fuse(), 导致 BPR 完全够不到投影头,
        投影头 100% 由权重仅 1e-3 的 InfoNCE 驱动 -> conf_mean 反而跌到 0.026.
        这里用 project_subset(带梯度)重算 batch 子集的 e^(0)_item, 拼回
        light_out 的 gamma·embs_zero 项, BPR 梯度即可沿这条直通路回到 proj 头.
        开销: project_subset 每 batch 仅算一次(约 280ms), InfoNCE 与 BPR 复用同一结果."""
        proj_feats = self.project_subset(feats, idx)        # 带梯度, [len(idx), d]
        if not proj_feats:
            return None, None
        # 缓存供 contrastive_loss 复用
        self._subset_proj_feats = proj_feats
        self._subset_idx = idx

        gates = self.gate_weights(proj_feats)               # type_emb 在此收梯度
        pooled = sum(gates[t] * proj_feats[t] for t in proj_feats.keys())
        pooled = self._l2(pooled)

        id_det = self._l2(id_emb[idx].detach())
        v_norm = pooled
        cos = (v_norm * id_det).sum(-1, keepdim=True)
        conf_in = torch.cat([v_norm, id_det], dim=-1)
        conf_logit = self.conf_mlp(conf_in)                # conf_mlp 在此收梯度
        c = torch.sigmoid(conf_logit + 2.0 * cos)

        id_scale = id_emb[idx].norm(dim=-1, keepdim=True).detach()
        pooled_scaled = pooled * id_scale
        fused = id_emb[idx] + c * (pooled_scaled - id_emb[idx])   # 带梯度
        return fused, c

    def contrastive_loss(self, idx=None, feats=None):
        """视图一致性 InfoNCE(训练损失项) —— 同时是 proj 头的梯度入口.

        同一物品的不同类型视图互为正例, batch 内其他物品为负例.

        Args:
            idx:   长整型张量, 本 batch 参与 loss 的物品下标(pos+neg 去重后).
            feats: 原始特征字典. **传入时**对 idx 重新做带梯度投影
                   (project_subset), 使 proj 头每个 batch 都收到梯度;
                   为 None 时退化为读 fuse() 的 no_grad 缓存(无梯度, 仅兼容旧调用).
        """
        # 优先复用 fuse_subset 已算好的带梯度子集(避免二次 project_subset)
        cache = getattr(self, '_subset_proj_feats', None)
        cache_idx = getattr(self, '_subset_idx', None)
        if cache is not None and cache_idx is not None and idx is not None \
                and cache_idx.shape == idx.shape and torch.equal(cache_idx, idx):
            proj_feats = cache
            sub = None
        elif feats is not None and idx is not None and idx.numel() > 1:
            proj_feats = self.project_subset(feats, idx)   # 带梯度, 已按 idx 取子集
            sub = None
        else:
            proj_feats = getattr(self, '_last_proj_feats', None)
            sub = idx
        if not proj_feats:
            return torch.tensor(0.0, device=next(self.parameters()).device)
        types = list(proj_feats.keys())
        if len(types) < 2:
            return torch.tensor(0.0, device=next(self.parameters()).device)

        def _get(t):
            v = proj_feats[t]
            return v[sub] if sub is not None else v

        a = self._l2(_get(types[0]))     # [B, d] anchor
        b = self._l2(_get(types[1]))     # [B, d] positive(同 item)
        tau = self.temperature
        loss = 0.0
        for anchor, positive in [(a, b), (b, a)]:
            pos = (anchor * positive).sum(1) / tau                       # [B] 正例相似度(同 item 跨类型)
            neg = (anchor @ anchor.t()) / tau                            # [B, B] 同类型其他物品
            B = anchor.size(0)
            mask = torch.eye(B, device=anchor.device, dtype=torch.bool)
            neg = neg.masked_fill(mask, -1e9)
            logits = torch.cat([pos.unsqueeze(1), neg], dim=1)           # [B, 1+B]
            labels = torch.zeros(B, dtype=torch.long, device=anchor.device)
            loss += F.cross_entropy(logits, labels)
        return loss / 2.0

    # 注: 原 conf_reg() 方法已移除. 置信度判别正则改在 model.py 的 bpr_loss 中
    # 用缓存的 conf_vec 内联实现(避免对 fuse() 的二次调用, 见 model.py 注释).
