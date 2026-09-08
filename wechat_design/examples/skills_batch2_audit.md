# 审计 + 安装：`guizang-social-card-skill` 与 `html-anything`

> 审计时间：2026-08-11
> 背景：用户确认这两个仓库「都很有用」，按之前 xiaowan 的同样流程做下载→审计→安装/文档。

---

## 一、`guizang-social-card-skill`（@op7418）

**是什么**：社交媒体图文卡片生成 skill——小红书 3:4 图文、Live Photo 动图卡、以及**微信公众号封面（21:9 主封面 + 1:1 方封面成对）**。两种视觉体系：Editorial 杂志墨水（6 套调色板）/ Swiss 国际主义（4 套 accent）。自带 2 个种子模板 + 16 条 Editorial 布局 + 12 条 Swiss 布局 + 自动校验脚本 `validate-social-deck.mjs`（查溢出/字号/密度等 9 项）。

**安全审计：P2（安全）**
- 仅依赖 `playwright`（渲染用，本地）；无 postinstall、无网络回传。
- 抓取网络图仅限 Unsplash/Pexels/Flickr 免费图库，且「先取后告知、由用户决定署名」。
- ⚠️ **授权提示**：`package.json` 标 ISC，但附带 `COMMERCIAL_LICENSING.md`——**个人/学术使用（如论文解读公众号）无碍；若要做商业产品集成需单独谈授权**。

**安装**：✅ 已装到用户级 `~/.workbuddy/skills/guizang-social-card-skill/`（完整：SKILL.md + 18 个 references + 模板/脚本/资产）。

**对我们管道的好内容**：
| 我们文件的痛点 | guizang 解法 |
|---|---|
| 封面用论文原图（且是本地路径） | 生成正规 **WeChat 21:9 + 1:1 封面对**，同一 HTML 内双比例对照，标题/副标题/视觉关系一次排好 |
| 只有 1 张封面，缺社交分发素材 | 可顺手出小红书 3:4 图文卡 / 微博卡，一文多用 |
| 配图「AI 感」重 | 强制「用户自备图优先」+ 真实图库 + 截图处理规范，避免廉价 AI 插画 |

---

## 二、`html-anything`（@nexu-io）

**是什么**：一个**本地 Next.js Web 应用**（不是 WorkBuddy skill）。它自动识别你本机已登录的 coding-agent CLI（Claude Code / Codex / Cursor / Gemini / Copilot / OpenCode / Qwen / Aider / IBM Bob 共 9 个），把 75 套 skill 模板喂给 agent，SSE 流式把生成的 HTML 灌进沙箱 iframe 实时预览，再一键导出到**微信公众号（juice 内联 CSS，粘贴 0 调整）/ 知乎 / 推特 / 小红书 / PNG**。

**安全审计：P2（安全）**
- 许可证 **Apache-2.0**；纯本地优先，复用你已登录的 agent session，**零 API Key**。
- 用户 HTML 走 `iframe[sandbox]` + `dompurify` XSS 防御；`child_process.spawn` 只 spawn**你本机已装**的 agent CLI（不是任意代码）。
- 依赖干净：`next` 标准栈 + `juice`/`modern-screenshot`/`xlsx`/`marked`/`dompurify`，无 postinstall 钩子，无可疑包。

**⚠️ 安装决策：不装进 skills 目录**。它没有根级 `SKILL.md`，本质是带 75 个模板的 Web 应用；塞进 `~/.workbuddy/skills/` 会误当成 skill 且体积庞大。已作为**伴随工具**保留在：
`C:/Users/xu.yan1/papers/recommendation-system-learning/.audit_htmlanything`

**运行方式（在你自己机器上）**：
```bash
cd .audit_htmlanything
pnpm install
pnpm -F @html-anything/next dev   # → http://localhost:3000
```
> 本沙箱无 pnpm / 无本地 agent CLI，无法直接跑；它是你本机的桌面工具。

**对我们管道的好内容（两条正好补我们的缺口）**：
1. **微信公众号导出 = `juice` 内联 CSS + `data-tool` 标记 → 粘贴 0 调整**。这与 gzh-design / multi-platform-publishing 是**同层互补**的另一种「粘贴不掉格式」实现。
2. **知乎导出 = `<mjx-container>` → `data-eeimg` 公式图占位**。这正是我前面对 loopsbench 文件预警的**「公式→图片」缺口**的标准解法——写推荐系统论文（满屏公式）时，知乎/公众号侧用这招把 LaTeX 转成图，不再丢公式。html-anything 的 75 模板里也直接 vendor 了 guizang 的 deck 模板。

---

## 三、现在的完整技能栈（与本文工作流对应）

| 层 | skill / 工具 | 角色 | 状态 |
|---|---|---|---|
| 排版引擎 | `gzh-design`（项目级，recsys-blue 已注册） | Markdown→公众号兼容 HTML、组件库、双校验 | ✅ 已装 |
| 移动端审美层 | `xiaowan-wechat-layout-lite`（用户级） | 首屏单元/层级代线条/装饰预算/图片证据/反馈路由 | ✅ 已装 |
| 封面与社交卡 | `guizang-social-card-skill`（用户级） | WeChat 21:9+1:1 封面对、小红书图文、Live Photo | ✅ 已装 |
| 图床与发布 | `multi-platform-publishing`（用户级） | 图片自动上传素材库、改写 src 为公网、草稿投递 | ✅ 已装 |
| 伴随 Web 工具 | `html-anything`（项目级 `.audit_htmlanything`） | 流式生成 + 微信 juice 导出 + 知乎公式转图 | ⏸ 保留待用 |

**对 loopsbench 文件的一揽子修复路线**：
冻结正文 → `guizang` 出 WeChat 封面对（灭掉本地路径封面）→ `xiaowan` 图片证据表（6 张示意改为「证明句」或预拼/删）→ `gzh-design(recsys-blue)` 出基础 HTML + 移动端覆盖（去线条/装饰预算/首屏/断行）→ `multi-platform-publishing` 上传图床灭裂图 → 若要发知乎或含公式，用 `html-anything` 的 juice/eeimg 导出。

---

## 四、残留说明（无害，需手动清）
- 审计克隆 `.audit_guizang/`、`.audit_htmlanything/` 及两个已装 skill 目录里的 `.git`，因沙箱 safe-delete 拦截未能自动删除。真正的 skill 已在 `~/.workbuddy/skills/`；这两个 `.audit_*` 临时目录你可在确认后手动删除。
- guizang 的商业授权条款仅在你做商业产品集成时才需关注；个人/学术公众号使用不受影响。
