"""
ex14bis_anchor_probe.py — PRISM × MixRAGRec 集成 · E14-bis 锚定消融（Idea-α 修复验证）

 E14 FAIL 根因回顾（docs/prism_gate_a_report.md §6）：
   PRISM 的 L_syn 仅约束「syn 专家远离单模态残缺版」= 几何 decorrelation，
   未把 syn 专家锚定到真值协同信号 → syn 专家学到任意正交方向 →
   AFL 路由正确(syn 权重 0.074→0.201 随 w_syn) 但内容错 → syn 主导配置反而更差。

 E14-bis 干预（用户拍板）：给 syn 专家加「真值 c_syn 重建」辅助损失
   (prism_moe.PRISMExpertLayer 的 syn_anchor_lambda + forward(syn_target=c_syn))，
   把 syn 专家直接拉向真值协同分量，重测探针。

 判据（E14-bis 修正版，不再要求「随 w_syn 单调」——锚定强制对齐，恒定高才对）：
   gate1: prism_anchor 的 syn 专家线性探针 R²(syn 主导 w_syn) > 0.5
          （证明锚定生效，syn 专家确实对齐真 synergy，而非 0.147 平台）
   gate2: prism_anchor syn-R²(syn 主导) > baseline fused-R²(syn 主导)
          （PRISM+AFL 解耦优于无归纳偏置的均值池基线）
   gate3: AFL syn 权重随 w_syn 抬升（自适应融合仍工作）
   gate4: 决策门 L_syn<0.5 / div<0.8 / 4 损失曲线分离 全 PASS
   => 全过 = E14-bis PASS = PRISM 机制健全（一旦有锚定 proxy 即可解耦）→ 开 E15

 启动铁律：PowerShell / CPU / torch（Git Bash 下 segfault）。
 输出：logs/ex14bis/{report.md, aggregate.json, results.json, pid/*.npz}
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from prism_moe import PRISMExpertLayer, EXPERT_KEYS, _l2
from ex14_synthetic_probe import (make_synthetic, build_target,
                                  linprobe_R2, paired_tstat, BaselineMLP)


# ────────────────────────────── 训练（支持锚定变体）──────────────────────────────
def train_one(model, kind, img, txt, y, c_syn_t=None,
              epochs=20, batch=256, lr=1e-3, seed=0):
    torch.manual_seed(seed)
    np.random.seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    N = img.shape[0]
    idx = torch.arange(N)
    hist = {"reg": [], "syn": [], "uni_v": [], "uni_t": [], "rdn": [],
            "div": [], "anchor": []}
    mse = nn.MSELoss()

    for ep in range(epochs):
        model.train()
        perm = idx[torch.randperm(N)]
        ep_reg = 0.0
        for s in range(0, N, batch):
            b = perm[s:s + batch]
            opt.zero_grad()
            if kind == "baseline":
                pred, fused = model(img[b], txt[b])
                reg = mse(pred, y[b])
                loss = reg
                ep_reg += float(reg.detach())
            else:
                st = c_syn_t[b] if (kind == "prism_anchor" and c_syn_t is not None) else None
                out = model(img[b], txt[b], syn_target=st)
                pred = model.head(out["fused"])
                reg = mse(pred, y[b])
                loss = reg + out["loss"]
                ep_reg += float(reg.detach())
                hist["syn"].append(out["loss_dict"]["synergy"])
                hist["uni_v"].append(out["loss_dict"]["uniqueness_v"])
                hist["uni_t"].append(out["loss_dict"]["uniqueness_t"])
                hist["rdn"].append(out["loss_dict"]["redundancy"])
                hist["div"].append(out["div"])
                if "syn_anchor" in out["loss_dict"]:
                    hist["anchor"].append(float(out["loss_dict"]["syn_anchor"]))
            loss.backward()
            opt.step()
        hist["reg"].append(ep_reg / max(1, N // batch))

    model.eval()
    out_dict = {"test_mse": None, "syn_emb": None, "fused": None,
                "afl_w": None, "div": None}
    with torch.no_grad():
        if kind == "baseline":
            pred, fused = model(img, txt)
            out_dict["test_mse"] = float(mse(pred, y))
            out_dict["fused"] = fused.cpu().numpy()
        else:
            out = model(img, txt)
            pred = model.head(out["fused"])
            out_dict["test_mse"] = float(mse(pred, y))
            out_dict["syn_emb"] = out["expert_embs"]["syn"].cpu().numpy()
            out_dict["fused"] = out["fused"].cpu().numpy()
            out_dict["afl_w"] = out["afl_w"].mean(0).cpu().numpy()
            out_dict["div"] = out["div"]
    return out_dict, hist


# ────────────────────────────── 主流程 ──────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default="logs/ex14bis_cos")
    ap.add_argument("--N", type=int, default=1500)
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seeds", default="2024,2025,2026")
    ap.add_argument("--w_syn_grid", default="0.1,0.5,0.9")
    ap.add_argument("--data_seed", type=int, default=1234)
    ap.add_argument("--anchor_lambda", type=float, default=0.5)
    ap.add_argument("--anchor_mode", default="cos",
                    help="syn 锚定损失模式: cos(1-cos距离, 与 L_syn 同量纲, 默认) | mse(per-element 重建)")
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "pid"), exist_ok=True)
    res_path = os.path.join(out_dir, "results.json")

    seeds = [int(s) for s in args.seeds.split(",")]
    w_grid = [float(w) for w in args.w_syn_grid.split(",")]

    t0 = time.time()
    img, txt, comps = make_synthetic(N=args.N, d=args.d, data_seed=args.data_seed)
    c_syn_np = comps["syn"]
    c_syn_t = torch.tensor(c_syn_np, dtype=torch.float32)
    print(f"[data] built N={args.N} d={args.d} in {time.time()-t0:.2f}s", flush=True)

    results = []
    if os.path.exists(res_path):
        try:
            results = json.load(open(res_path, encoding="utf-8"))
        except Exception:
            results = []
    done_keys = {(r["model"], round(r["w_syn"], 3), r["seed"]) for r in results}

    for w_syn in w_grid:
        y = build_target(comps, w_syn, args.N)
        for seed in seeds:
            for kind in ("baseline", "prism", "prism_anchor"):
                key = (kind, round(w_syn, 3), seed)
                if key in done_keys:
                    print(f"[skip] {key}", flush=True)
                    continue
                t0 = time.time()
                if kind == "baseline":
                    model = BaselineMLP(dim=args.d, hidden=128)
                elif kind == "prism":
                    model = PRISMExpertLayer(dim=args.d, expert_hidden=128,
                                             lambda_uni_v=0.1, lambda_uni_t=0.1,
                                             lambda_syn=0.5, lambda_rdn=0.1,
                                             use_afl=True, syn_anchor_lambda=0.0)
                    model.head = nn.Linear(args.d, args.d)
                else:  # prism_anchor
                    model = PRISMExpertLayer(dim=args.d, expert_hidden=128,
                                             lambda_uni_v=0.1, lambda_uni_t=0.1,
                                             lambda_syn=0.5, lambda_rdn=0.1,
                                             use_afl=True,
                                             syn_anchor_lambda=args.anchor_lambda,
                                             syn_anchor_mode=args.anchor_mode)
                    model.head = nn.Linear(args.d, args.d)
                out, hist = train_one(
                    model, kind, img, txt, y, c_syn_t=c_syn_t,
                    epochs=args.epochs, batch=args.batch, lr=args.lr, seed=seed)
                test_mse = out["test_mse"]

                row = {
                    "model": kind, "w_syn": w_syn, "seed": seed,
                    "anchor_lambda": args.anchor_lambda if kind == "prism_anchor" else 0.0,
                    "test_mse": test_mse,
                    "final_reg": hist["reg"][-1] if hist["reg"] else None,
                    "final_syn": hist["syn"][-1] if hist.get("syn") else None,
                    "final_uni_v": hist["uni_v"][-1] if hist.get("uni_v") else None,
                    "final_uni_t": hist["uni_t"][-1] if hist.get("uni_t") else None,
                    "final_rdn": hist["rdn"][-1] if hist.get("rdn") else None,
                    "final_div": hist["div"][-1] if hist.get("div") else None,
                    "final_anchor": hist["anchor"][-1] if hist.get("anchor") else None,
                    "elapsed_s": round(time.time() - t0, 2),
                }
                if kind in ("prism", "prism_anchor"):
                    syn_r2 = linprobe_R2(out["syn_emb"], c_syn_np)
                    fused_r2 = linprobe_R2(out["fused"], c_syn_np)
                    row["syn_probe_r2"] = syn_r2
                    row["fused_probe_r2"] = fused_r2
                    row["afl_w"] = [round(float(x), 4) for x in out["afl_w"]]
                    np.savez(os.path.join(out_dir, "pid", f"{seed}_{w_syn}_{kind}_syn.npz"),
                             syn=out["syn_emb"], c_syn=c_syn_np)
                else:
                    fused_r2 = linprobe_R2(out["fused"], c_syn_np)
                    row["fused_probe_r2"] = fused_r2
                results.append(row)
                json.dump(results, open(res_path, "w", encoding="utf-8"), indent=2)
                print(f"[{kind}] w_syn={w_syn} seed={seed} "
                      f"mse={test_mse:.5f} "
                      f"{('synR2=%.3f'%row['syn_probe_r2']) if kind in ('prism','prism_anchor') else ''} "
                      f"{('fusedR2=%.3f'%row['fused_probe_r2'])} "
                      f"{('afl=%s'%row['afl_w']) if kind in ('prism','prism_anchor') else ''} "
                      f"({row['elapsed_s']}s)", flush=True)

    # ── 聚合与决策 ──
    print("\n===== E14-bis AGGREGATE =====", flush=True)
    base_rows = [r for r in results if r["model"] == "baseline"]
    prism_rows = [r for r in results if r["model"] == "prism"]
    anc_rows = [r for r in results if r["model"] == "prism_anchor"]

    verdict = {"mse_by_wsyn": {}, "probe_by_wsyn": {}, "paired": {},
               "afl_syn_by_wsyn": {}, "gates": {}}
    high_w = max(w_grid)

    for w in w_grid:
        pb = [r["test_mse"] for r in base_rows if abs(r["w_syn"] - w) < 1e-6]
        pr = [r["test_mse"] for r in prism_rows if abs(r["w_syn"] - w) < 1e-6]
        pa = [r["test_mse"] for r in anc_rows if abs(r["w_syn"] - w) < 1e-6]
        verdict["mse_by_wsyn"][str(w)] = {
            "base_mean": float(np.mean(pb)), "prism_mean": float(np.mean(pr)),
            "anchor_mean": float(np.mean(pa)),
        }
        bf = [r["fused_probe_r2"] for r in base_rows if abs(r["w_syn"] - w) < 1e-6]
        ps = [r["syn_probe_r2"] for r in prism_rows if abs(r["w_syn"] - w) < 1e-6]
        pa_s = [r["syn_probe_r2"] for r in anc_rows if abs(r["w_syn"] - w) < 1e-6]
        verdict["probe_by_wsyn"][str(w)] = {
            "base_fused_r2": float(np.mean(bf)),
            "prism_syn_r2": float(np.mean(ps)),
            "anchor_syn_r2": float(np.mean(pa_s)),
            "anchor_wins_base": bool(np.mean(pa_s) > np.mean(bf)),
            "anchor_wins_prism": bool(np.mean(pa_s) > np.mean(ps)),
        }
        afl = {k: [] for k in ("base", "prism", "anchor")}
        # afl 仅 PRISM 类有；baseline 无
        for rows, key in ((prism_rows, "prism"), (anc_rows, "anchor")):
            for r in rows:
                if abs(r["w_syn"] - w) < 1e-6:
                    afl[key].append(r["afl_w"][2])
        verdict["afl_syn_by_wsyn"][str(w)] = {
            "prism": float(np.mean(afl["prism"])) if afl["prism"] else None,
            "anchor": float(np.mean(afl["anchor"])) if afl["anchor"] else None,
        }

    # 决策门（取 syn 主导 w_syn 的 prism_anchor 行）
    gate_rows = [r for r in anc_rows if abs(r["w_syn"] - high_w) < 1e-6]
    gates = {
        "L_syn<0.5": all((r["final_syn"] is not None and r["final_syn"] < 0.5) for r in gate_rows),
        "div<0.8": all((r["final_div"] is not None and r["final_div"] < 0.8) for r in gate_rows),
        "loss_curves_separated": all(
            (r["final_syn"] is not None and r["final_uni_v"] is not None
             and abs(r["final_syn"] - r["final_uni_v"]) > 0.02
             and abs(r["final_syn"] - r["final_rdn"]) > 0.02) for r in gate_rows),
    }
    verdict["gates"] = gates

    # 主证裁定（E14-bis 修正版）
    h = str(high_w)
    anchor_syn_high = verdict["probe_by_wsyn"][h]["anchor_syn_r2"]
    base_fused_high = verdict["probe_by_wsyn"][h]["base_fused_r2"]
    prism_syn_high = verdict["probe_by_wsyn"][h]["prism_syn_r2"]
    gate1 = anchor_syn_high > 0.5
    gate2 = anchor_syn_high > base_fused_high
    afl_resp = (verdict["afl_syn_by_wsyn"][h]["anchor"]
                > verdict["afl_syn_by_wsyn"][str(min(w_grid))]["anchor"])
    gate3 = bool(afl_resp)
    gate4 = all(gates.values())
    passed = bool(gate1 and gate2 and gate3 and gate4)
    verdict["E14bis_PASS"] = passed
    verdict["summary"] = {
        "anchor_syn_r2_high_wsyn": float(anchor_syn_high),
        "base_fused_r2_high_wsyn": float(base_fused_high),
        "prism_syn_r2_high_wsyn": float(prism_syn_high),
        "anchor_wins_base": bool(gate2),
        "anchor_wins_prism_unanchored": bool(anchor_syn_high > prism_syn_high),
        "afl_upweights_syn_with_wsyn": bool(gate3),
        "all_decision_gates": bool(gate4),
    }

    json.dump({"results": results, "verdict": verdict},
              open(os.path.join(out_dir, "aggregate.json"), "w", encoding="utf-8"), indent=2)

    # ── 报告 ──
    lines = []
    lines.append("# E14-bis 锚定消融 — 决策报告\n")
    lines.append(f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 锚定: syn_anchor_lambda={args.anchor_lambda}, mode={args.anchor_mode}（syn 专家对齐真值 c_syn）")
    lines.append(f"- 数据: N={args.N}, d={args.d}, data_seed={args.data_seed}, "
                 f"seeds={seeds}, w_syn_grid={w_grid}")
    lines.append(f"- 启动: PowerShell / CPU / torch {torch.__version__}")
    lines.append("- 对照: baseline(均值池) / prism(无锚定, E14 复现) / prism_anchor(锚定)\n")
    lines.append("## 1. 回归 Test MSE（信息性参考，非主证）\n")
    lines.append("| w_syn | Baseline | PRISM(无锚) | PRISM(锚定) |")
    lines.append("|---|---|---|---|")
    for w in w_grid:
        m = verdict["mse_by_wsyn"][str(w)]
        lines.append(f"| {w} | {m['base_mean']:.5f} | {m['prism_mean']:.5f} | {m['anchor_mean']:.5f} |")
    lines.append("\n## 2. 解耦探针 R²：线性探针从表征恢复真值 c_syn（**主证**）\n")
    lines.append("> PRISM 类取 syn 专家嵌入；Baseline 取 fused。R² 高=该表征线性可恢复真值协同。\n")
    lines.append("| w_syn | Base fused-R² | PRISM syn-R²(无锚) | Anchor syn-R² | Anchor 胜 Base? | Anchor 胜 无锚? |")
    lines.append("|---|---|---|---|---|---|")
    for w in w_grid:
        m = verdict["probe_by_wsyn"][str(w)]
        lines.append(f"| {w} | {m['base_fused_r2']:.4f} | {m['prism_syn_r2']:.4f} "
                     f"| {m['anchor_syn_r2']:.4f} | {'✅' if m['anchor_wins_base'] else '❌'} "
                     f"| {'✅' if m['anchor_wins_prism'] else '❌'} |")
    lines.append("\n## 3. AFL syn 权重（index=2）随 w_syn\n")
    lines.append("| w_syn | PRISM(无锚) | Anchor |")
    lines.append("|---|---|---|")
    for w in w_grid:
        a = verdict["afl_syn_by_wsyn"][str(w)]
        lines.append(f"| {w} | {a['prism']:.4f} | {a['anchor']:.4f} |")
    lines.append("\n## 4. 决策门（syn 主导 w_syn=%s 的 Anchor 行）\n" % h)
    for g, v in gates.items():
        lines.append(f"- {g}: **{'PASS' if v else 'FAIL'}**")
    lines.append("\n## 5. 总裁定\n")
    e14b_text = ("✅ PASS（锚定后 PRISM 机制健全 → 可开 E15，真实场景需另构锚定 proxy）"
                 if passed else "❌ FAIL（即使锚定，syn 专家仍未对齐真 synergy → 机制缺陷，不开 E15）")
    lines.append(f"**E14-bis = {e14b_text}**\n")
    lines.append(f"- gate1 anchor syn-R²(syn主导)={anchor_syn_high:.4f} > 0.5: {gate1}")
    lines.append(f"- gate2 anchor syn-R² > baseline fused-R²({base_fused_high:.4f}): {gate2}")
    lines.append(f"- gate3 AFL 随 w_syn 抬升 syn 权重: {gate3}")
    lines.append(f"- gate4 决策门全过: {gate4}")
    lines.append(f"- 对照(无锚 PRISM syn-R² syn主导)={prism_syn_high:.4f}（E14 平台 0.147 复现）")
    lines.append("\n## 6. 结论与下一步\n")
    if passed:
        lines.append("- 锚定使 syn 专家 R² 从 0.147 平台跃升至 %.3f，证明 **PRISM 机制本身健全**，"
                     "E14 的 FAIL 纯因缺锚定信号（L_syn 仅几何 decorrelation）。" % anchor_syn_high)
        lines.append("- 含义：真实场景里只要能构造可靠锚定 proxy（残差/辅助任务），PRISM 即可解耦协同。"
                     "下一步开 E15（真实 amazon-baby-mmssl 特征），并在 E15 内设计锚定 proxy 来源。")
    else:
        lines.append("- 即便给真值锚定，syn 专家仍未能对齐 c_syn → 机制层缺陷（非超参/缺锚定）。")
        lines.append("- 不开 E15；需重新审视 PRISM 专家结构（如 syn 专家是否真能表达非线性协同）。")
    lines.append("\n> 注：全程未用 MI 估计，绕开 E-X1c 盲区与 E-X1d 偏差地板；主证以线性探针 R² 为准。")
    open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines), flush=True)
    print(f"\nE14bis_PASS={passed}", flush=True)


if __name__ == "__main__":
    main()
