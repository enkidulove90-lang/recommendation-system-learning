# Skill 统一管理实施记录（含各工作树状态盘点）

日期：2026-11-21
实施分支：`experiments`（sab-anc-design worktree），**已提交、未推送**

---

## 1. 测试可行性评估（先评估，后动手）

| 维度 | 可测性 | 证据方式 |
|---|---|---|
| 登记表 schema / 路由存在性 / 入口与验证命令 | ✅ 完全可测 | `SkillManager.validate()` 真实仓库全绿 |
| IDE 指针 stub 内容（status + 指向 + 无可执行命令） | ✅ 完全可测 | 断言 front matter 与禁令模式 |
| 废弃归档不可执行 | ✅ 完全可测 | history 文件存在 + README 勿执行声明 + 禁令模式扫描 |
| 孤儿/未登记技能、removed 残留、用户级重名 | ✅ 可测（用户级经 `home_override` 注入） | 8 个反例各自触发对应 code |
| deprecate 全链路（归档→指针→登记表） | ✅ 端到端集成可测 | tmp 仓两次 `validate()` 全绿（前→后） |
| AGENTS.md 失效仓库相对链接 | ✅ 可测 | `sweep_markdown_links(AGENTS.md)` 为空 |
| **真实 IDE 路由行为**（WorkBuddy/Claude Code 是否真的按指针改道） | ❌ 不可自动化 | 人工门：在 IDE 内触发一次任务，确认读到 canonical 技能；本记录不声称已验证 |
| CI 运行 | ✅ 工作流已写 | `.github/workflows/skill-routing.yml`（push/PR + 每周巡检），**推送后才生效** |

**完整性声明（防"辅助函数单测=链路完成"幻觉）**：本次的"链路级证据"只有两个——① 真实仓库 `validate()` 零问题（覆盖登记表+磁盘+归档+用户目录四层一致）；② `deprecate()` 在 tmp 仓端到端跑通且事后 validator 全绿。其余 10 个 tmp 反例是 validator 自身的正确性证明，**不等价于**真实 IDE 已按新路由工作；后者待人工门。

## 2. 实施内容

1. **登记表升级 v2**（`config/skill_registry.yaml`）：active 3 条（xhs-paper-draft / multi-platform-publishing / paper-summarize），deprecated 2 条（redbook-publish-legacy 带 history_path；paper-summarize-claude-pointer，正文由继任者保留），removed 1 条（evil-read-arxiv 空壳占位）；全局 `forbidden_executable_patterns` 三条禁令。
2. **正文收敛**：`paper-summarize` 规范正文从 `.claude/skills/` 迁至 `.agents/skills/paper-summarize/SKILL.md`，原位置改写为指针 stub（8 必填区块契约随正文迁移，未丢失）。
3. **空壳清理**：`git rm` 被跟踪的空占位文件 `.claude/skills/evil-read-arxiv` + 删除残留空目录。
4. **SkillManager**（`redbook/services/skill_manager.py`）：`load_registry / validate（7 类问题码）/ inventory / deprecate（端到端退役）/ sweep_markdown_links`；用户级目录扫描支持 `home_override` 注入（CI 无用户目录时跳过）。
5. **测试迁移与扩展**：`tests/test_skill_routing.py` → `redbook/tests/test_skill_routing.py`（**关键修复：原位置在 `pytest.ini testpaths=redbook` 下根本不会被默认收集**——上一会话的路由测试从未进全量回归）；扩至 16 用例。
6. **AGENTS.md** 新增「Skill 管理与路由（统一约定）」章节（登记表约定/规范位置/用户级防重/AI 路由顺序/治理入口/回归与 CI）。
7. **CI**：`.github/workflows/skill-routing.yml`。

## 3. 测试证据

