# 目标五：多平台分发自动化

> 调研范围：论文解读项目「一键发布到微信公众号 / 小红书 / 知乎」的自动化方案。
> 调研日期：2026-08-12。口径：区分 **官方 SDK/文档**、**合规开源转换工具**、**逆向工程/模拟（标 ⚠️ 风险）** 三类。
> 标注规则：⚠️ = 逆向/模拟，违反平台服务条款（ToS）风险高，仅限自有账号、低频、人工监督使用；🟢 = 官方或合规。

---

## 解决方案设计

### 设计层面 — 统一内容模型 + 发布状态机

**统一内容模型（一次编写，多端适配）**
字段：标题 / 正文（Markdown 源）/ 封面图 / 摘要（≤120字，公众号限制）/ 标签（话题）/ 原文链接 / 平台专属裁剪（字数、图数）。
各平台字段映射：

| 字段 | 微信公众号 | 小红书 | 知乎专栏/回答 |
|------|-----------|--------|-------------|
| 标题 | title（≤64字） | title（**≤20字**硬限） | title（≤120字） |
| 正文 | 内联 HTML（去 JS） | 纯文本+emoji+话题标签 | Markdown（需适配 Draft.js） |
| 封面 | thumb_media_id（永久素材） | 首图（必填，1-9张） | cover_image_id（可选） |
| 摘要 | digest（≤120字） | 无 | 无 |
| 标签 | 无（后台手动） | #话题（≤10） | tags（≤5） |
| 字数上限 | 正文<2万字符 | 正文<1000字（图文） | 长文友好 |

**发布流水线状态机（已在本项目 `content_events/` 落地）**
`intake → render(DTLE双轨) → validated → staged(草稿) → published → feedback`
- 幂等键 `paper_id::platform::content_hash`，同论文同平台仅一个草稿。
- 敏感操作全部 `staged` 后**人工确认**才 `published`，回滚=删草稿/删帖。

### 开发层面 — 适配器模式

- **适配器基类 `PlatformPublisher`**：`publish(content) → {status, url, error}`。本项目已分化为 `WeChatPublisher` / `XhsPublisher` / `ZhihuPublisher`。
- **微信公众号 Browser Bridge（推荐主路径）**：复用已登录 `mp.weixin.qq.com` 的 Chrome 会话（OpenCLI CDP），`browser fill` 写标题、`innerHTML` 注入正文 HTML、官方选择器设封面。经验证比已弃用的 `opencli weixin create-draft`（标题空白/正文像 changelog 的 bug）稳定。
  - *官方 API 路径*（`draft/add` + `freepublish/submit`，需 AppID/AppSecret + IP 白名单）：适合纯自动、无登录态依赖，但**不支持定时发布**且无官方阅读量回采（缺 `user-data` 权限）。
- **知乎 API 封装**：官方 `api.zhihu.com/v4/articles` 需开放平台审核（个人号基本拿不到）；实际可行路径是 **Markdown→知乎格式转换 + 浏览器注入**（见下 md-to-zhihu）。
- **小红书模拟方案**：无公开 API，必须 Cookie + 浏览器自动化。本项目用 `xiaohongshu-cli`（`xhs` 包，反向工程签名）+ OpenCLI CDP 双路径，存草稿后人工发。

### 测试层面

- **沙盒/隔离**：公众号有草稿箱可只存不发布；小红书/知乎用「存草稿」模式验证格式，不真发。
- **自动化回归**：正文 HTML 注入校验（标题非空、图片加载、emoji 不丢）、各平台字数/图数断言（本项目 `wechat_design/dtle/tests` 已验证 13 用例）。
- **敏感操作人工确认**：`staged → 人工 approve → published`；CLI 保留 `--auto` 跳过确认仅供可信环境。

### 运维层面

- **发布任务队列**：本项目 `publish_queue/<hash>/<platform>.json` + `content_events/queue_processor`，支持后台批处理。
- **重试策略**：网络/验证码（XHS `NeedVerifyError`）触发指数退避；XHS 内置 ~1-1.5s 高斯抖动避免风控。
- **限流应对**：公众号 API 有调用配额；知乎 429 读 `Retry-After`；小红书 IP 被封切网络。
- **多账号密钥管理（Vault-like）**：Cookie/AppSecret 用加密存储（如 `xiaohongshu-cli` 的 Fernet、`ZHIHU_COOKIE_KEY` 环境变量、本项目 `~/.xiaohongshu-cli/cookies.json`）。生产建议 HashiCorp Vault / SOPS 统一管理，禁止明文入库。

---

## 真实可用项目列表（已验证）

> 类型图例：🟢 官方/合规　⚠️ 逆向/模拟（标注法律风险）

### A. 微信公众号

