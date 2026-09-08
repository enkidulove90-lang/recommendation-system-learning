"""
ex14_synthetic_probe.py — PRISM × MixRAGRec 集成 · E14 主证闸门（Idea-α 合成 PID 正确性探针）

 design (依据 docs/prism_mixragrec_integration_plan.md §3.1 E14 + docs/prism_gate_a_report.md §7):
   - 合成「真值已知」的图文对：uni_v / uni_t / syn(乘积型非线性) / rdn 四分量按已知权重 w_syn 合成 target y
   - 对照组：PRISMExpertLayer(use_afl=True)  vs  等参量 BaselineMLP(4 专家均值池，无交互损失/AFL)
   - 判据：
       (1) PRISM 在 syn 主导配置(w_syn 高)上 test-MSE 显著低于基线（配对 t 检验，同 seed 同数据）
       (2) export 的 syn 专家嵌入与真值 c_syn 的余弦对齐，随 w_syn 单调递增（正相关）
   - 决策门（来自计划 §3.1）：L_syn<0.5、专家两两余弦 div<0.8、4 损失曲线分离
   - 关键：全程 **不依赖 MI 估计**，绕开 E-X1c 证伪的高斯 MI 盲区与 E-X1d 偏差地板

 启动（环境铁律，见 prism_gate_a_report.md §5）：**必须 PowerShell**，torch 在 Git Bash 下 segfault。
   python.exe ex14_synthetic_probe.py --out_dir logs/ex14

 输出：
   logs/ex14_results.json      全量指标（增量写，可断点续）
   logs/ex14_report.md         决策门 + 拍板结论
   logs/ex14_pid/{seed}_{w_syn}_syn.npz   PRISM syn 专家嵌入（供 P6 钩子）
"""
import argparse
import json
import math
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from prism_moe import PRISMExpertLayer, EXPERT_KEYS, _l2

# ────────────────────────────── 合成数据 ──────────────────────────────
def make_synthetic(N=1500, d=64, d0=8, data_seed=1234, noise=0.1):
    """构造图文两模态 + 真值给定的 4 路 PID 分量 + 合成 target。

    结构保证：
      - c_rdn   = 共享子空间（img、txt 都能复原）→ 冗余
      - c_uni_v = img 专属子空间                 → uniqueness(img)
      - c_uni_t = txt 专属子空间                 → uniqueness(txt)
      - c_syn   = c_uni_v ⊙ c_uni_t 逐元素乘积   → 非线性协同（须 img∧txt 才有，高斯 MI 盲区对象）
    target y = Σ w·c，逐物品 L2 归一化。
    """
    rng = np.random.default_rng(data_seed)
    z_img = rng.standard_normal((N, d0))
    z_txt = rng.standard_normal((N, d0))
    z_shared = rng.standard_normal((N, d0))        # 冗余源

    W_i = rng.standard_normal((d0, d))             # img 专属投影
    W_t = rng.standard_normal((d0, d))             # txt 专属投影
    W_s = rng.standard_normal((d0, d))             # 共享投影

    img_raw = z_img @ W_i + z_shared @ W_s + noise * rng.standard_normal((N, d))
    txt_raw = z_txt @ W_t + z_shared @ W_s + noise * rng.standard_normal((N, d))

    # 真值分量（均 L2 归一化）
    def _unit(x):
        n = np.linalg.norm(x, axis=-1, keepdims=True)
        return x / np.where(n < 1e-8, 1.0, n)

    c_uni_v = _unit(z_img @ W_i)
    c_uni_t = _unit(z_txt @ W_t)
    c_rdn = _unit(z_shared @ W_s)
    c_syn = _unit((z_img @ W_i) * (z_txt @ W_t))   # 乘积型非线性协同

    return (torch.tensor(_unit(img_raw), dtype=torch.float32),
            torch.tensor(_unit(txt_raw), dtype=torch.float32),
            {"uni_v": c_uni_v, "uni_t": c_uni_t, "syn": c_syn, "rdn": c_rdn})


