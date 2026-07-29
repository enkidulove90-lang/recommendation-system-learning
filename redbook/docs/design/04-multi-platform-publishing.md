# 第 4 章：多平台发布扩展

## 结论与优先级

先扩展“微信公众号草稿 + 知乎回答”，并同步建设 Notion/GitHub Pages 论文库；不把 B 站动态和即刻作为第一批自动发布目标。前两者覆盖中文深度阅读与搜索问答，且当前 OpenCLI 已有可用的草稿/回答写入能力；Notion/GitHub Pages 提供低风控、可引用的长期归档。

| 平台 | 当前可行写入路径 | 内容形态 | 技术难度 | 风控 | 受众契合 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| 微信公众号 | `opencli weixin create-draft`，只创建草稿 | 深度图文 | 中 | 低（草稿先审） | 高 | P0 |
| 知乎 | `opencli zhihu answer <question> <text>` | 面向问题的回答 | 中 | 中 | 高 | P0 |
| Notion | 官方 API 创建论文库页面 | 可检索知识库 | 低 | 低 | 高 | P0 |
| GitHub Pages/博客 | Markdown + `git push` + Pages Actions | 永久论文页 | 低 | 低 | 高 | P0 |
| X | `opencli twitter post` 浏览器复用登录态 | 英文短帖/线程 | 低 | 中 | 中高 | P1 |
| 即刻 | `opencli jike create <text>` | 中文短动态 | 低 | 中 | 中 | P1 |
| B站动态 | 当前 OpenCLI 无动态发布命令 | 图文动态 | 高 | 高 | 中 | P2 |

## 平台可行性

### 知乎

当前 OpenCLI 支持发布回答，不支持文章/想法的写入命令。因此只在存在高相关问题时创建回答，不把一篇论文机械地投放到多个无关问题。回答正文携带论文结论、方法解释、局限和 PDF/代码链接；配图降为 1–3 张最能说明方法或结果的原图。没有匹配问题时输出“知乎候选包”，不发布。

### X

当前 OpenCLI 可通过已登录浏览器发帖、引用与线程，适合用英文摘要发布：首帖一句结论 + 一张架构/结果图，后续 2–4 条线程解释方法、结果、PDF 与代码。X 的官方 API 要求访问计划并按量计费，因此本项目不接 API；仅使用用户已登录的 OpenCLI 浏览器路径，并先人工审核每篇英文内容。

### B站动态

本机 OpenCLI 的 B 站适配器有评论、收藏、关注等写操作，但没有动态发布命令；公开接口/抓取接口不能等同于发布授权。因此当前不做自动化。链路只生成“B站动态包”（标题、100–180 字摘要、1–3 图、视频脚本提纲），由人工在创作中心发布；后续只有出现官方发布接口或 OpenCLI 写入命令才升级。

### 即刻

本机 OpenCLI 支持 `jike create <text>`，当前按文本动态设计：100–220 字，1 个反直觉结论、1 个论文链接、1 个代码链接。由于现有命令不承诺图片上传，图片不作为必须项。初期每周最多两条，并在公开发布前人工审阅。

### 微信公众号

OpenCLI 可创建公众号图文草稿，适合把小红书的 5 张图扩展为 1,200–2,000 字的深度解读：问题、方法、实验、局限、论文/PDF/代码、原图版权说明。自动化仅到草稿箱；群发/发布保留人工审核。若未来接入官方公众号接口，也仍保留同一“先草稿后发布”的闸门。

### Notion 与博客

Notion 是论文库，不等同社交分发：用官方 API 在数据库下创建页面，并写入 Markdown、结构化元数据和 PDF/代码链接；是否公开页面由 Notion 工作区手动控制。GitHub Pages 则把同一 Markdown 渲染为稳定的公开论文详情页。GitHub Pages 可由推送或 GitHub Actions 工作流自动部署，因此可用作所有平台的规范链接落点。

## 内容版本矩阵

