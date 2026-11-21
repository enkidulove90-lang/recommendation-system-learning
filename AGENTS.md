# Repository agent instructions

本仓库用于推荐系统论文解析、摘要、分类与多平台发布。跨 IDE（WorkBuddy / Codex / Claude Code / Cursor）共用同一套仓库内约束；**规则不要写进任何一台机器的用户目录**。

技能状态、所有者和规范路径登记在 `config/skill_registry.yaml`；下面的路由表仍是任务选择入口。废弃技能只可作历史检索，不可执行。

## Skill 管理与路由（统一约定）

- **唯一登记表**：`config/skill_registry.yaml`（schema_version 2）。每个 skill 的 `id` 全局唯一；`active` 必须带 `entrypoint` 与 `verification_command`；`deprecated` 必须带 `superseded_by`（指向 active id）；`removed` 表示已从磁盘删除、只留决议记录。
- **规范位置**：可执行技能正文一律放 `.agents/skills/<id>/SKILL.md`。IDE 本地目录（`.claude/skills/` 等）**只允许放指针 stub**（front matter 带 `status: deprecated` + 指向规范路径 + 路由说明，不含任何可执行命令）。`archive/skill_history/` 存废弃原文，**勿执行**。
- **用户级防重**：`~/.claude/skills`、`~/.workbuddy/skills`、`~/.codex/skills` 中**禁止定义与仓库 active id 同名的技能**（会造成双路由）；用户级同主题技能只保留指针。本仓库的规则（AGENTS.md / `.agents/skills/` / `config/`）永远覆盖用户级同名规则。
- **AI 路由顺序**：任务进来 → 先查本文件路由表 → 再查 `config/skill_registry.yaml` 确认状态与入口 → 最后读规范 SKILL.md。命中 `deprecated`/`removed` 条目时按 `superseded_by` 改道，不读历史归档。
- **治理入口**：`redbook/services/skill_manager.py` —— `SkillManager(root).validate()` 输出路由问题清单（ROUTE_MISSING / DUPLICATE_ID / EXECUTABLE_DEPRECATED / ORPHAN_SKILL / USER_LEVEL_DUPLICATE 等）；`deprecate(skill_id, superseded_by)` 一步完成"归档原文 → 改写指针 → 更新登记表"。
- **回归与 CI**：`redbook/tests/test_skill_routing.py`（16 用例：真实仓库全绿 + 8 个反例 + deprecate 端到端）随全量测试运行；`.github/workflows/skill-routing.yml` 在 push/PR 上单独校验路由、失效链接与废弃命令。

## 路由表

| 任务 | 必读 | 入口 |
|---|---|---|
| 论文 → 小红书草稿 / 发帖 | `.agents/skills/xhs-paper-draft/SKILL.md` → `redbook/docs/xhs-content-spec.md` | **`python -m redbook.cli note <slug> --validate\|--stage\|--publish`** |
| 多平台发布（公众号 / 知乎 / Twitter 等） | `.agents/skills/multi-platform-publishing/SKILL.md` | 各平台章节内命令；用户级同名 skill 只留指针 |
| 单篇内容声明 | `redbook/notes/<slug>.yaml`（字段：`redbook/notes/_schema.yaml`） | `redbook/services/note_spec.py` |
| 内容组装器 / 编排 | `redbook/services/render_post.py`、`redbook/application/paper_workflow.py` | `render_post`、`PaperCreationWorkflow` |
| 内容规则口径 | `config/xhs_content_rules.yaml`（单一事实源） | `redbook/services/xhs_content_gate.py` |
| 小红书投递实现 | `redbook/infrastructure/xiaohongshu_delivery.py` | `OpenCliXiaohongshuDelivery.deliver` |
| 运行记录 / 会话转储 | `redbook/infrastructure/run_log.py`、`redbook/scripts/session_inspect.py` | `python -m redbook.infrastructure.run_log --summary` |
| 归档日志与临时脚本 | `archive/stdout_logs/README.md`、`archive/session_scripts/README.md` | 只作溯源、勿执行 |
| 只读 / 暂存的 MCP tool | `redbook/mcp/server.py` | `list_note_specs` / `validate_note_spec` / `stage_note_spec`（无 publish） |
| 历史脚本溯源 | `archive/xhs_drafts/README.md` | — |
| 论文解析资产 → Notion / 个人主页 | `docs/notion_paper_library_integration.md`（设计，未实施） | 只读，勿写 Notion |
| 链路历史诊断 | `docs/publishing-pipeline-diagnosis.md` | — |

## 硬性约束（小红书论文帖）

1. **发一篇新帖只新增一个 `redbook/notes/<slug>.yaml`，不新增 .py**。唯一运行入口是 `python -m redbook.cli note <slug>`；`render_post` 是组装器，`PublicationPackage` 是纯投递载体，两者都不自行声明单篇内容。
2. 不要新建根目录 `build_xhs_draft_<name>.py` 手写 `BODY`，不要再直接调 `PersonaPostComposer().compose()` 当入口。14 个历史脚本已移到 `archive/xhs_drafts/`，只作溯源、勿执行。
3. 发布闸门五条：正文纯文本、≤1000 字、独立一行「局限」段、话题在白名单内、`visual_review` 有真实目检记录。改口径只改 `config/xhs_content_rules.yaml`。
4. 只存草稿不公开发布；话题绑定成平台真实实体；PDF 附件在存草稿前完成。`--publish` 只能人工在 CLI 执行，MCP 不暴露该动作。
5. `redbook/services/content_spec.py` 是 2026-10-28 冻结的 7 段结构口径（明确不限字数），与发布闸门是两层契约，**不要为加字数上限去改它**。
6. `status: published` 的历史稿只归档，`stage_note()` 会拒绝重发；重发须改回 `validated` 并补真实逐张目检记录。

## 通用注意

- **论文目录依赖方向**：`paper_intake` 是身份与准入事实源，禁止 import `redbook.*`；跨域交接只能经 catalog outbox，哨兵池只接收目录快照，不反向写目录身份字段。

- **规则优先级**：仓库内 `AGENTS.md` / `.agents/skills/` / `config/` 覆盖任何用户级 skill 的同名规则；用户级 `multi-platform-publishing` 与 `.claude/skills/redbook-publish` 只作路由或历史参考。
- **不要再往仓库根写日志**：`logs_*.txt` / `_*.txt` / `_*.py` 已被 `.gitignore` 拦下；正式入口的运行记录写 `data/logs/runs.jsonl`（`redbook.infrastructure.run_log`），会话转储用 `python -m redbook.scripts.session_inspect <session.jsonl>`。
- Windows 环境下 native 命令请显式传仓库绝对路径；Git Bash 里 `git -C /c/...` 会失败，用 `git -C "C:/..."`。
- 根目录 `.gitignore` 含 `*.json`，新增配置文件若需入库请用 `.yaml` 或显式加白名单例外。
- 入库前扫 `ntn_` / `sk-` / `LEETCODE_SESSION` / `csrftoken` 等密钥特征；`.env` 永不入包。
- 验证命令见 `redbook/docs/xhs-content-spec.md` §7。