| # | 项目 | 类型 | 说明 / 验证点 |
|---|------|------|--------------|
| 1 | **微信公众平台官方 API**（draft/add、freepublish/submit、material/add_material） | 🟢 官方文档 | 合规唯一真路径；需认证服务号/订阅号 + AppID/AppSecret + IP 白名单。**已知缺口：无定时发布 API、无官方阅读量回采**。 |
| 2 | **wechatpy**（messense/wechatpy，pip 安装） | 🟢 官方 API 社区封装 | 封装上述官方接口（草稿/发布/素材/菜单），MIT。合规，但本质仍是官方 API 约束。 |
| 3 | **mdnice / markdown-nice**（mdnice/markdown-nice） | 🟢 合规开源 | Markdown→公众号富文本 HTML，`pip install mdnice` 后 `to_wechat()` 可脚本化。本项目 DTLE 引擎已复用其主题思路。 |
| 4 | **wechat-format**（lyricat/wechat-format） | 🟢 合规开源 | 轻量转换，暗黑模式，代码块优化，1.6k★。 |
| 5 | **doocs/md**（WeChat Markdown Editor） | 🟢 合规开源 | 在线+开源，支持 LaTeX/Mermaid/代码高亮，可自托管。 |

### B. 小红书 ⚠️（无公开 API，全部逆向/模拟）

| # | 项目 | 类型 | 说明 / 风险 |
|---|------|------|------------|
| 6 | **xiaohongshu-cli**（`xhs`，jackwener/SoftHeinrich） | ⚠️ 逆向 API | 反向工程 x-s 签名，`xhs post --title --body --images` 发图文。本项目已集成该包。**风险：违反 XHS ToS，Cookie 7天过期，高频触发验证码/IP 封禁**。 |
| 7 | **xiaohongshu-mcp**（xpzouying） | ⚠️ 浏览器模拟 | MCP 服务器，浏览器自动化模拟真人操作，可连 Claude/Cursor。风险同。 |
| 8 | **xhs_auto_publisher_js**（fzj1214） | ⚠️ Puppeteer | Node+Puppeteer+DeepSeek 全流程发布。 |
| 9 | **jiang-xiaohongshu-crawler**（upJiang） | ⚠️ Puppeteer | 爬虫+舆情，可参考登录态管理。 |
| 10 | **jetwu/xiaohongshu** | ⚠️ 逆向 | 全栈采集器（React+Flask），Cookie 加密存储参考。 |
| 11 | **xhs-cli**（0xranx-agent-kit） | ⚠️ 模拟 | 草稿 Markdown→发布，需创作者中心扫码。 |

### C. 知乎

| # | 项目 | 类型 | 说明 / 风险 |
|---|------|------|------------|
| 12 | **知乎开放平台 API**（api.zhihu.com/v4/articles） | 🟢 官方（受限） | 支持 Markdown 提交、专栏、分析接口。**缺口：开放平台审核极严，个人/小号基本无权限；x-zse-96 签名需前端逆向**。 |
| 13 | **md-to-zhihu**（zhenxuanshi） | 🟢 合规开源 | Markdown→知乎格式 + Playwright 一键发布，主题可配。本项目知乎路径参考。 |
| 14 | **zhihu-auto-skill**（longxiaskill） | ⚠️ 浏览器写 | 双通道：HTTP 读 + 浏览器写（发布/互动），Cookie 加密。 |
| 15 | **PolyPost 知乎适配器**（wxfwxf911） | ⚠️ 逆向签名 | 逆向 x-zse-96（AES-CBC MD5+HMAC），属逆向工程。 |

### D. 跨平台一键发布（混合 API + 模拟）

| # | 项目 | 类型 | 说明 / 风险 |
|---|------|------|------------|
| 16 | **PolyPost**（wxfwxf911 / markrussinovich） | ⚠️ 混合 | 9 平台一键发：有 API 的走 API（Dev.to/Hashnode），无的走 Playwright（XHS/Douyin）。架构参考：Markdown→适配层→平台适配器。MIT。 |
| 17 | **Article Publisher**（clawhub） | ⚠️ Playwright | 知乎/B站/百家号/头条/小红书，扫码登录+Cookie 持久化。 |
| 18 | **AIPlaywright 社媒分发**（tornadoami） | ⚠️ Playwright | 钉钉文档→多平台，AI 生成摘要/封面/标签；公众号仅存草稿。参考其「字数优化+格式清理」逻辑。 |

### E. 统一内容模型 / Headless CMS（一次编辑，多渠道适配输出）

