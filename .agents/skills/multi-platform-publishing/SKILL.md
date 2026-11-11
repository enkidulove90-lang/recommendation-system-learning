---
name: multi-platform-publishing
description: >
  MUST USE when user wants to 发布/publish/投稿/推送 论文内容到 小红书/微信公众号/知乎/Twitter。
  覆盖从论文摘要到平台发布的完整链路：内容渲染 → 图片选择 → 草稿创建 → 人工审核 → 发布。
  支持小红书（OpenCLI CDP 单会话路径；xhs-cli 逆向 API 已弃用，仅作历史参考）和微信公众号（browser-bridge 驱动真实编辑器 + HTML 预览 fallback；旧的 opencli weixin create-draft 因标题丢失/正文不渲染 Markdown 已弃用）。

  触发词：发布论文/小红书发帖/公众号推送/wechat draft/小红书草稿/多平台发布/
  publish paper/xhs post/微信公众号草稿/知乎回答

  NOT for: 纯内容生成（无发布意图时用 paper-summary-log skill）；
  纯搜索/读取社交平台内容（用 Agent-Reach skill）。
triggers:
  - publish: 发布/发帖/推送/投稿/publish/草稿/draft
  - xhs: 小红书/xhs/xiaohongshu/红书
  - wechat: 微信公众号/公众号/wechat/weixin/MP
  - zhihu: 知乎/zhihu
  - twitter: twitter/x/推特
  - multi: 多平台/全平台/multi-platform/同步发布
metadata:
  openclaw:
    homepage: ""
---

# 多平台论文发布 Skill

> **跨 IDE 全局版本（2026-11-11）**：本目录由 `~/.workbuddy/skills/multi-platform-publishing/`
> 整体迁入仓库并推到 GitHub，WorkBuddy / Codex / Claude Code / Cursor 读到同一份。
> 用户级同名 skill 只保留路由指针，不再是规则来源。公众号 / 知乎 / Twitter 章节原文保留。
> 文中 `C:/Users/xu.yan1/...` 一类机器路径按当前机器映射；小红书论文帖的现行口径见
> `.agents/skills/xhs-paper-draft/SKILL.md`，优先级见仓库根 `AGENTS.md`。

从论文摘要到小红书/微信公众号/知乎等多平台发布的完整链路。

## 常驻规则

1. **先 stage 后 publish**：所有平台先生成审核包（`stage`），人工确认后才执行 `publish`。
2. **幂等控制**：同一论文同一平台只允许一个草稿，以 `content_hash` 去重。
3. **不替用户登录**：小红书使用已保存的 Cookie（`~/.xiaohongshu-cli/cookies.json`）；公众号使用 OpenCLI 已有 Chrome 会话或手动上传。
4. **先查后发**：发布前先检查 Cookie 是否过期、工具是否可用。

## 路由表

| 用户意图 | 平台 | 详细文档 |
|---------|------|---------|
| 小红书论文帖 | xhs | **`.agents/skills/xhs-paper-draft/SKILL.md`**（跨 IDE 全局）；[OpenCLI 历史参考](references/xhs-publishing.md) |
| 微信公众号草稿 | wechat | [references/wechat-publishing.md](references/wechat-publishing.md) · [正文模板](references/wechat-body-template.md) · [帖子模板](references/wechat-post-template.md) |
| 公众号文章抓取/参考 | wechat-read | OpenCLI `weixin search`/`download`（仅规范 `/s/SHORTID` 链接；Sogou 分享链接不可外部抓，详见 wechat-publishing §十） |
| 知乎回答 | zhihu | 本文档（见下方快速命令） |
| 内容模板选择 | — | [references/content-templates.md](references/content-templates.md) |
| 图片选择与合成 | — | [references/image-pipeline.md](references/image-pipeline.md) |

## 快速命令

### 小红书论文帖 → 仓库全局 skill（唯一规范入口）

**本 skill 不再声明小红书口径。** 跨 IDE 的单一事实源在仓库内：

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | 路由总入口（优先级高于任何用户级 skill） |
| `.agents/skills/xhs-paper-draft/SKILL.md` | 全局 skill：事实来源 / 取图 / 五条硬约束 |
| `redbook/docs/xhs-content-spec.md` | 完整规范与验证命令 |
| `config/xhs_content_rules.yaml` | 机器规则（单一事实源） |
| `redbook/notes/<slug>.yaml` | 单篇内容声明 |

```bash
python -m redbook.cli note --list
python -m redbook.cli note <slug> --validate
python -m redbook.cli note <slug> --stage
python -m redbook.cli note <slug> --publish   # 人工目检后才执行
```

一篇新帖只新增一个 YAML，不新增 .py。`build_xhs_draft.py` / `paper_to_xhs.render_note` /
`cli stage --paper paper_card.json` 都是 2026-11-10 前的历史路径，脚本已归档到
`archive/xhs_drafts/`，**勿执行**。`references/xhs-publishing.md` 只作 OpenCLI / CDP
底层排查资料，其中 §8.0 / §8.1 的 canonical 命令与 300–700 字模板均已作废。

### 微信公众号草稿

