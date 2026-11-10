# 小红书论文帖 · 统一内容规范（跨 IDE 单一事实源）

> 建立日期：2026-11-10
> 背景：`docs/publishing-pipeline-diagnosis.md` §2.3「双投递路径冲突」、§2.4「两条独立的内容生成路径，且格式不统一」。
> 2026-11-08 同项目在两台机器（WorkBuddy / Codex）产出差异极大的草稿，根因是各自走了不同的内容生成路径。本文把口径固化到仓库，任何一方 clone 后读到的都是同一份约束。

## 1. 架构：一篇一个 spec，一条命令，一份闸门

**2026-11-10 二次收敛**：14 个 `build_xhs_draft_*.py` 已整体迁到
`archive/xhs_drafts/`（映射表见该目录 README），每篇论文只留一个
`redbook/notes/<slug>.yaml`。字段规范在 `redbook/notes/_schema.yaml`。

```
redbook/notes/<slug>.yaml        ← 每篇唯一新增物：标题 / 定稿正文 / 图序 / 话题 / 链接 / 目检
        │
        ▼
python -m redbook.cli note <slug> --list | --validate | --stage | --publish
        │
        ▼
PaperCreationWorkflow.build_note_package()   ← 复用已有 checkpoint 状态机
        │  定稿正文走 render_post(body=...)：跳过 persona 模板，只过闸门
        │  生成稿走 render_post(summary, figures)：persona 模板
        ▼
render_package() → PublicationPackage → XhsPublisher.validate()
        │  发布闸门：纯文本 / ≤1000 字 / 局限段 / 话题白名单 / 图片数 / 目检标记
        ▼
XhsPublisher.stage() → publish() → OpenCliXiaohongshuDelivery.deliver()
        （topics → PDF → 存草稿，只存草稿不发布）
```

**不要再做的事**：新建根目录 `build_xhs_draft_<name>.py`、把正文硬编码进 Python、
或绕过 `redbook.cli note` 自己拼 `PublicationPackage`。内容由 note spec 声明，
`render_post` 只是唯一的组装器，`PublicationPackage` 只是投递载体。

MCP 侧（`redbook/mcp/server.py`）另暴露 `list_note_specs` / `validate_note_spec` /
`stage_note_spec` 三个 tool；**刻意不暴露 publish**，真实草稿箱写入只能由人在 CLI
显式执行，避免自动化误触。

## 2. 五条铁律