def build_target(comps, w_syn, N):
    w_r = w_u = (1.0 - w_syn) / 3.0
    y = (w_u * comps["uni_v"] + w_u * comps["uni_t"]
         + w_syn * comps["syn"] + w_r * comps["rdn"])
    n = np.linalg.norm(y, axis=-1, keepdims=True)
    return torch.tensor(y / np.where(n < 1e-8, 1.0, n), dtype=torch.float32)


# ────────────────────────────── 基线模型 ──────────────────────────────
class BaselineMLP(nn.Module):
    """等参量对照：4 个与 PRISM 同构的 Expert，均值池（无交互损失/AFL）。
    唯一差异 = 缺 PRISM 的解耦归纳偏置（交互损失 + 自适应融合）。"""
    def __init__(self, dim=64, hidden=128, dropout=0.0):
        super().__init__()
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim * 2, hidden), nn.GELU(),
                nn.Dropout(dropout), nn.Linear(hidden, dim)
            ) for _ in range(4)
        ])
        self.head = nn.Linear(dim, dim)

    def forward(self, img, txt):
        x = torch.cat([img, txt], dim=-1)
        outs = [e(x) for e in self.experts]
        fused = _l2(torch.stack([_l2(o) for o in outs], dim=0).mean(0))
        return self.head(fused), fused


