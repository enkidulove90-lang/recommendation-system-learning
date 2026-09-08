"""
Created on Mar 1, 2020
Pytorch Implementation of LightGCN in
Xiangnan He et al. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation

@author: Jianbai Ye (gusye@mail.ustc.edu.cn)

Define models here
"""
import world
try:
    import world_gaudi
except ImportError:
    world_gaudi = None
import torch
from dataloader import BasicDataset
from torch import nn
import torch.nn.functional as F
import numpy as np
from mm_align import MultiModalAligner


class BasicModel(nn.Module):    
    def __init__(self):
        super(BasicModel, self).__init__()
    
    def getUsersRating(self, users):
        raise NotImplementedError
    
class PairWiseModel(BasicModel):
    def __init__(self):
        super(PairWiseModel, self).__init__()
    def bpr_loss(self, users, pos, neg):
        """
        Parameters:
            users: users list 
            pos: positive items for corresponding users
            neg: negative items for corresponding users
        Return:
            (log-loss, l2-loss)
        """
        raise NotImplementedError
    
class PureMF(BasicModel):
    def __init__(self, 
                 config:dict, 
                 dataset:BasicDataset):
        super(PureMF, self).__init__()
        self.num_users  = dataset.n_users
        self.num_items  = dataset.m_items
        self.latent_dim = config['latent_dim_rec']
        self.f = nn.Sigmoid()
        self.__init_weight()
        
    def __init_weight(self):
        self.embedding_user = torch.nn.Embedding(
            num_embeddings=self.num_users, embedding_dim=self.latent_dim)
        self.embedding_item = torch.nn.Embedding(
            num_embeddings=self.num_items, embedding_dim=self.latent_dim)
        print("using Normal distribution N(0,1) initialization for PureMF")
        
    def getUsersRating(self, users):
        users = users.long()
        users_emb = self.embedding_user(users)
        items_emb = self.embedding_item.weight
        scores = torch.matmul(users_emb, items_emb.t())
        return self.f(scores)
    
    def computer(self):
        return self.embedding_user.weight, self.embedding_item.weight
    
    def bpr_loss(self, users, pos, neg):
        users_emb = self.embedding_user(users.long())
        pos_emb   = self.embedding_item(pos.long())
        neg_emb   = self.embedding_item(neg.long())
        pos_scores= torch.sum(users_emb*pos_emb, dim=1)
        neg_scores= torch.sum(users_emb*neg_emb, dim=1)
        loss = torch.mean(nn.functional.softplus(neg_scores - pos_scores))
        reg_loss = (1/2)*(users_emb.norm(2).pow(2) + 
                          pos_emb.norm(2).pow(2) + 
                          neg_emb.norm(2).pow(2))/float(len(users))
        return loss, reg_loss
        
    def forward(self, users, items):
        users = users.long()
        items = items.long()
        users_emb = self.embedding_user(users)
        items_emb = self.embedding_item(items)
        scores = torch.sum(users_emb*items_emb, dim=1)
        return self.f(scores)

