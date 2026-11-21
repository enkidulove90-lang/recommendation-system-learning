# 工作树管理方案（2026-11-21）

> 数据来源：`python -m redbook.services.worktree_manager --repo . audit` 真实输出 + 手工核实。
> 本文是唯一权威处理方案；执行动作见 §5 执行清单。

## 0. 理想工作树状态（定义）

1. **一线一树**：每条活跃开发线 = 1 个注册 worktree + 1 个已推送远程的分支。
2. **无孤儿**：`.worktrees/` 与外部 codex worktrees 下不允许存在无 `.git` 的目录快照。
3. **主仓不悬挂**：主仓 HEAD 必须停在某个分支上（当前 detached 于 0d8dd49）。
4. **远端可恢复**：任何只存在于本机的分支（NO_UPSTREAM）要么推送备份，要么其 head 已被其他分支包含。
5. **冗余可审计**：哨兵/CLI 周期输出 audit 报告，REMOVABLE/ORPHAN_DIR/REDUNDANT_COPY 标记驱动清理。

## 1. 现状总表（2026-11-21 实测）

| 工作树 | 分支 | 未提交 | 未推送 | 判定 |
|---|---|---|---|---|
| 主仓（D:/recommendation-system-learning） | **detached** 0d8dd49 | 171（含大量 data untracked；已跟踪改动 4 文件） | — | ⚠️ 悬挂 HEAD |
| sab-anc-design | experiments | 31 | **3**（54012b6/effebb6/a4ecc6f） | ✅ 活跃主战场，保留 |
| catalog-outbox | codex/catalog-outbox（无远程） | 25 | 分支整体 | ✅ paper_intake 硬化活跃，保留 |
| catalog-queues-handoff（codex 外部） | codex/catalog-queues-handoff（无远程） | 38 | 分支整体 | ✅ 队列层，与 outbox 同 tip 但改动集不同 |
| worker-auth-regression（codex 外部） | detached 5208853 | 23 | tip 已含于 codex/intake-backend-contracts | ⚠️ 未提交内容归属会话确认 |
| intake-v2-approval（codex 外部） | detached 73bd6ca | 0 | 0（head 含于 intake-backend-contracts） | 🗑️ **REMOVABLE** |
| sports-feature-import（codex 外部） | codex/sports-feature-import | 0 | 分支整体 | 可删树留分支（先推送） |
| ada-experiment-platform | codex/ada-experiment-platform-internal | 0 | 分支整体 | 保留（ADA 平台活跃）；分支待推送 |
| cloudflare-paper-intake | codex/cloudflare-paper-intake | 0 | 0 | 🗑️ **REMOVABLE**（已全推送） |
| intake-backend-contracts | codex/intake-backend-contracts | 2 | 分支整体 | 保留至 gate 链收尾；2 个 session-archive docs 待提交 |
| opticalrec-single-release | codex/opticalrec-single-release | 0 | **1** | 推送 1 提交后可删树 |
| site-coverr-video（**属 Hexo 仓**） | codex/coverr-home-video | 4 | 分支整体 | Hexo 域，归属其会话 |
| **arxiv-stage01-verify-7bfa14e** | **无 .git（孤儿目录）** | 2004 文件 / 486MB | — | 🗑️ **ORPHAN_DIR + REDUNDANT_COPY** |

分支包含关系（防丢代码的关键事实）：
- 0d8dd49（主仓 detached tip）⊂ experiments / codex/ada-experiment-platform(-internal) / codex/sports-feature-import —— 主仓悬挂不丢提交。
- 5208853（worker-auth-regression tip）⊂ codex/intake-backend-contracts / phase1。
- phase1（3918906）是独立血统，含 intake 修复链。

## 2. 唯一 vs 重复文件判定

**纯重复（可回收）**：
- `arxiv-stage01-verify-7bfa14e`：486MB 快照。171 个 PDF 的 basename **全部**存在于主仓 data/（comm 比对 = 0 独有）；代码文件均为已提交血统的旧快照（stage0-1 验收证据已由 catalog-outbox 分支的 f2d8b9d/0db91e0 等提交承载）。**整目录无独有价值**。
- catalog-queues-handoff 与 catalog-outbox 同 tip（3cabc92），但未提交改动集不重叠（前者 catalog_events/store/worker + cloudflare TS 队列层；后者 pipeline/adapters/repository/service）→ **两树都要保留**，不是冗余。