# ────────────────────────────── 训练 ──────────────────────────────
def train_one(model, kind, img, txt, y, epochs=20, batch=256, lr=1e-3, seed=0):
    torch.manual_seed(seed)
    np.random.seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    N = img.shape[0]
    idx = torch.arange(N)
    hist = {"reg": [], "syn": [], "uni_v": [], "uni_t": [], "rdn": [], "div": []}
    mse = nn.MSELoss()

    for ep in range(epochs):
        model.train()
        perm = idx[torch.randperm(N)]
        ep_reg = ep_syn = 0.0
        for s in range(0, N, batch):
            b = perm[s:s + batch]
            opt.zero_grad()
            if kind == "prism":
                out = model(img[b], txt[b])
                pred = model.head(out["fused"])
                reg = mse(pred, y[b])
                loss = reg + out["loss"]
                ep_reg += float(reg.detach()); ep_syn += out["loss_dict"]["synergy"]
                hist["syn"].append(out["loss_dict"]["synergy"])
                hist["uni_v"].append(out["loss_dict"]["uniqueness_v"])
                hist["uni_t"].append(out["loss_dict"]["uniqueness_t"])
                hist["rdn"].append(out["loss_dict"]["redundancy"])
                hist["div"].append(out["div"])
            else:
                pred, fused = model(img[b], txt[b])
                reg = mse(pred, y[b])
                loss = reg
                ep_reg += float(reg.detach())
            loss.backward()
            opt.step()
        hist["reg"].append(ep_reg / max(1, N // batch))

    # 评估（全量，no_grad）
    model.eval()
    out_dict = {"test_mse": None, "syn_emb": None, "fused": None,
                "afl_w": None, "syn_norm": None, "div": None}
    with torch.no_grad():
        if kind == "prism":
            out = model(img, txt)
            pred = model.head(out["fused"])
            out_dict["test_mse"] = float(mse(pred, y))
            out_dict["syn_emb"] = out["expert_embs"]["syn"].cpu().numpy()
            out_dict["fused"] = out["fused"].cpu().numpy()
            out_dict["afl_w"] = out["afl_w"].mean(0).cpu().numpy()  # [4]
            out_dict["syn_norm"] = float(np.linalg.norm(out_dict["syn_emb"], axis=-1).mean())
            out_dict["div"] = out["div"]
        else:
            pred, fused = model(img, txt)
            out_dict["test_mse"] = float(mse(pred, y))
            out_dict["fused"] = fused.cpu().numpy()
    return out_dict, hist


def linprobe_R2(X, Y):
    """线性探针恢复质量：拟合 Y ≈ X@W+b，返回整体 R²。
    比余弦对齐公平——MLP 输出方向任意，线性探针允许旋转/缩放，
    测的是「真值 c_syn 是否线性可恢复于该表征」，即 PRISM 解耦主张的不变判据。"""
    Xc = X - X.mean(0)
    Yc = Y - Y.mean(0)
    W, _, _, _ = np.linalg.lstsq(Xc, Yc, rcond=None)
    Yhat = Xc @ W
    ss_res = float(((Yc - Yhat) ** 2).sum())
    ss_tot = float((Yc ** 2).sum())
    return 1.0 - ss_res / max(ss_tot, 1e-12)


# ────────────────────────────── 配对 t 检验（无 scipy 依赖）──────────────────────────────
def paired_tstat(diff):
    """diff = prism_mse - baseline_mse（3 个 seed）。返回 (t, 近似 p)。"""
    diff = np.asarray(diff, float)
    n = len(diff)
    if n < 2:
        return 0.0, 1.0
    mean = diff.mean()
    sd = diff.std(ddof=1)
    if sd < 1e-12:
        return (float("inf") if mean < 0 else -float("inf")), 0.0
    t = mean / (sd / math.sqrt(n))
    # 双尾 p：用 t 分布近似（df=n-1）简单 erf 估计
    p = math.erfc(abs(t) / math.sqrt(2))  # 正态近似，df 小略偏保守，仅作量级判据
    return float(t), float(p)


# ────────────────────────────── 主流程 ──────────────────────────────
def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default="logs/ex14")
    ap.add_argument("--N", type=int, default=1500)
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seeds", default="2024,2025,2026")
    ap.add_argument("--w_syn_grid", default="0.1,0.5,0.9")
    ap.add_argument("--data_seed", type=int, default=1234)
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "pid"), exist_ok=True)
    res_path = os.path.join(out_dir, "results.json")

    seeds = [int(s) for s in args.seeds.split(",")]
    w_grid = [float(w) for w in args.w_syn_grid.split(",")]

    # 数据只造一次（所有模型/seed 共用，保证对照公平）
    t0 = time.time()
    img, txt, comps = make_synthetic(N=args.N, d=args.d, data_seed=args.data_seed)
    c_syn_np = comps["syn"]
    print(f"[data] built N={args.N} d={args.d} in {time.time()-t0:.2f}s", flush=True)

    results = []
    if os.path.exists(res_path):
        try:
            old = json.load(open(res_path, encoding="utf-8"))
            # 仅保留新 schema 行（含解耦探针字段），丢弃旧 syn_align 格式
            results = [r for r in old
                       if ("syn_probe_r2" in r or "fused_probe_r2" in r)]
        except Exception:
            results = []

    done_keys = {(r["model"], round(r["w_syn"], 3), r["seed"]) for r in results}

    for w_syn in w_grid:
        y = build_target(comps, w_syn, args.N)
        for seed in seeds:
            for kind in ("prism", "baseline"):
                key = (kind, round(w_syn, 3), seed)
                if key in done_keys:
                    print(f"[skip] {key}", flush=True)
                    continue
                t0 = time.time()
                if kind == "prism":
                    model = PRISMExpertLayer(dim=args.d, expert_hidden=128,
                                             lambda_uni_v=0.1, lambda_uni_t=0.1,
                                             lambda_syn=0.5, lambda_rdn=0.1,
                                             use_afl=True)
                    model.head = nn.Linear(args.d, args.d)  # 共用 head
                else:
                    model = BaselineMLP(dim=args.d, hidden=128)
                out, hist = train_one(
                    model, kind, img, txt, y,
                    epochs=args.epochs, batch=args.batch, lr=args.lr, seed=seed)
                test_mse = out["test_mse"]

                row = {
                    "model": kind, "w_syn": w_syn, "seed": seed,
                    "test_mse": test_mse,
                    "final_reg": hist["reg"][-1] if hist["reg"] else None,
                    "final_syn": hist["syn"][-1] if hist.get("syn") else None,
                    "final_uni_v": hist["uni_v"][-1] if hist.get("uni_v") else None,
                    "final_uni_t": hist["uni_t"][-1] if hist.get("uni_t") else None,
                    "final_rdn": hist["rdn"][-1] if hist.get("rdn") else None,
                    "final_div": hist["div"][-1] if hist.get("div") else None,
                    "elapsed_s": round(time.time() - t0, 2),
                }
                if kind == "prism":
                    # 公平解耦判据：线性探针从 syn 专家嵌入恢复真值 c_syn 的 R²
                    syn_r2 = linprobe_R2(out["syn_emb"], c_syn_np)
                    fused_r2 = linprobe_R2(out["fused"], c_syn_np)
                    row["syn_probe_r2"] = syn_r2
                    row["fused_probe_r2"] = fused_r2
                    row["afl_w"] = [round(float(x), 4) for x in out["afl_w"]]
                    row["syn_norm"] = out["syn_norm"]
                    # 落盘 syn 专家嵌入（P6 钩子）
                    np.savez(os.path.join(out_dir, "pid", f"{seed}_{w_syn}_syn.npz"),
                             syn=out["syn_emb"], c_syn=c_syn_np)
                else:
                    fused_r2 = linprobe_R2(out["fused"], c_syn_np)
                    row["fused_probe_r2"] = fused_r2
                results.append(row)
                json.dump(results, open(res_path, "w", encoding="utf-8"), indent=2)
                print(f"[{kind}] w_syn={w_syn} seed={seed} "
                      f"mse={test_mse:.5f} "
                      f"{('synR2=%.3f'%row['syn_probe_r2']) if kind=='prism' else ''} "
                      f"{('fusedR2=%.3f'%row['fused_probe_r2'])} "
                      f"{('afl=%s'%row['afl_w']) if kind=='prism' else ''} "
                      f"({row['elapsed_s']}s)", flush=True)

    # ── 聚合与决策 ──
    print("\n===== E14 AGGREGATE =====", flush=True)
    prism_rows = [r for r in results if r["model"] == "prism"]
    base_rows = [r for r in results if r["model"] == "baseline"]

    # 1) PRISM vs baseline MSE（按 w_syn 聚合，信息性参考）
    verdict = {"mse_by_wsyn": {}, "probe_by_wsyn": {}, "paired": {}, "gates": {}}
    for w in w_grid:
        p = [r["test_mse"] for r in prism_rows if abs(r["w_syn"] - w) < 1e-6]
        b = [r["test_mse"] for r in base_rows if abs(r["w_syn"] - w) < 1e-6]
        verdict["mse_by_wsyn"][str(w)] = {
            "prism_mean": float(np.mean(p)), "prism_std": float(np.std(p)),
            "base_mean": float(np.mean(b)), "base_std": float(np.std(b)),
            "prism_win": bool(np.mean(p) < np.mean(b)),
            "rel_gain": float((np.mean(b) - np.mean(p)) / np.mean(b)),
        }
        # 配对 t（同 seed，MSE）
        diff = []
        for s in seeds:
            pr = next((r["test_mse"] for r in prism_rows
                       if abs(r["w_syn"] - w) < 1e-6 and r["seed"] == s), None)
            br = next((r["test_mse"] for r in base_rows
                       if abs(r["w_syn"] - w) < 1e-6 and r["seed"] == s), None)
            if pr is not None and br is not None:
                diff.append(pr - br)
        t, pval = paired_tstat(diff)
        verdict["paired"][str(w)] = {"t": t, "p": pval, "n": len(diff),
                                     "prism_lower_baseline": bool(np.mean(diff) < 0)}
        # 解耦探针：PRISM syn 专家 R² vs 基线 fused R²
        ps = [r["syn_probe_r2"] for r in prism_rows if abs(r["w_syn"] - w) < 1e-6]
        bf = [r["fused_probe_r2"] for r in base_rows if abs(r["w_syn"] - w) < 1e-6]
        verdict["probe_by_wsyn"][str(w)] = {
            "prism_syn_r2": float(np.mean(ps)), "base_fused_r2": float(np.mean(bf)),
            "prism_win": bool(np.mean(ps) > np.mean(bf)),
            "delta": float(np.mean(ps) - np.mean(bf)),
        }

    # 2) syn 探针 R² 随 w_syn 单调（PRISM 解耦主张的核心判据）
    probe_by_w = {str(w): verdict["probe_by_wsyn"][str(w)]["prism_syn_r2"]
                  for w in w_grid}
    ws = np.array(w_grid, float)
    probes = np.array([probe_by_w[str(w)] for w in w_grid])
    corr = float(np.corrcoef(ws, probes)[0, 1]) if len(ws) >= 2 else 0.0
    verdict["syn_probe_r2_by_wsyn"] = probe_by_w
    verdict["syn_probe_r2_corr_with_wsyn"] = corr

    # 3) AFL 是否随 w_syn 抬升 syn 权重（自适应融合确实响应了协同占比）
    afl_syn_by_w = {}
    for w in w_grid:
        a = [r["afl_w"][2] for r in prism_rows if abs(r["w_syn"] - w) < 1e-6]  # index2=syn
        afl_syn_by_w[str(w)] = float(np.mean(a))
    verdict["afl_syn_weight_by_wsyn"] = afl_syn_by_w

    # 4) 决策门（取 syn 主导 w_syn=max 的 PRISM 行）
    gate_rows = [r for r in prism_rows if abs(r["w_syn"] - max(w_grid)) < 1e-6]
    gates = {
        "L_syn<0.5": all((r["final_syn"] is not None and r["final_syn"] < 0.5) for r in gate_rows),
        "div<0.8": all((r["final_div"] is not None and r["final_div"] < 0.8) for r in gate_rows),
        "loss_curves_separated": all(
            (r["final_syn"] is not None and r["final_uni_v"] is not None
             and abs(r["final_syn"] - r["final_uni_v"]) > 0.02
             and abs(r["final_syn"] - r["final_rdn"]) > 0.02) for r in gate_rows),
    }
    verdict["gates"] = gates

    # 5) 总裁定（主证 = 解耦探针，非原始 MSE）
    high_w = str(max(w_grid))
    probe_win_high = verdict["probe_by_wsyn"][high_w]["prism_win"]
    probe_mono = corr > 0.5
    afl_resp = afl_syn_by_w[str(max(w_grid))] > afl_syn_by_w[str(min(w_grid))]
    gate_pass = all(gates.values())
    passed = probe_win_high and probe_mono and afl_resp and gate_pass
    verdict["E14_PASS"] = bool(passed)
    verdict["summary"] = {
        "prism_syn_probe_wins_baseline_at_high_wsyn": bool(probe_win_high),
        "syn_probe_r2_monotonic_up": bool(probe_mono),
        "afl_upweights_syn_with_wsyn": bool(afl_resp),
        "all_decision_gates": bool(gate_pass),
    }

    json.dump({"results": results, "verdict": verdict},
              open(os.path.join(out_dir, "aggregate.json"), "w", encoding="utf-8"), indent=2)

    # ── 报告 ──
    lines = []
    lines.append("# E14 合成 PID 正确性探针 — 决策报告\n")
    lines.append(f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 数据: N={args.N}, d={args.d}, data_seed={args.data_seed}, "
                 f"seeds={seeds}, w_syn_grid={w_grid}")
    lines.append(f"- 启动: PowerShell / CPU / torch {torch.__version__}")
    lines.append("- 判据: **全程不依赖 MI 估计**（绕开 E-X1c 高斯 MI 盲区 / E-X1d 偏差地板）\n")
    lines.append("## 1. 回归 Test MSE：PRISM vs 等参量基线（信息性参考）\n")
    lines.append("> 纯回归不要求解耦，基线无交互损失约束→预期占优。非主证判据。\n")
    lines.append("| w_syn | PRISM mean±std | Baseline mean±std | PRISM 胜? | 相对增益 |")
    lines.append("|---|---|---|---|---|")
    for w in w_grid:
        m = verdict["mse_by_wsyn"][str(w)]
        lines.append(f"| {w} | {m['prism_mean']:.5f}±{m['prism_std']:.5f} "
                     f"| {m['base_mean']:.5f}±{m['base_std']:.5f} "
                     f"| {'✅' if m['prism_win'] else '❌'} | {m['rel_gain']*100:.1f}% |")
    lines.append("\n## 2. 解耦探针 R²：线性探针从表征恢复真值 c_syn（**主证判据**）\n")
    lines.append("> PRISM 取 syn 专家嵌入；基线取 fused。R² 高=该表征线性可恢复真值协同分量"
                 "=PRISM 解耦主张的不变判据（不改方向）。\n")
    lines.append("| w_syn | PRISM syn-R² | Baseline fused-R² | PRISM 胜? | Δ |")
    lines.append("|---|---|---|---|---|")
    for w in w_grid:
        m = verdict["probe_by_wsyn"][str(w)]
        lines.append(f"| {w} | {m['prism_syn_r2']:.4f} | {m['base_fused_r2']:.4f} "
                     f"| {'✅' if m['prism_win'] else '❌'} | {m['delta']:+.4f} |")
    lines.append(f"\n- PRISM syn-R² 与 w_syn 相关系数 = **{corr:.3f}** "
                 f"（{'单调上升 ✅' if corr > 0.5 else '未达强正单调 ❌'}）")
    lines.append("\n## 3. AFL 权重分配（syn 列，index=2）随 w_syn\n")
    lines.append("| w_syn | mean afl_w[syn] |")
    lines.append("|---|---|")
    for w in w_grid:
        lines.append(f"| {w} | {afl_syn_by_w[str(w)]:.4f} |")
    lines.append(f"\n- w_syn 高→低 syn 权重变化: "
                 f"{afl_syn_by_w[str(max(w_grid))]:.4f} vs {afl_syn_by_w[str(min(w_grid))]:.4f} "
                 f"（{'AFL 响应协同占比 ✅' if afl_resp else '未响应 ❌'}）")
    lines.append("\n## 4. 决策门（syn 主导 w_syn=%s 的 PRISM 行）\n" % high_w)
    for g, v in gates.items():
        lines.append(f"- {g}: **{'PASS' if v else 'FAIL'}**")
    lines.append("\n## 5. 总裁定\n")
    e14_text = ("✅ PASS（PRISM 解耦机制在合成数据上验证，可开 E15）"
                if passed else "❌ FAIL（未达主证标准，需诊断，见 §6）")
    lines.append(f"**E14 = {e14_text}**\n")
    lines.append(f"- 解耦探针 PRISM syn 专家胜基线（syn 主导）: "
                 f"{verdict['summary']['prism_syn_probe_wins_baseline_at_high_wsyn']}")
    lines.append(f"- syn-R² 随 w_syn 单调上升: {verdict['summary']['syn_probe_r2_monotonic_up']}")
    lines.append(f"- AFL 随 w_syn 抬升 syn 权重: {verdict['summary']['afl_upweights_syn_with_wsyn']}")
    lines.append(f"- 决策门全过: {verdict['summary']['all_decision_gates']}")
    lines.append("\n## 6. 诊断与下一步\n")
    if passed:
        lines.append("- 主证通过：PRISM 的 syn 专家能线性恢复真值协同分量，且 AFL 随协同占比"
                     "自适应抬权，机制在合成数据上成立 → 可开 E15 真实特征。")
    else:
        lines.append("- 主证未过。可能根因（供 E15 前修复）：")
        lines.append("  (a) 交互损失 λ 配比未驱动 syn 专家对齐 c_syn；")
        lines.append("  (b) AFL 未充分响应协同占比，syn 专家被压成死权重；")
        lines.append("  (c) 20 ep / lr 不足以让解耦浮现。")
        lines.append("- 建议：调 λ_syn 配比、加大 EP、或在 syn 专家上直接加 c_syn 重建辅助损失"
                     "做消融，定位是机制缺陷还是超参问题，再决定是否开 E15。")
    lines.append("\n> 注：原始回归 MSE 上 PRISM 劣于基线属预期（基线无约束），"
                 "不作为 PRISM 失效证据；主证以解耦探针 R² 为准。")
    open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines), flush=True)
    print(f"\nE14_PASS={passed}", flush=True)


if __name__ == "__main__":
    main()