| # | 规则 | 值 / 判据 | 校验函数 |
|---|---|---|---|
| 1 | 正文纯文本 | 不含 `#`、`**`、`__`、`~~`、`` ` ``、`](` | `validate_xhs_content` |
| 2 | 字数上限 | `len(body) <= 1000` | 同上 |
| 3 | 必须有局限段 | 存在独立一行含「局限」且长度 ≤ `section_line_max_chars`（默认 120） | 同上 |
| 4 | 话题白名单 | 每个话题归一后在 `topic_allowlist` 内 | 同上 |
| 5 | 图片目检标记 | `metadata.visual_review` 为真实目视记录，不能缺失或 `pending` | `validate_visual_review` |

另有平台硬限制，由 `XhsPublisher.validate()` / `DraftPayload.validate()` 各自执行：标题 ≤20 字、图片 1–9 张、论文 PDF 附件存在且后缀 `.pdf`、话题必须是平台真实实体。

### 单一事实源

所有规则数据在 **`config/xhs_content_rules.yaml`**，代码不含硬编码常量。改口径只改这个文件，三处调用方立即同步：

- `redbook/services/render_post.py` → `validate_xhs_content`
- `redbook/cli.py compose-post` → 走 `render_post`，间接受约束
- `redbook/automation/publishing.py::XhsPublisher.validate` → `validate_xhs_content` + `validate_visual_review`

> 为什么是 `.yaml` 不是 `.json`：仓库根 `.gitignore` 有 `*.json`，规则文件若用 JSON 会被忽略，另一台机器 clone 后读不到，等于没有约束。

### 与 `content_spec.py` 的边界

`redbook/services/content_spec.py` 是 2026-10-28 冻结的**7 段结构组装口径**，其 docstring 明确「不限制总字数；字数只作日志指标」。本规范是**平台发布准入闸门**，是另一层契约。两者不互相替换，不要为了加 1000 字上限去改 `content_spec`（会破坏 `test_content_spec.py` 的验收断言）。

## 3. 正文结构

`render_post` 的默认 persona `research_translator` 产出 8 段，每个事实槽位**只出现一次**：

```
🎓 论文在解决什么？   ← 主要贡献
✨ 核心亮点           ← 创新点（缺失写「原文未披露独立创新点」）
🧠 方法拆解           ← 方法论
📊 关键实验           ← 实验结果
📝 阅读注释           ← 借鉴
💻 代码状态           ← 官方 GitHub 有无
⚠️ 局限               ← 局限（所有 persona 共用，统一在外层追加）
📎 论文与代码         ← arXiv abs / pdf / GitHub 单独成段
```

旧版 `persona_composer.py` 把 `problem` 和 `method` 各插入两次（「论文在解决什么」≡「核心亮点」第 1 条、「核心亮点」第 2 条 ≡「方法拆解」），已修复并有回归测试 `test_problem_and_method_each_appear_once`。

**事实摘要 `summary` 建议提供 6 个 `##` 段**：`主要贡献` / `创新点` / `方法论` / `实验结果` / `局限` / `借鉴`。缺段一律写「原文未披露」，禁止虚构；缺「局限」会让草稿显得空，但对闸门前仍是合规的（题头存在）。

## 4. 取图规范

1. `https://arxiv.org/e-print/<id>` 源包优先取作者原图；矢量 `.pdf` 用 PyMuPDF 3x 渲染。
2. 源图只有 1024px 位图时，先确认 PDF 内嵌无更高清版本，再 1.8× LANCZOS + 轻锐化。
3. 学术表格不要直接截图（手机不可读），改自制数字卡，并在 `figures.json` 标注「自制」。
4. 内联图（tikz/pgfplots）按图注 clip 裁 + 6x 渲染，横向必须留出坐标轴刻度文本的空间。
5. **逐张目视检查**每张图（画了什么、坐标/图例、字是否看得清、自制卡是否溢出），把结果写进 `metadata.visual_review`。没有目检记录的包会被发布闸门拒绝。

## 5. 最短可用命令（唯一入口）

```bash
python -m redbook.cli note --list                  # 列出全部 spec 与状态
python -m redbook.cli note <slug> --validate      # 只跑内容闸门，不检查图片文件
python -m redbook.cli note <slug> --stage         # 落盘不可变 review 包 + 推进 checkpoint
python -m redbook.cli note <slug> --publish       # 人工目检后才投递草稿箱
```

`--validate` 刻意不检查图片文件是否存在：`data/parsed/**/*.png` 被 `.gitignore`
挡掉，另一台机器 clone 后天然没有图；`--stage` 才检查图片与 PDF 并调用
`XhsPublisher.validate()` 复核全部铁律。

向后兼容仍保留 `compose-post` / `save-xhs-draft`（生成稿走 persona 模板），
但新发一篇论文帖**只需新增一个 YAML**，不再新增 `.py`。

**已发布归档稿**：`status: published` 的 spec 只作溯源，`stage_note()` 会拒绝重发；
要重发须先把 status 改回 `validated` 并补一条真实逐张目检记录。

## 6. 旧脚本迁移（已完成）

14 个草稿脚本 + 8 个工具脚本已移到 `archive/xhs_drafts/`，逐个加了
`DEPRECATED` 头指向对应 spec / 新模块，映射表见该目录 README。迁移遵循
「正文原样搬、不为过闸门改写」，`test_note_migration.py` 逐字比对锁死。

其余能力归位：

| 旧工具 | 新位置 |
|---|---|
| 图注定位裁矢量图 | `redbook/services/figure_crop.py` |
| ACM PDF / Cloudflare 探测 | `redbook/infrastructure/paper_sources/acm_dl.py` |
| 草稿箱清点 / 核验 / 删除 | `redbook/scripts/xhs_drafts.py` |
| 自制数字卡 / 位图放大 | `redbook/services/cards.py`（新稿可声明式调用） |

两篇历史稿不符合新闸门且**正文未改**：`2608.14429`（用「⚠️ 一点提醒」代替
局限题头）、`3773078.3831765`（冻结 7 段口径 1328 字）。它们会被闸门拦住、
无法重发；如需重新启用须由人工决定补写还是维持归档。

## 7. 环境与验证

CLI 顶层 import 链会加载 `openai`、`pydantic`、`yaml`、`pytest`、`PIL` 等。本机 `C:\Program Files\Python311\python.exe` 依赖齐全；WorkBuddy 托管的 venv 缺 `openai` / `pydantic`，跑 CLI 会 `ModuleNotFoundError`（这不是代码缺陷，是环境差异）。换机器先探测：

```bash
python -c "import yaml, openai, pydantic, pytest; print('deps ok')"
```

回归验证：

```bash
python -m pytest \
  redbook/tests/test_content_spec.py \
  redbook/tests/test_xiaohongshu_delivery.py \
  redbook/tests/test_automation.py \
  redbook/test_figure_workflow.py \
  redbook/tests/test_xhs_content_gate.py -q
```

当前基线：`63 passed, 11 subtests passed`。

## 8. 发布侧铁律（沿用既有实现）

- 只存草稿，不公开发布；`state = saved_draft_only`。
- 同一个未保存的编辑器会话内完成：图 → 标题 → 正文 → 话题 → PDF → **最后**才存草稿。
- 严禁「先存草稿再回草稿箱补附件」，CDP 上下文会丢失。
- 话题必须绑定成平台真实实体，不靠正文里的 `#文本`。
- 发布不幂等：同一 `staged_id` 重复 `publish` 会多建一条草稿；改内容要重新 stage（新 hash）。
- 核验用 ASCII `draft_id` 子串匹配，不要用返回里的中文标题（PowerShell 5.1 按 GBK 解码会不可逆乱码）。