```
16 passed（redbook/tests/test_skill_routing.py，2026-11-21）
- 真实仓库集成：registry 全绿 / AGENTS.md 零失效链接 / 指针与归档不变式 / removed 已删
- 反例 8：ROUTE_MISSING、DUPLICATE_ID、BAD_SUPERSEDED_BY、EXECUTABLE_DEPRECATED、
  ORPHAN_SKILL、REMOVED_STILL_PRESENT、USER_LEVEL_DUPLICATE、ARCHIVE_NOTICE
- 端到端：deprecate("alpha","beta") → 归档存在 + 指针干净 + 登记表更新 + validator 复绿
```

## 4. 各工作树未提交改动报告（防并行冲突）

| 工作树 | 分支 | 未提交 | 归属说明 |
|---|---|---|---|
| sab-anc-design | experiments | ~32 项 | 本次提交 3 组（见 §5）；其余归属其他会话：`redbook/automation/publishing.py`（+18/-2，PF 话题绑定链）**勿动**；notes/data/workflow_state 产物、docs/devplan*、docs/unified*、docs/paper_catalog*、docs/sentinel* 等设计文档 |
| catalog-outbox | codex/catalog-outbox | 25 项 | paper_intake 管线 + 验收矩阵修改（evidence/acceptance_matrix.md、intake-* schemas），归属该分支会话 |
| arxiv-stage01-verify-7bfa14e | （游离） | 171 项 | stage0-1 验证工作树，量最大，勿动 |
| intake-backend-contracts | codex/intake-backend-contracts | 2 项 | 契约层小改 |
| site-coverr-video | codex/coverr-home-video | 4 项 | Hexo 站点视频相关 |
| ada-experiment-platform / cloudflare-paper-intake / opticalrec-single-release | 各自分支 | 0 | 干净 |
| Hexo 主树 D:/enkidulove90-lang.github.io | source | 18 项 | P0-A 数学重构 + math_audit 等待验证提交 |
| Hexo music-diagnostics 工作树 | codex/music-diagnostics | 0 | 干净 |

## 5. 本次提交分组（experiments 分支，均未推送）

1. `fix(sentinel): map restricted HTTP responses to degraded semantics` — probes.py + sentinel.yaml + test_probes.py（今日上午的探测修复 + HTTPError 转换）
2. `feat(sentinel): register daily task scheduler entrypoint` — schedule.py + test_schedule.py（此前会话遗留 untracked）
3. `feat(skills): centralize skill routing registry and manager` — skill_registry.yaml v2 + archive/skill_history + .claude 指针×2 + .agents/paper-summarize 迁移 + evil-read-arxiv 删除 + skill_manager.py + 测试迁移与扩展 + AGENTS.md 章节 + CI 工作流 + 本记录

## 6. 项目演进状态速览（结合另一 agent 记录）

- **XHS 话题绑定**：`xiaohongshu_delivery.py` 合并版（面板读芯片→重开重读→IndexedDB 回读校验）在 2026-11-19 ops/dev 合并文档中标注"⚠️ 未提交"；当前 worktree 里对应未提交残量为 `publishing.py`（+18/-2）——归属其会话，本次未提交。
- **公式保护与 MathJax**：P0-A 配置（CDN.option.mathjax）+ opticalrec-math.js 泛化已在 Hexo 主树，`hexo generate` 验证中断待复跑；对应 TC16（渲染目检）/TC17（normalize_math 与 MinerU 原文逐段一致）为两道门中的人工门，**未关**。
- **参考文献回填 / 机构核验**：backfill_references / backfill_paper_dates / enrich_paper_affiliations 为 Hexo 侧既有工具；对应 TC18（已核验 DOI 才 diff 回填）/TC19（排除名单）沙箱门已过，真机证据待归档 `reports/`。
- **URL 入口测试**：意图层 TC1-TC4（url-only 零 LLM 调用/幂等/非法 URL 结构化错误）沙箱可测，属 devplan_task2 范围。
- **TC15（WeChat 真机草稿+截图）/ TC18 权威文献映射 / 84 个未解析搜索链接**：三者为**待办缺口**——TC15 需登录态人工执行；TC18 真机 diff 证据未归档；84 个未解析链接在仓库内未找到对应清单文件，**需该会话补落盘**（建议位置：Hexo `reports/` 或 `data/workflow_state/`）。