| 版本 | 长度与结构 | 图片 | 链接 |
| --- | --- | --- | --- |
| `xhs` | 300–700 字，emoji 分段、5 张解析图、知识图谱/详情收尾 | 5 张 | 正文保留论文、PDF、代码链接 |
| `wechat` | 1,200–2,000 字：背景→方法→实验→局限→实践启发 | 5–7 张 | 文末统一参考链接 |
| `zhihu_answer` | 800–1,500 字，先直接回答问题，再用论文作证 | 1–3 张 | 文末“来源与复现” |
| `x_thread` | 首帖 ≤ 280 字，后续 2–4 条，每条一个论点 | 1–4 张 | 首帖论文页，末帖 PDF/代码 |
| `jike` | 100–220 字：结论→为什么→链接 | 可选 | 一条规范链接 |
| `notion/blog` | 完整 Markdown + YAML 元数据 + 原始链接 | 所有选中原图 | 永久 canonical URL |

内容生成器不直接生成平台文本；先生成 `paper_card.json`（事实、结论、数字、链接、图号、免责声明），再由 `render_<platform>.py` 渲染。每个平台只可使用这个事实包中的字段，避免不同平台出现不一致或虚构表述。

## 统一 Publisher 接口

```python
class Publisher(Protocol):
    platform: str

    def validate(self, package: dict) -> list[str]:
        """返回阻断错误；不写入平台。"""

    def stage(self, package: dict) -> dict:
        """创建草稿、Notion 页面或本地待发布文件，返回外部 ID/URL。"""

    def publish(self, staged_id: str) -> dict:
        """仅在 review_status=approved 时调用。"""

    def metrics(self, external_id: str) -> dict:
        """读取允许获得的互动数据；无法读取时明确返回 unavailable。"""
```

输入使用 `data/publish_queue/<paper_id>/<platform>.json`，结果写 `data/publish_results/<platform>/<external_id>.json`。`stage` 与 `publish` 是两个独立命令；平台没有草稿能力时，`stage` 只写本地“人工待发布包”，绝不隐式公开发布。

```json
{
  "paper_id": "arxiv:2607.07108",
  "platform": "wechat",
  "canonical_url": "https://<site>/papers/2607-07108/",
  "title": "MMEACR：多模态记忆推荐智能体",
  "body_markdown": "...",
  "image_paths": ["..."],
  "links": {"paper": "...", "pdf": "...", "code": "..."},
  "review_status": "pending",
  "source_attribution": "图表摘自论文，仅作学术解读"
}
```

## 风控与审核

1. 所有新平台默认只 `stage`，不得从定时任务直接调用 `publish`。
2. 同一论文只允许每个平台一个外部草稿；以 `paper_id + platform + content_hash` 幂等，避免重试重复发帖。
3. 任何平台出现登录失效、内容审核提示、图片上传失败或链接被截断时，置为 `needs_review`，不自动重试。
4. X、知乎、即刻的公开发布需要人工审核；公众号只进草稿箱；Notion 与博客可在前 10 篇人工验收无误后自动 stage，公开仍由仓库/工作区的发布设置控制。
5. 不使用互动刷量、批量关注、批量评论或第三方非官方发布 API。

## 首批实施计划

1. 建立 `paper_card.json` 与平台渲染器；先生成但不发布六个版本。
2. 实现 `NotionPublisher.stage` 与 `BlogPublisher.stage`，得到一条稳定 canonical URL。
3. 实现 `WeChatPublisher.stage`，仅写入公众号草稿箱。
4. 实现 `ZhihuPublisher.stage`：先搜索候选问题，人工选择一个问题后才写回答。
5. 运行两周人工审核期；通过后才启用 X/即刻的单篇公开发布，并继续保留频率限制。

## 可实施性

**4/5；预计 3 个工作日。** 第 1 天完成事实包与 Notion/GitHub Pages；第 2 天接公众号草稿与知乎候选问答；第 3 天完成审核状态机、幂等记录和 X/即刻渲染。B站动态不纳入本期开发。

## 依据

- [Notion：Create a page API](https://developers.notion.com/reference/post-page)
- [Notion：2026 Markdown content API 更新](https://developers.notion.com/page/changelog)
- [GitHub Pages：推送或 Actions 发布](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [X Developer Platform：访问计划与按量计费](https://developer.x.com/)