class LightGCN(BasicModel):
    def __init__(self, 
                 config:dict, 
                 dataset:BasicDataset):
        super(LightGCN, self).__init__()
        self.config = config
        self.dataset : BasicDataset = dataset
        self.__init_weight()

    def __init_weight(self):
        self.num_users  = self.dataset.n_users
        self.num_items  = self.dataset.m_items
        self.latent_dim = self.config['latent_dim_rec']
        self.n_layers = self.config['lightGCN_n_layers']
        self.keep_prob = self.config['keep_prob']
        self.A_split = self.config['A_split']
        self.gamma = self.config['gamma']
        self.embedding_user = torch.nn.Embedding(num_embeddings=self.num_users, embedding_dim=self.latent_dim)
        self.embedding_item = torch.nn.Embedding(num_embeddings=self.num_items, embedding_dim=self.latent_dim)
        
        if self.config['pretrain'] == 0:
            nn.init.normal_(self.embedding_user.weight, std=0.1)
            nn.init.normal_(self.embedding_item.weight, std=0.1)
            world.cprint('use NORMAL distribution initilizer')
        else:
            self.embedding_user.weight.data.copy_(torch.from_numpy(self.config['user_emb']))
            self.embedding_item.weight.data.copy_(torch.from_numpy(self.config['item_emb']))
            print('use pretarined data')
        
        self.f = nn.Sigmoid()
        self.Graph = self.dataset.getSparseGraph()

        # ---- P1: NLGCL (idea4) config ----
        self.use_cl = self.config.get('use_cl', 0)
        self.cl_temp = self.config.get('cl_temp', 0.1)
        self.cl_reg = self.config.get('cl_reg', 5e-5)
        self.cl_alpha = self.config.get('cl_alpha', 0.6)
        self.G = min(self.config.get('G', 2), self.n_layers)

        # ---- idea2: Multi-Modal Alignment (align-then-fuse) ----
        self.use_mm = self.config.get('use_mm', 0)
        self.mm_info = {'conf_mean': 0.0, 'n_types': 0}
        if self.use_mm:
            feats = getattr(self.dataset, 'mm_feats', None)
            assert feats, ("use_mm=1 but dataset has no mm_feats. "
                           "Run prep_amazon_sports.py (synthetic) or fetch_mm_data.py (real MMSSL features).")
            feat_dims = {k: int(v.size(1)) for k, v in feats.items()}
            self.mm_feats = feats
            self.mm_aligner = MultiModalAligner(
                n_items=self.num_items, id_dim=self.latent_dim, feat_dims=feat_dims,
                proj_hidden=self.config.get('mm_proj', 256),
                temperature=self.config.get('mm_temp', 0.1),
                conf_hidden=self.config.get('mm_conf', 64),
                force_c=self.config.get('force_c', 0.0),
            ).to(world.device)
            self.mm_reg = self.config.get('mm_reg', 1e-3)
            self.mm_conf_reg_w = self.config.get('mm_conf_reg', 0.01)
            self.mm_cost_w = self.config.get('cost_reg', 0.0)
            # idea3 预算式成本: 鼓励平均引入率稳定在 cost_target 附近.
            # =0 时为纯征税(原语义); >0 时激活预算式, 避免把已偏低的 conf 压到 0.
            self.cost_target = self.config.get('cost_target', 0.0)
            # ---- E6 全局预算硬约束 ----
            # L_budget = mm_budget_lambda * (mean(c_batch) - mm_budget)^2
            # 与 idea3 cost_reg 的本质区别(勿混用):
            #   cost_reg  : (c_i - t)^2 的**逐物品**均值 -> 强迫每个物品的 c 都等于 t,
            #               会抹平门控判别性, 等价于「软化版 force_c」, 学不到自适应.
            #   mm_budget : (mean(c) - t)^2 只约束**批均值** -> 允许物品间分化
            #               (图文相符者 c 高 / 不符者 c 低), 只把"总引入预算"顶住不塌.
            # 动机: E1(force_c=0.8 -> R@20 0.08798) vs E2(conf_reg=0, c 塌到 0.005 -> 0.0848)
            #       证明 BPR 局部梯度偏好丢弃多模态, 软惩罚(conf_reg)打不过收缩,
            #       须用全局预算把 c 顶在 0.8 附近, 同时保留逐物品自适应.
            #
            # 【固定 lambda 的软惩罚有系统性欠冲, 必须知道】
            # 记 BPR 对 c 的等效下压强度为 A, 则 lambda_b*(c_bar-t)^2 的驻点满足
            #     2*lambda_b*(t - c_bar) = A   =>   c_bar = t - A/(2*lambda_b)
            # 即**永远够不到 t**, 缺口 A/(2*lambda_b). _smoke_e6_budget.py 实测(A=0.5):
            #     lambda=0.5 -> 0.2998 | 1.0 -> 0.5506 | 2.0 -> 0.6750, 与解析解三位小数吻合.
            # 而真实 A 未知 => 只扫固定 lambda 可能得到 "conf_mean<0.6 -> E6 无效" 的**假阴性**.
            # 解法: 增广拉格朗日(mm_budget_dual>0), 用对偶上升自适应乘子把 c_bar 精确顶到 t,
            #       与 A 的大小无关:
            #     L = BPR + nu*(t - c_bar) + lambda_b*(t - c_bar)^2
            #     nu <- clip(nu + eta*(t - c_bar), -nu_max, +nu_max)      # 双侧, 故为等式约束
            self.mm_budget = self.config.get('mm_budget', 0.0)          # c_target
            self.mm_budget_lambda = self.config.get('mm_budget_lambda', 0.0)  # lambda_b (二次项)
            self.mm_budget_dual = self.config.get('mm_budget_dual', 0.0)      # eta, 0=纯二次(软)
            self.mm_budget_dual_max = self.config.get('mm_budget_dual_max', 5.0)
            self._mm_dual = 0.0                                          # nu, 对偶乘子(非参数)
            # ---- 投影缓存刷新频率(E6 阻断级修复) ----
            # project() 的全量缓存原本每 epoch 只刷 1 次, 而预算通过 fuse_subset(带梯度)
            # 每 batch 都在推 proj 头 -> 图传播读到的 c 结构上永远追不上训练路径。
            # 实测 seed2024: 图传播 c≈0.055, 预算路径 batch_c≈0.823, 差 0.77。
            # 后果: 模型实际是在"几乎不融合多模态"的图上训练, E6 等于没生效;
            #       而若只在 eval 前刷新(mm_eval_fresh), 又变成训练/评测错配, R@20 直接崩。
            # 正解: 训练途中periodically 刷新, 让两条路径同步。K=0 关闭(旧行为)。
            # 开销: 全量投影 ~2.5s, 94 batch/epoch, K=32 => 约 +7.5s/epoch(可接受)。
            self.mm_proj_refresh = int(self.config.get('mm_proj_refresh', 0))
            self._mm_batch_cnt = 0
            print(f"[idea2] MultiModalAligner ON: types={list(feat_dims)}, dims={feat_dims}, "
                  f"mm_reg={self.mm_reg}"
                  + (f", idea3 cost_reg={self.mm_cost_w}" if self.mm_cost_w > 0 else "")
                  + (f", E1 force_c={self.config.get('force_c', 0.0)}" if self.config.get('force_c', 0.0) > 0 else "")
                  + (f", E6 budget target={self.mm_budget} lambda={self.mm_budget_lambda}"
                     + (f" dual_eta={self.mm_budget_dual}" if self.mm_budget_dual > 0 else " (fixed-lambda/soft)")
                     if self.mm_budget > 0 else "")
                  + (f", proj_refresh={self.mm_proj_refresh}batch" if self.mm_proj_refresh > 0 else ""))

    def mm_new_epoch(self):
        """每个训练 epoch 开始时调用, 触发对齐器刷新「全量投影缓存」(no_grad).
        缓存只供图传播读取; proj 头的梯度由 contrastive_loss 里的
        project_subset(本 batch pos+neg 物品, 带梯度)每 batch 提供."""
        if getattr(self, 'use_mm', 0):
            self._mm_epoch = getattr(self, '_mm_epoch', 0) + 1
            self.mm_aligner.set_epoch(self._mm_epoch)

    def __dropout_x(self, x, keep_prob):
        size = x.size()
        index = x.indices().t()
        values = x.values()
        random_index = torch.rand(len(values)) + keep_prob
        random_index = random_index.int().bool()
        index = index[random_index]
        values = values[random_index]/keep_prob
        g = torch.sparse.FloatTensor(index.t(), values, size)
        return g
    
    def __dropout(self, keep_prob):
        if self.A_split:
            graph = []
            for g in self.Graph:
                graph.append(self.__dropout_x(g, keep_prob))
        else:
            graph = self.__dropout_x(self.Graph, keep_prob)
        return graph
    
    def computer(self):
        """
        propagate methods for lightGCN
        """       
        users_emb = self.embedding_user.weight
        items_emb = self.embedding_item.weight
        # ---- idea2: 把对齐融合后的视觉表示注入 e^(0)_item ----
        if getattr(self, 'use_mm', 0):
            items_emb, self.mm_info = self.mm_aligner.fuse(
                self.mm_feats, self.embedding_item.weight)
        all_emb = torch.cat([users_emb, items_emb])
        
        embs = [all_emb]
        if self.config['dropout']:
            if self.training:
                print("droping")
                g_droped = self.__dropout(self.keep_prob)
            else:
                g_droped = self.Graph        
        else:
            g_droped = self.Graph    
        
        for layer in range(self.n_layers):
            norm = torch.norm(all_emb, dim=1) + 1e-12
            all_emb = all_emb / norm[:,None]
            
            if self.A_split:
                temp_emb = []
                for f in range(len(g_droped)):
                    temp_emb.append(torch.sparse.mm(g_droped[f], all_emb))
                side_emb = torch.cat(temp_emb, dim=0)
                all_emb = side_emb
            else:
                all_emb = torch.sparse.mm(g_droped, all_emb)
            
            embs.append(all_emb)

        embs_zero = embs[0]
        embs_prop = torch.mean(torch.stack(embs[1:], dim=1), dim=1)

        light_out = (self.gamma * embs_zero) + ((1 - self.gamma) * embs_prop)

        _users, _items = torch.split(torch.stack(embs, dim=1), [self.num_users, self.num_items])
        users, items = torch.split(light_out, [self.num_users, self.num_items])
        
        return users, items, _users, _items

    # ============ P1: NLGCL naturally-contrastive loss (idea4) ============
    def InfoNCE(self, v1, v2, view, tau):
        """NLGCL InfoNCE. NOTE: uses .sum() not .mean() (paper convention);
        cl_reg must be scaled ~batch_size if switched to .mean()."""
        v1 = F.normalize(v1, dim=1)
        v2 = F.normalize(v2, dim=1)
        view = F.normalize(view, dim=1)
        pos = torch.exp((v1 * v2).sum(1) / tau)
        ttl = torch.exp(v1 @ view.t() / tau).sum(1)
        return -torch.log(pos / ttl).sum()

    def neighbor_cl_loss(self, embs_list, users, pos):
        """embs_list[l] = [N, d] = cat(user/item emb at layer l).
        Positive pair: (e_u^(g), e_{i+}^{(g+1)}), i+ in N_u.  (cross-layer + cross-node)"""
        eu, ei = torch.split(embs_list[0], [self.num_users, self.num_items])
        cl_u = cl_i = 0.
        for g in range(self.G):
            cu, ci = torch.split(embs_list[g + 1], [self.num_users, self.num_items])
            cl_u += self.InfoNCE(ci[pos], eu[users], eu[users], self.cl_temp)
            cl_i += self.InfoNCE(cu[users], ei[pos], ei[pos], self.cl_temp)
            eu, ei = cu, ci
        return self.cl_alpha * cl_u + (1 - self.cl_alpha) * cl_i
    
    def getUsersRating(self, users, all_users=None, all_items=None):
        if all_users is None or all_items is None:
            all_users, all_items, _, _ = self.computer()
        users_emb = all_users[users.long()]
        items_emb = all_items
        rating = self.f(torch.matmul(users_emb, items_emb.t()))
        return rating
    
    def getEmbedding(self, users, pos_items, neg_items):
        all_users, all_items, _users, _items = self.computer()
        self._items = _items   # 缓存逐层 item 嵌入, 供 bpr_loss 的 idea2 梯度通路复用
        users_emb = all_users[users]
        pos_emb = all_items[pos_items]
        neg_emb = all_items[neg_items]
        users_emb_ego = self.embedding_user(users)
        pos_emb_ego = self.embedding_item(pos_items)
        neg_emb_ego = self.embedding_item(neg_items)
        # 缓存逐层嵌入供 NLGCL 对比损失复用, 避免 bpr_loss 再调用一次 computer()
        # (原实现在 use_cl 时二次全量图传播+对齐器, 双倍算力).
        if self.use_cl:
            self._cl_embs_list = [torch.cat([_users[:, l, :], _items[:, l, :]], dim=0)
                                  for l in range(self.n_layers + 1)]
        return users_emb, pos_emb, neg_emb, users_emb_ego, pos_emb_ego, neg_emb_ego
    
    def bpr_loss(self, users, pos, neg):
        (users_emb, pos_emb, neg_emb,
         userEmb0,  posEmb0, negEmb0) = self.getEmbedding(users.long(), pos.long(), neg.long())
        reg_loss = (1/2)*(userEmb0.norm(2).pow(2) +
                         posEmb0.norm(2).pow(2)  +
                         negEmb0.norm(2).pow(2))/float(len(users))
        pos_scores = torch.sum(users_emb * pos_emb, dim=1)
        neg_scores = torch.sum(users_emb * neg_emb, dim=1)
        bpr_term = torch.mean(torch.nn.functional.softplus(neg_scores - pos_scores))

        # ---- P1: NLGCL contrastive loss (idea4) ----
        if self.use_cl:
            # 复用 getEmbedding 中缓存的逐层嵌入(不再二次调用 computer())
            embs_list = getattr(self, '_cl_embs_list', None)
            if embs_list is None:
                all_users, all_items, _users, _items = self.computer()
                embs_list = [torch.cat([_users[:, l, :], _items[:, l, :]], dim=0)
                             for l in range(self.n_layers + 1)]
            cl = self.neighbor_cl_loss(embs_list, users.long(), pos.long())
            bpr_term = bpr_term + self.cl_reg * cl

        # ---- idea2/idea3: 多模态对齐(梯度通路 v3) ----
        if getattr(self, 'use_mm', 0):
            cat_pn = torch.cat([pos.long(), neg.long()])
            idx, inverse = cat_pn.unique(return_inverse=True)
            # 带梯度融合 e^(0)_item(仅 batch 子集), BPR 梯度经此回到 proj 头;
            # 投影结果同时缓存给下方 InfoNCE 复用.
            fused_idx, c_idx = self.mm_aligner.fuse_subset(
                self.mm_feats, self.embedding_item.weight, idx)
            c = None
            if fused_idx is not None:
                pos_map = inverse[: pos.shape[0]]
                neg_map = inverse[pos.shape[0]:]
                fused_pos = fused_idx[pos_map]
                fused_neg = fused_idx[neg_map]
                c_pos = c_idx[pos_map]
                c_neg = c_idx[neg_map]
                # light_out 的 gamma·embs_zero 项替换为带梯度融合结果,
                # (1-gamma)·embs_prop 仍取 computer() 的无梯度传播项(无需 proj 梯度).
                ep_pos = self._items[pos.long(), 1:, :].mean(dim=1)
                ep_neg = self._items[neg.long(), 1:, :].mean(dim=1)
                pos_emb2 = self.gamma * fused_pos + (1 - self.gamma) * ep_pos
                neg_emb2 = self.gamma * fused_neg + (1 - self.gamma) * ep_neg
                pos_scores2 = torch.sum(users_emb * pos_emb2, dim=1)
                neg_scores2 = torch.sum(users_emb * neg_emb2, dim=1)
                bpr_term = torch.mean(torch.nn.functional.softplus(neg_scores2 - pos_scores2))
                c = torch.cat([c_pos, c_neg], dim=0).squeeze(-1)

            # 视图一致性 InfoNCE(复用 fuse_subset 缓存的子集投影, 无二次开销)
            cl_mm = self.mm_aligner.contrastive_loss(idx)
            bpr_term = bpr_term + self.mm_reg * cl_mm

            if c is None:
                c_vec = self.mm_info.get('conf_vec', None)
                if c_vec is not None:
                    c = c_vec[idx].squeeze(-1)
            if c is not None:
                # idea2 置信度判别正则(消除死代码 conf_reg): 鼓励 c 有区分度(远离全0/全1极端)
                if self.mm_conf_reg_w > 0:
                    bpr_term = bpr_term + self.mm_conf_reg_w * (1.0 - torch.abs(2.0 * c - 1.0)).mean()
                # idea3 成本感知: cost_target==0 纯征税; >0 预算式
                if self.mm_cost_w > 0:
                    if self.cost_target > 0:
                        cost_loss = self.mm_cost_w * (c - self.cost_target).pow(2).mean()
                    else:
                        cost_loss = self.mm_cost_w * c.mean()
                    bpr_term = bpr_term + cost_loss
                # ---- E6 全局预算约束(增广拉格朗日) ----
                #   L = BPR + nu*(t - c_bar) + lambda_b*(t - c_bar)^2
                # 作用在 c.mean() 而非逐物品 -> 只顶住总预算, 不抹平物品间分化(与 cost_reg 的分水岭).
                # nu 由对偶上升自适应, 可抵消未知强度的 BPR 下压, 消除固定 lambda 的欠冲.
                # (若 force_c>0, c 已 detach 为常数, 该项梯度为 0, 自动失效.)
                if self.mm_budget > 0 and (self.mm_budget_lambda > 0 or self.mm_budget_dual > 0):
                    c_bar = c.mean()
                    gap = self.mm_budget - c_bar          # >0 表示 c 偏低, 需要往上顶
                    budget_loss = c_bar.new_zeros(())
                    if self.mm_budget_lambda > 0:
                        budget_loss = budget_loss + self.mm_budget_lambda * gap.pow(2)
                    if self.mm_budget_dual > 0:
                        # 乘子项(nu 视作常数, 不回传); dL/dc_bar = -nu -> nu>0 时把 c 往上推
                        budget_loss = budget_loss + self._mm_dual * gap
                        # 对偶上升: 双侧 clip => 等式约束 c_bar = t(低档 0.2 也能压下去)
                        nu = self._mm_dual + self.mm_budget_dual * float(gap.detach())
                        self._mm_dual = max(-self.mm_budget_dual_max,
                                            min(self.mm_budget_dual_max, nu))
                    bpr_term = bpr_term + budget_loss
                    self._mm_batch_c_mean = float(c_bar.detach())
                    self._mm_budget_loss = float(budget_loss.detach())

            # ---- 周期性同步全量投影缓存 ----
            # 必须放在 idea2 块内、每个 batch 都走到的位置(不能只在有预算时刷,
            # 否则 E1/E2 的对照跑行为会不一致)。用计数器而非 epoch 判断。
            if self.mm_proj_refresh > 0 and self.training:
                self._mm_batch_cnt += 1
                if self._mm_batch_cnt % self.mm_proj_refresh == 0:
                    self.mm_aligner.refresh_proj(self.mm_feats)

        loss = bpr_term
        return loss, reg_loss
       
    def forward(self, users, items):
        # compute embedding
        all_users, all_items, _, _ = self.computer()
        users_emb = all_users[users]
        items_emb = all_items[items]
        inner_pro = torch.mul(users_emb, items_emb)
        gamma     = torch.sum(inner_pro, dim=1)
        return gamma

