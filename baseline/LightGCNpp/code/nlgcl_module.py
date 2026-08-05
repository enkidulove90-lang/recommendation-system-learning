"""
NLGCL-H: Naturally Existing Neighbor Layers Graph Contrastive Learning
Heterogeneous-scope variant (distinguishes user/item nodes).

Extracted from baseline/LightGCNpp/code/model.py (the in-class
`InfoNCE` / `neighbor_cl_loss` methods) into reusable pure functions so
it can be plugged into any LightGCN-style CF backbone -- e.g. the CF
branch of CCDRec.

Key property (NLGCL-H, "heterogeneous"):
  - positive pair is cross-layer AND cross-node:
        user-side:  (e_u^(g),  e_{i+}^(g+1))   i+ in N(u)
        item-side:  (e_i^(g),  e_{u+}^(g+1))   u+ in N(i)
  - negatives are drawn from the same-layer full view (batch-inclusive).
  - No data augmentation needed; views come from adjacent GNN layers.
"""
import torch
import torch.nn.functional as F


def nlgcl_info_nce(v1, v2, view, tau):
    """NLGCL InfoNCE. Uses .sum() (paper convention, not .mean()).

    Args:
        v1:   (N, d) anchor embeddings
        v2:   (N, d) positive embeddings
        view: (M, d) full view used to draw negatives (M >= N)
        tau:  temperature
    Returns:
        scalar loss (summed over the N pairs)
    """
    v1 = F.normalize(v1, dim=1)
    v2 = F.normalize(v2, dim=1)
    view = F.normalize(view, dim=1)
    pos = torch.exp((v1 * v2).sum(1) / tau)
    ttl = torch.exp(v1 @ view.t() / tau).sum(1)
    return -torch.log(pos / ttl).sum()


def nlgcl_neighbor_cl_loss(embs_list, num_users, num_items, users, pos,
                           cl_temp=0.1, cl_alpha=0.6, G=2):
    """NLGCL-H neighbor-layer contrastive loss.

    Args:
        embs_list: list of [N, d] tensors, embs_list[l] = node embeddings at
                   layer l (l = 0..L). N = num_users + num_items, ordered
                   as [users; items] (items are offset by num_users).
        num_users, num_items: node counts (split point of embs_list[l]).
        users: (B,) user indices in [0, num_users).
        pos:   (B,) positive item *local* indices in [0, num_items); the
               absolute item index is num_users + pos.
        cl_temp:    temperature.
        cl_alpha:   weight balancing user-side vs item-side loss.
        G:          number of contrastive view groups (G <= num_layers).
    Returns:
        scalar loss = cl_alpha * cl_u + (1-cl_alpha) * cl_i
    """
    if G < 1:
        return torch.zeros((), device=embs_list[0].device)
    G = min(G, len(embs_list) - 1)  # safety: need layers 0..G

    eu, ei = torch.split(embs_list[0], [num_users, num_items])
    cl_u = cl_i = 0.
    for g in range(G):
        cu, ci = torch.split(embs_list[g + 1], [num_users, num_items])
        # user-side anchor e_u^(g); positive = next-layer neighbor e_{i+}^(g+1)
        cl_u += nlgcl_info_nce(ci[pos], eu[users], eu[users], cl_temp)
        # item-side anchor e_i^(g); positive = next-layer neighbor e_{u+}^(g+1)
        cl_i += nlgcl_info_nce(cu[users], ei[pos], ei[pos], cl_temp)
        eu, ei = cu, ci
    return cl_alpha * cl_u + (1 - cl_alpha) * cl_i


class NLGCLHLoss(torch.nn.Module):
    """Drop-in module wrapping nlgcl_neighbor_cl_loss with hyper-params."""
    def __init__(self, cl_temp=0.1, cl_alpha=0.6, G=2):
        super().__init__()
        self.cl_temp = cl_temp
        self.cl_alpha = cl_alpha
        self.G = G

    def forward(self, embs_list, num_users, num_items, users, pos):
        return nlgcl_neighbor_cl_loss(
            embs_list, num_users, num_items, users, pos,
            self.cl_temp, self.cl_alpha, self.G)


if __name__ == "__main__":
    # quick shape sanity check
    N_u, N_i, d, L = 50, 100, 16, 3
    embs = [torch.randn(N_u + N_i, d) for _ in range(L + 1)]
    users = torch.randint(0, N_u, (32,))
    pos = torch.randint(0, N_i, (32,))
    loss = nlgcl_neighbor_cl_loss(embs, N_u, N_i, users, pos, G=2)
    print("NLGCL-H loss:", float(loss), "finite:", torch.isfinite(loss).item())