```bash
# 推荐：从 11 维度摘要直接生成并投递（自动 stage → publish，未登录回退 HTML）
python -m redbook.automation.paper_to_wechat --paper-id 2302.08191

# 或：先 stage 审核包，人工确认后再 publish
python -m redbook.automation.cli --data-root data stage \
  --platform wechat --paper data/paper_card.json --canonical-url https://arxiv.org/abs/XXXX
python -m redbook.automation.cli --data-root data publish \
  --platform wechat --staged-id <content_hash>
```

公众号要求已登录 mp.weixin.qq.com 的 Chrome 会话（browser-bridge 复用其登录态）。

> **正文已渲染为 HTML**：`paper_to_wechat.build_package` 现在会生成 `metadata.wechat_html`
> （由 `render_wechat_html` 产出的微信安全内联样式 HTML：段标题色条 / 📌高亮框 / 编号列表 /
> 文末 arXiv·PDF 链接）。browser-bridge 直接 `innerHTML` 注入；未登录时 `render_wechat_preview_doc`
> 生成自包含预览 `data/publish_preview/wechat/<title>.html`（标题+封面+富正文+全部图）供手动粘贴。
> 换配色改 `paper_to_wechat.py` 的 `_ACCENT`/`_ACCENT_BG` 常量即可。
未登录时 `publish` 自动回退到本地 HTML 预览（`data/publish_preview/wechat/*.html`）供手动上传。
当前默认路径是 `WeChatDraftDelivery`（browser-bridge）：标题以 `browser fill` verified 写入、
正文以 `innerHTML <p>` 注入、封面经官方选择器设为封面——编辑器正常渲染，不再有「标题空白 / 正文像 changelog」问题。
旧 `opencli weixin create-draft` 因这两个 bug 已弃用。多图深度图文仍用 HTML 预览手动上传。
详见 [references/wechat-publishing.md](references/wechat-publishing.md) 与 [正文模板](references/wechat-body-template.md)。

### 抓取公众号参考帖子（选题/模板）

```bash
# 搜狗微信搜索公众号文章（返回 title/url/summary/publish_time）
opencli weixin search "推荐系统 论文" --limit 10 -f json

# 下载规范链接文章为 Markdown（必须是 mp.weixin.qq.com/s/SHORTID，Sogou 分享链接不行）
opencli weixin download --url "https://mp.weixin.qq.com/s/SHORTID" --output data/weixin_crawl
```
> 实测：搜"代码随想录/再见Superpowers"可命中其最新帖；Sogou 跳转链接为会话绑定，无法外部抓取，
> 需改用公开镜像。详见 wechat-publishing §十。

### 知乎回答

```bash
# 1. 生成审核包
python -m redbook.automation.cli --data-root data stage \
  --platform zhihu_answer --paper data/paper_card.json --canonical-url https://arxiv.org/abs/XXXX

# 2. 人工在知乎找到相关问题后发布
```

## 内容版本矩阵

| 平台 | 字数 | 图片数 | 结构 |
|------|------|--------|------|
| xhs | 300-700 + emoji | 5 | 🎓✨🧠📊💡 + #话题 + 链接 |
| wechat | 1,200-2,000 | 1 封面(opencli) / 5-7(HTML预览) | 背景→方法→实验→局限→实践启发→参考 |
| zhihu_answer | 800-1,500 | 1-3 | 先回答→再论证→来源 |
| x_thread | ≤280 × 2-5 条 | 1-4 | 结论→方法→结果→链接 |
| jike | 100-220 | 0 | 结论→为什么→链接 |

> xhs 行是 2026-11-10 前的模板口径；现行发布闸门（纯文本 / ≤1000 字 / 局限段 /
> 话题白名单 / 逐张目检）见 `config/xhs_content_rules.yaml`。

## 前置条件

| 条件 | 小红书 | 微信公众号 |
|------|--------|-----------|
| Cookie/登录态 | `~/.xiaohongshu-cli/cookies.json` | OpenCLI Chrome 会话 |
| CLI 工具 | `xhs` (pip install xiaohongshu-cli) | `opencli` 或手动上传 |
| 图片 | 论文解析目录 `data/parsed/*/images/` | 同左 |
| 摘要 | `data/summaries/*_summary.json` | 同左 |

## Agent-Reach 集成

发布前调研参考帖子格式：
```bash
# 搜索同领域爆款帖子
xhs search "推荐系统 论文" --json

# 读取目标帖子详情
xhs read <note_url> --comments --json
```

Agent-Reach 用于读取/搜索，不用于发布。详见 [references/xhs-publishing.md](references/xhs-publishing.md)。

## 详细文档

- [小红书发布指南](references/xhs-publishing.md) — **历史参考**：OpenCLI / CDP / Cookie 底层排查；论文帖规范以 `.agents/skills/xhs-paper-draft/SKILL.md` 为准
- [微信公众号发布指南](references/wechat-publishing.md) — browser-bridge（弃用 create-draft 的根因）、微信风味纯文本、抓取能力与自动化工作流（§十）
- [微信公众号正文模板](references/wechat-body-template.md) — 微信风味纯文本骨架（emoji 标记 + 空行 + 「」强调，无 Markdown 语法）
- [微信公众号帖子模板](references/wechat-post-template.md) — 以代码随想录《再见Superpowers》为范例的爆款长文骨架
- [内容模板](references/content-templates.md) — 模板 A（单篇深度）和模板 B（综述汇总）
- [图片流水线](references/image-pipeline.md) — arXiv 源优先 → PDF 高清回退 → MinerU 兜底