| # | 项目 | 类型 | 说明 |
|---|------|------|------|
| 19 | **Strapi** | 🟢 官方开源 | 最流行 headless CMS，Node.js，REST+GraphQL，内容类型构建器。作内容中枢 + webhook 触发发布。 |
| 20 | **Directus** | 🟢 官方开源 | 包任意 SQL 库，即时 REST/GraphQL + 管理 UI，适合已有数据库。 |
| 21 | **Payload CMS** | 🟢 官方开源 | TS 原生、code-first schema，Next.js 友好。 |
| 22 | **Ghost** | 🟢 官方开源 | 面向发布/邮件/会员，自带 Content/Admin API，最接近「写作→多渠道」场景。 |
| 23 | **Decap CMS** | 🟢 官方开源 | Git-backed，提交即内容，零数据库，适合静态站+Jamstack。 |
| 24 | **KeystoneJS / Webiny** | 🟢 官方开源 | GraphQL 原生 / 无服务器企业级，可作多渠道分发后端。 |

### F. 本项目内部已验证基础设施（🟢 自有，已跑通）

| # | 模块 | 类型 | 说明 |
|---|------|------|------|
| 25 | **redbook/ + multi-platform-publishing skill** | 🟢 内部已验证 | `build_xhs_draft.py`(XHS 存草稿) / `paper_to_wechat.py`(公众号 Browser Bridge) / `cli stage --platform zhihu_answer`。 |
| 26 | **content_events/ 编排层** | 🟢 内部已验证 | 状态机 intake→render→validated→staged→published→feedback，幂等+人工确认+反馈采集。 |
| 27 | **wechat_design/dtle/ 双轨渲染** | 🟢 内部已验证 | 一套 YAML 主题双轨输出（公众号安全内联 HTML / 小红书卡片），13 用例单测。 |

---

## 缺口诚实报告

**1. 平台层硬缺口（无法用开源绕过）**
- **公众号定时发布**：官方 API 无定时发布接口，`freepublish/submit` 立即发。定时只能靠 Browser Bridge 操作后台 UI，或外部 cron 触发发布——稳定性差。
- **公众号阅读量/数据回采**：无普通权限接口，数据监控只能靠后台人工或第三方（如新榜），自动化预警缺失。
- **知乎开放平台权限**：个人号几乎拿不到 `articles` 写权限，生产级知乎自动发布本质上只能走浏览器模拟（⚠️）。
- **小红书**：无任何官方发布入口，自动化=逆向/模拟，封号风险固有，无法消除。

**2. 跨平台统一模型的断点**
- 三平台字段语义差异大（标题 20/64/120 字、正文 纯文本/HTML/Markdown、标签 10/0/5），**没有现成工具能做到零损映射**，必须按平台裁剪（本项目 DTLE 已做双轨，但 XHS 话题派生、知乎标签仍半自动）。
- Headless CMS（Strapi 等）解决「内容中枢+版本」，但**不解决平台适配与发布**，需自建适配器层——它只是 1/3 的方案。

**3. 发布状态监控与回滚（最弱一环）**
- 绝大多数开源工具**无草稿版本管理、无发布后链接自动收集、无错误预警**。本项目 `content_events` 提供了状态机与反馈采集骨架，但「发布后链接回采 + 跨平台统一仪表盘 + 失败自动告警」仍缺：
  - 公众号：发后无 API 取 article_url（需从后台或分享链手动补）。
  - 小红书/知乎：发后 URL 需从账号页/Cookie 会话回读，无标准接口。
  - 建议补：发布成功写 `publish_queue/<hash>/<platform>_result.json`（含 url+publish_time），配一个轻量监控脚本（轮询 429/NeedVerify/SessionExpired + 企微/邮件告警）。

**4. 合规与可持续性风险（必须明示）**
- 小红书、知乎模拟发布均违反各自 ToS，平台随时可改签名/风控导致工具失效（xiaohongshu-cli 已需频繁升级）。**仅建议用于自有账号、低频、人工监督**，切勿批量/营销化。
- 多账号矩阵运营在 XHS 有封号连锁风险，Vault 管密钥解决不了封号，只是不泄露。

**5. 结论**
- 合规可达成的自动化：公众号（官方 API 或 Browser Bridge 存草稿）+ 格式转换（mdnice/doocs）+ 内容中枢（Strapi/Ghost）。
- 必须接受「半自动 + 人工确认」的：小红书、知乎。
- 本项目当前架构（content_events 状态机 + DTLE 双轨 + 三平台适配器 + 存草稿人工发）已是**最务实且合规边界内最优**的组合，缺口主要在「发后监控/回滚/定时发布」三处，建议优先补 `publish_result` 回采与告警。

---

*参考：微信开放文档、wechatpy、mdnice、doocs/md、xiaohongshu-cli、xiaohongshu-mcp、md-to-zhihu、PolyPost、Strapi/Directus/Payload/Ghost/Decap 官方仓库与文档。*