**各树独有（勿动）**：
- sab-anc-design：redbook/sentinel 全套 + orchestration + 30+ docs（设计文档群）。
- catalog-outbox：paper_intake 管线硬化 + 验收矩阵 + ADR。
- catalog-queues-handoff：catalog_health/catalog_relay/cloudflare migrations/0006。
- worker-auth-regression：remote_worker/control_client/provider-proxy 测试群（23 文件，未提交）。
- ada-experiment-platform：baseline/ada 全套。

## 3. 逐树处理方案

| 树 | 动作 | 顺序 |
|---|---|---|
| arxiv-stage01-verify-7bfa14e | **归档**（`worktree_manager archive`，移动到 archive/worktree_history/，同卷 rename 不删数据）；人工确认后再删归档副本 | 立即可做，回收 486MB |
| intake-v2-approval | `git worktree remove`（clean + head 已包含） | 立即可做 |
| cloudflare-paper-intake | `git worktree remove`（已全推送） | 立即可做 |
| opticalrec-single-release | 先 `git push origin codex/opticalrec-single-release`（1 提交），后 remove 树 | 推送后删 |
| sports-feature-import | 先推分支备份，后 remove 树 | 推送后删 |
| ada-experiment-platform | 保留树（活跃平台）；推送 -internal 分支 | 推送 |
| worker-auth-regression | 23 未提交文件归属会话确认：有保留价值 → 提交到 codex/intake-backend-contracts；无 → 归档删除 | 待会话确认 |
| catalog-queues-handoff / catalog-outbox | 保留；归属会话提交各自未提交改动后推送分支 | 会话内完成 |
| sab-anc-design | 保留；31 未提交中 9 个已跟踪文件归 logging 会话（run_log/worker/delivery/registry/runner/publishing/cli），docs 群归对应设计会话；**3 个未推送提交由本会话负责推送** | 推送 + 会话收尾 |
| 主仓 | 脱离 detached：4 个已跟踪改动（xhs skill/spec/xiaohongshu_delivery+tests）提交到 phase1 血统分支；或确认 phase1 已含 0d8dd49 血统后 checkout phase1 | 待确认血统后执行 |
| site-coverr-video | Hexo 仓域，随 Hexo P0-A 一并收尾 | Hexo 会话 |

## 4. 哨兵接入（冗余代码管理）

本方案已落地 `redbook/services/worktree_manager.py`（9 测试全绿）：
- `audit()`：注册树 + 孤儿目录统一盘点，标记 DIRTY/UNPUSHED/NO_UPSTREAM/DETACHED/DUPLICATE_TIP/REMOVABLE/ORPHAN_DIR/REDUNDANT_COPY/contained_elsewhere。
- `remove()`：门禁——dirty/unpushed 拒绝（需 force），必须显式 confirm，孤儿目录强制走 archive。
- `archive()`：孤儿快照**移动**到 `archive/worktree_history/<name>-<date>/`，不删数据。

哨兵挂接（一行补丁，待 logging 会话落地后加入，避免冲突）：

```python
# runner.run_once 内，retrieval 之后：
from redbook.services.worktree_manager import WorktreeManager
report["worktree_audit"] = [s.to_dict() for s in WorktreeManager(repo_root).audit()]
```

审计结果随 `sentinel.run.report` JSONL 落盘，REDUNDANT_COPY/ORPHAN_DIR 出现即告警；只读不删，清理动作仍由人执行 CLI。

## 5. 未提交/未推送处理（本会话承诺范围）

1. **本会话产出**（worktree_manager + 测试 + 本方案文档）→ 提交到 experiments，**不推送**（沿用会话约定；推送命令：`"/c/Program Files/Git/bin/git.exe" -c http.proxy= -c https.proxy= push origin experiments`）。
2. **3 个未推送提交**（探测修复/调度器/技能管理）同上，等待与 31 个未提交文件（归属会话）一起推送或分批推送。
3. **不执行任何跨会话清理**（worker-auth-regression 23 文件、主仓 4 文件、Hexo 4 文件均归其会话）。
4. 归档/删除操作（§3 标 🗑️）仅在用户明确批准后由 CLI 执行，本文档不含自动执行。