class LightGCNGaudi(LightGCN):
    def __init__(self, 
                 config:dict, 
                 dataset:BasicDataset):
        super(LightGCNGaudi, self).__init__(config, dataset)
        self.Graph_dense = self.Graph.to_dense().to(world_gaudi.device)
            
    def __dropout_x(self, x, keep_prob):
        size = x.size()
        index = x.indices().t()
        values = x.values()
        random_index = torch.rand(len(values)) + keep_prob
        random_index = random_index.int().bool()
        index = index[random_index]
        values = values[random_index]/keep_prob
        g = torch.sparse.FloatTensor(index.t(), values, size)
        return g
    
    def __dropout(self, keep_prob):
        if self.A_split:
            graph = []
            for g in self.Graph:
                graph.append(self.__dropout_x(g, keep_prob))
        else:
            graph = self.__dropout_x(self.Graph, keep_prob)
        return graph    
    
    def computer(self):
        """
        propagate methods for lightGCN
        """
        users_emb = self.embedding_user.weight
        items_emb = self.embedding_item.weight
        all_emb = torch.cat([users_emb, items_emb])
        
        embs = [all_emb]
        if self.config['dropout']:
            if self.training:
                print("droping")
                g_droped = self.__dropout(self.keep_prob)
            else:
                g_droped = self.Graph_dense
        else:
            g_droped = self.Graph_dense        
        
        for layer in range(self.n_layers):
            norm = torch.norm(all_emb, dim=1) + 1e-12
            all_emb = all_emb / norm[:,None]
            
            if self.A_split:
                temp_emb = []
                for f in range(len(g_droped)):
                    # temp_emb.append(torch.sparse.mm(g_droped[f], all_emb))
                    # Gaudi does not support sparse for now, use dense mm instead
                    temp_emb.append(torch.mm(g_droped[f], all_emb))
                side_emb = torch.cat(temp_emb, dim=0)
                all_emb = side_emb
            else:
                # all_emb = torch.sparse.mm(g_droped, all_emb)
                # Gaudi does not support sparse for now, use dense mm instead
                all_emb = torch.mm(g_droped, all_emb)
            embs.append(all_emb)

        embs_zero = embs[0]
        embs_prop = torch.mean(torch.stack(embs[1:], dim=1), dim=1)

        light_out = (self.gamma * embs_zero) + ((1 - self.gamma) * embs_prop)

        _users, _items = torch.split(torch.stack(embs, dim=1), [self.num_users, self.num_items])
        users, items = torch.split(light_out, [self.num_users, self.num_items])
        
        return users, items, _users, _items
    
    def getEmbedding(self, users, pos_items, neg_items):
        all_users, all_items, _, _ = self.computer()        
        users_emb = all_users[users]
        pos_emb = all_items[pos_items]
        neg_emb = all_items[neg_items]        
        users_emb_ego = self.embedding_user(users)
        pos_emb_ego = self.embedding_item(pos_items)
        neg_emb_ego = self.embedding_item(neg_items)
        return users_emb, pos_emb, neg_emb, users_emb_ego, pos_emb_ego, neg_emb_ego
    
    def bpr_loss(self, users, pos, neg):
        device = self.embedding_item.weight.device
        users = users.long().to(device)
        pos = pos.long().to(device)
        neg = neg.long().to(device)
        
        (users_emb, pos_emb, neg_emb, 
        userEmb0,  posEmb0, negEmb0) = self.getEmbedding(users, pos, neg)
        reg_loss = (1/2)*(userEmb0.norm(2).pow(2) + 
                         posEmb0.norm(2).pow(2)  +
                         negEmb0.norm(2).pow(2))/float(len(users))
        pos_scores = torch.mul(users_emb, pos_emb)
        pos_scores = torch.sum(pos_scores, dim=1)
        neg_scores = torch.mul(users_emb, neg_emb)
        neg_scores = torch.sum(neg_scores, dim=1)
        
        loss = torch.mean(torch.nn.functional.softplus(neg_scores - pos_scores))
        
        return loss, reg_loss
       
    def forward(self, users, items):
        # compute embedding
        all_users, all_items, _, _ = self.computer()
        users_emb = all_users[users]
        items_emb = all_items[items]
        inner_pro = torch.mul(users_emb, items_emb)
        gamma     = torch.sum(inner_pro, dim=1)
        return gamma
