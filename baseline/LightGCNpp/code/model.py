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
            ).to(world.device)
            self.mm_reg = self.config.get('mm_reg', 1e-3)
            self.mm_conf_reg_w = self.config.get('mm_conf_reg', 0.01)
            self.mm_cost_w = self.config.get('cost_reg', 0.0)
            # idea3 预算式成本: 鼓励平均引入率稳定在 cost_target 附近.
            # =0 时为纯征税(原语义); >0 时激活预算式, 避免把已偏低的 conf 压到 0.
            self.cost_target = self.config.get('cost_target', 0.0)
            print(f"[idea2] MultiModalAligner ON: types={list(feat_dims)}, dims={feat_dims}, "
                  f"mm_reg={self.mm_reg}"
                  + (f", idea3 cost_reg={self.mm_cost_w}" if self.mm_cost_w > 0 else ""))

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
        pos_scores = torch.mul(users_emb, pos_emb)
        pos_scores = torch.sum(pos_scores, dim=1)
        neg_scores = torch.mul(users_emb, neg_emb)
        neg_scores = torch.sum(neg_scores, dim=1)

        loss = torch.mean(torch.nn.functional.softplus(neg_scores - pos_scores))

        # ---- P1: NLGCL contrastive loss (idea4) ----
        if self.use_cl:
            # 复用 getEmbedding 中缓存的逐层嵌入(不再二次调用 computer())
            embs_list = getattr(self, '_cl_embs_list', None)
            if embs_list is None:
                all_users, all_items, _users, _items = self.computer()
                embs_list = [torch.cat([_users[:, l, :], _items[:, l, :]], dim=0)
                             for l in range(self.n_layers + 1)]
            cl = self.neighbor_cl_loss(embs_list, users.long(), pos.long())
            loss = loss + self.cl_reg * cl

        # ---- idea2: 多模态对齐对比损失(视图一致性) ----
        # ---- idea2/idea3: 置信度判别正则 + 成本感知门控(挂 G3 置信度门控) ----
        if getattr(self, 'use_mm', 0):
            # 本 batch 参与计算的物品(正+负). 传 feats 让对齐器对这批物品
            # **重新做带梯度投影** —— 这是 proj 头唯一的梯度来源:
            # 全量投影已改为 no_grad 缓存(避免 94 batch × 2502ms 的不可接受开销),
            # 只有这里的 batch 子集(约 2048 物品, 约 280ms)带梯度.
            idx = torch.cat([pos.long(), neg.long()]).unique()
            cl_mm = self.mm_aligner.contrastive_loss(idx, feats=self.mm_feats)
            loss = loss + self.mm_reg * cl_mm

            c_vec = self.mm_info.get('conf_vec', None)
            if c_vec is not None:
                c = c_vec[idx].squeeze(-1)                    # [B] 本 batch 物品的知识引入权重

                # idea2 置信度判别正则(消除死代码 conf_reg): 鼓励 c 有区分度
                # (远离全 0 / 全 1 极端). 实测 conf_mean=0.088 过低, 多模态信号被门控掐断,
                # 该项把 c 往 0.5 拉, 让更多图文知识真正进入 e^(0)_item.
                if self.mm_conf_reg_w > 0:
                    loss = loss + self.mm_conf_reg_w * (1.0 - torch.abs(2.0 * c - 1.0)).mean()

                # idea3 成本感知:
                #  - cost_target == 0 -> 纯征税(原语义): 引入知识有代价, 过高则退化为纯 ID.
                #  - cost_target  > 0 -> 预算式: 鼓励平均引入率稳定在目标值附近,
                #    既不过度压低(避免 idea3 退化为 baseline), 也不过度放开.
                #    这是针对"纯征税在 conf 已偏低时自相矛盾"缺陷的重构.
                if self.mm_cost_w > 0:
                    if self.cost_target > 0:
                        cost_loss = self.mm_cost_w * (c - self.cost_target).pow(2).mean()
                    else:
                        cost_loss = self.mm_cost_w * c.mean()
                    loss = loss + cost_loss

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
