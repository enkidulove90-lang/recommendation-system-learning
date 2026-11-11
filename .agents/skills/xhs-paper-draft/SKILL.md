---
name: xhs-paper-draft
description: >
  MUST USE when the task is to turn an academic paper into a Xiaohongshu (小红书) draft
  in this repository: 发小红书 / 论文帖 / 论文速递 / arxiv 发小红书 / compose-post /
  save-xhs-draft / XHS paper draft. Covers paper facts, figure selection, copy rules,
  staging, draft saving and verification. Also触发：redbook.cli note / note spec /
  redbook/notes/*.yaml.
  NOT for: 微信公众号 / 知乎 / 纯论文摘要（无发布意图）。
---

# 论文 → 小红书草稿（仓库内统一链路）

本 skill 是跨 IDE 版本：WorkBuddy、Codex、Claude Code、Cursor 读到的是同一份约束。
**规则的可执行定义在仓库代码与配置里，不在任何一台机器的用户目录里。**

> **优先级（2026-11-11）**：本文件 + `AGENTS.md` + `config/xhs_content_rules.yaml` 高于任何用户级
> skill。用户级 `~/.workbuddy/skills/multi-platform-publishing/` 已整份迁入仓库
> `.agents/skills/multi-platform-publishing/`，本机只留路由指针；其旧版
> `canonical: build_xhs_draft.py` / `render_note` 口径、以及
> `.claude/skills/redbook-publish/SKILL.md` 的手写模板路径都已作废。

## 0. 先读这三份

| 文件 | 作用 |
|---|---|
| `AGENTS.md`（仓库根） | 路由总入口 |
| `redbook/docs/xhs-content-spec.md` | 完整规范、架构、命令、迁移说明 |
| `config/xhs_content_rules.yaml` | **单一事实源**：字数/话题白名单/标记符/目检规则 |

实现入口：`redbook/cli.py note`、`redbook/services/note_spec.py`、
`redbook/application/paper_workflow.py`、`redbook/services/render_post.py`、
`redbook/services/xhs_content_gate.py`。单篇字段规范：`redbook/notes/_schema.yaml`。

## 1. 铁律：一篇一个 spec，一条命令

**发新帖只新增一个 `redbook/notes/<slug>.yaml`，不新增 .py。**
唯一运行入口是 `python -m redbook.cli note <slug> --validate | --stage | --publish`。

禁止：
- 新建 `build_xhs_draft_<name>.py` 手写 `BODY`（14 个历史脚本已归档到 `archive/xhs_drafts/`，只作溯源）；
- 绕过 CLI 自己拼 `PublicationPackage`；
- 直接调 `PersonaPostComposer().compose()` 当入口，或自造分节模板 / 话题列表。

```
redbook/notes/<slug>.yaml  (title / body / figures / topics / links / pdf_path / visual_review)
        ↓
redbook.cli note <slug> → PaperCreationWorkflow.build_note_package()
        ↓ 定稿正文走 render_post(body=...)：跳过模板，只过闸门
render_package() → PublicationPackage → XhsPublisher.validate() → stage()/publish()
        ↓
OpenCliXiaohongshuDelivery.deliver()   ← 同一个投递器，topics → PDF → 存草稿
```

`compose-post` / `save-xhs-draft` 仅作生成稿的向后兼容路径；本仓库里发布论文帖不再走它们。
MCP 只开放 `list_note_specs` / `validate_note_spec` / `stage_note_spec`，**没有 publish**，
真实草稿箱写入必须由人在 CLI 显式执行。

## 2. 五条硬约束（会被代码拒绝，不是建议）

1. **正文纯文本**：不得出现 `#`、`**`、`__`、`~~`、反引号、`](`。小红书编辑器原样显示 Markdown。
2. **正文 ≤1000 字**、**标题 ≤20 字**。迭代时用 `DRY_RUN` 量字数，不硬删段落。
3. **必须有独立的「⚠️ 局限」段**。只写论文验证过的数字；用户给的结论若与原文冲突（例如「top-K 精度不降」实为 −4.03%），写进局限而不是藏起来。
4. **话题必须在 `config/xhs_content_rules.yaml` 白名单内**，且绑定为平台真实实体。`AI新手村` / `AI工具使用` / `ai大模型` 这类泛流量标签会被拒绝；用 `论文分享 / 人工智能 / 推荐系统 / 深度学习 / AI` 等垂直标签。
5. **`metadata.visual_review` 必须是真实逐张目检记录**，缺失或 `pending` 一律拦下。

平台侧另有：图片 1–9 张、论文 PDF 附件存在且为 `.pdf`、只存草稿不发布。

## 3. 事实来源

- 优先 `https://arxiv.org/e-print/<id>` 源包，直接读 `.tex` 原文（方法/主表/消融分段）；
- `WebFetch https://arxiv.org/abs/<id>` 取标题、作者、版本日期、comments 里的 venue；
- 代码状态不能只按论文名搜 GitHub：扫 PDF 全文脚注 URL、查作者账号全部仓库、确认实现确实在库里，分档写「已开源 / 声明开源但实现待补 / 未开源」；
- 摘要写成 6 个 `##` 段：`主要贡献` / `创新点` / `方法论` / `实验结果` / `局限` / `借鉴`。缺段写「原文未披露」，不要虚构；
- 预印本不要写成已录用论文。

## 4. 取图（必须目视）

1. 源包作者原图优先；矢量 `.pdf` 用 PyMuPDF `Matrix(3,3)` 渲染；
2. 只有 1024px 位图时，先确认 PDF 内嵌无更高清版本，再 1.8× LANCZOS + 轻锐化；
3. 内联图（tikz/pgfplots）按图注 clip + 6x 渲染，横向给坐标轴刻度留空间；
4. 学术表格改自制数字卡，标注「自制」；
5. **逐张看图**确认内容、坐标/图例、清晰度、自制卡无溢出/重叠，把结论写进 `visual_review`。

图序按叙事排：封面/架构 → 机制 → 数字卡 → 结果 → 消融。

## 5. 最短命令

```bash
# 1) 复制一份 spec 模板（不要复制 .py 脚本）
cp redbook/notes/2601.21452.yaml redbook/notes/<slug>.yaml
# 2) 改 paper_id / slug / title / body / figures / topics / links / pdf_path / visual_review
# 3) 三步走，最后一步只在人工目检后执行
python -m redbook.cli note --list
python -m redbook.cli note <slug> --validate
python -m redbook.cli note <slug> --stage
python -m redbook.cli note <slug> --publish
```

`--validate` 不检查图片文件是否存在（另一台机器 clone 后没有 `data/parsed/*.png`），
`--stage` 才检查；`status: published` 的历史归档稿会被拒绝重发。

发布前自检（应全过）：

```bash
python -m pytest redbook/tests/test_xhs_content_gate.py \
  redbook/tests/test_content_spec.py redbook/tests/test_automation.py \
  redbook/tests/test_note_spec.py redbook/tests/test_note_migration.py \
  redbook/tests/test_cards_and_mcp.py -q
```

## 6. 工程坑（跨机器已验证）

- **Windows PowerShell 5.1** 捕获原生命令 stdout 按 GBK 解码，中文标题乱码不可逆：让 Python 直接写 UTF-8 文件再读，控制台只打印 ASCII 的 id / 计数。
- 发布动作耗时长且中文多，用 PowerShell `Out-File -Encoding utf8` 落日志并查 `$LASTEXITCODE`。
- 草稿核验**只用 ASCII `draft_id` 子串**，不要依赖返回里的中文标题。
- `drafts` 列表 API 不暴露 PDF 字段，最终在创作者后台目测 PDF 卡片。
- 发布不幂等；改内容要重新 stage 拿新 hash，先发新稿成功后再删旧稿。
- 换机器先探测依赖：`python -c "import yaml, openai, pydantic, pytest; print('deps ok')"`。托管 venv 可能缺 `openai`/`pydantic`，导致 `redbook.cli` 顶层 import 失败。
- 历史手写脚本已整体归档到 `archive/xhs_drafts/`，映射表见该目录 README；不要再执行它们。
- spec 路径一律相对**仓库根**（`parsed_dir` / `pdf_path`），`figures[].file` 相对 `parsed_dir`；旧脚本的 `ROOT = Path(".")` 依赖 cwd，换机器就断。
- 同一论文有多个版本时用 `slug` 区分文件名（如 `2605.29322_ace_v2.yaml`），`slug` 必须等于文件名 stem。
- 「局限」段按**独立一行**判定（长度上限见 `config/xhs_content_rules.yaml` 的 `section_line_max_chars`），`⚠️ 局限：……` 题头与内容同行也合规。
- 自制数字卡用 `redbook/services/cards.py`，不要在每篇脚本里复制一份 `draw_numbers_card`。

## 7. 参考原文

`references/` 下保留了用户级 skill 的原始全文（含更细的踩坑记录）。其中 WorkBuddy 专有工具名（`Read` / `Skill` / `ViewImage` / `present_files`）和 `C:/Users/xu.yan1/...` 绝对路径需按你当前 IDE 与机器映射；**规范以本文件 + 仓库配置为准**。
