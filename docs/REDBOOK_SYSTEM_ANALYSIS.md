# redbook 自动化论文发布系统 —— 现状分析与研究指南

> 生成时间：2026-07-30 | 分支：phase1

---

## 第 0 章：CLI 工具对比与可用性分析

### 0.1 三个 CLI 工具概览

| 维度 | xhs-cli | xiaohongshu-cli | OpenCLI |
|------|---------|-----------------|---------|
| **安装方式** | pip | pip | npm (需 Node.js ≥20) |
| **语言** | Python | Python | Node.js (TypeScript) |
| **版本** | v0.1.4 | v0.6.4 | v1.8.6 |
| **Stars** | ~2.2k | ~2.2k | ~14k |
| **原理** | Camoufox 浏览器 (Firefox) | 逆向 HTTP API | Chrome CDP (复用浏览器登录态) |
| **认证方式** | Chrome Cookie 提取 / 扫码 | Cookie (a1+web_session) | Chrome 登录会话（无需提取 Cookie） |
| **反检测** | 浏览器指纹 (camoufox) | API 签名 (x-s, x-t) | CDP 级别：webdriver 伪造、插件伪装 |
| **依赖** | camoufox, playwright | httpx, pycryptodome | Chrome Extension + daemon |

### 0.2 主链路：发布笔记

| 步骤 | xhs-cli | xiaohongshu-cli | OpenCLI | 本项目使用 |
|------|---------|-----------------|---------|-----------|
| **登录** | `xhs login` (扫码/Chrome Cookie) | Cookie 文件 | 复用 Chrome 登录态 | OpenCLI + Cookie |
| **上传图片** | `--image` flag | `--images` flag (API: permit → COS PUT) | `--images` + CDP `DOM.setFileInputFiles` | **OpenCLI** ✅ |
| **填标题** | `--title` | `--title` | `--title` + CDP `Input.dispatchKeyEvent` | **OpenCLI** ✅ |
| **填正文** | `--content` | `--body` | positional arg + CDP `insertText` | **OpenCLI** ✅ |
| **话题标签** | ❌ 不支持 | `--topic`（单值，需 patch 修复多值）| `--topics` (逗号分隔) | **OpenCLI** ✅ (已 patch) |
| **发布/草稿** | 直接发布 | 直接发布 | `--draft true` 存草稿 | **OpenCLI** ✅ |
| **PDF 附件** | ❌ | ❌ | ❌ (需 CDP `set-file-input`) | ⚠️ CDP 辅助 |

**结论**：OpenCLI 是唯一支持草稿+多话题的发布工具，但 PDF 附件需 CDP 补足。

### 0.3 副链路

| 功能 | xhs-cli | xiaohongshu-cli | OpenCLI | 评价 |
|------|---------|-----------------|---------|------|
| **搜索笔记** | ✅ `search` | ✅ `search` | ✅ `search` | 三者均可 |
| **读取笔记** | ✅ `read` (HTML解析) | ⚠️ `read` (常失败) | ✅ `note` (CDP) | OpenCLI 最稳定 |
| **用户资料** | ✅ `user` | ✅ `user` | ✅ `user` | 均可 |
| **用户帖子** | ✅ `user-posts` | ✅ `user-posts` | ✅ `user` | 均可 |
| **Feed 推荐** | ✅ `feed` | ✅ `feed` | ✅ `feed` | 均可 |
| **点赞/收藏/评论** | ✅ | ❌ 未测 | ✅ | OpenCLI 最全 |
| **草稿管理** | ❌ | ❌ | ✅ `drafts/draft-delete/draft-clear` | **OpenCLI 独有** |
| **下载图片/视频** | ❌ | ❌ | ✅ `download` | **OpenCLI 独有** |
| **创作者数据** | ❌ | ❌ | ✅ `creator-notes/stats/profile` | **OpenCLI 独有** |
| **删除笔记** | ❌ 不可用 | ❌ 不可用 | ✅ `delete-note` | **OpenCLI 独有** |

### 0.4 实际可用性评分

| 场景 | xhs-cli | xiaohongshu-cli | OpenCLI |
|------|---------|-----------------|---------|
| 发布草稿(文+图+话题) | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 批量操作 | ⭐ | ⭐ | ⭐⭐⭐⭐ |
| 只读操作(搜索/读取) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 自动化集成 | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 反检测可靠性 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

**最终选型**：**OpenCLI 为主，xiaohongshu-cli/API 为辅**。发布走 OpenCLI（草稿+话题），搜索/读取走 xiaohongshu-cli API（更快，不需要浏览器）。

---

## 第 1 章：现状复盘

### 1.1 已实现模块

| 模块 | 功能 | 输入 | 输出 | 状态 | 实现位置 |
|------|------|------|------|------|---------|
| arXiv 检索 | 按关键词/分类搜索 | 分类+关键词 | 元数据列表 | ✅ | `skills/arxiv_searcher.py` |
| PDF 下载 | arXiv PDF 下载 | arXiv ID | PDF 文件 | ✅ | `skills/pdf_downloader.py` |
| MinerU 解析 | PDF 结构化解析 | PDF 文件 | content.json + images/ | ✅ | `skills/pdf_parser.py` |
| DeepSeek 摘要 | 生成论文摘要 | 解析结果 | summary.md | ✅ | `skills/deepseek_summarizer.py` |
| **图片 HD 提取** | arXiv 源码包 → 高清原图 | arXiv ID | images_hd/ | ✅ | `evil-read-arxiv/extract-paper-images` |
| **图片拼接** | ICS/层对比等关联图 2x2/横向合并 | 2张+ 图片 | 拼接图 | ✅ | `redbook/scripts/merge_images.py` |
| **模板A 正文** | emoji+结构化+链接文案 | 摘要 | 小红书正文 | ✅ | 模板内置于 Skill |
| **OpenCLI 发布** | 草稿创建(文+图+话题) | 正文+图片+话题 | 草稿 | ✅ | `opencli xiaohongshu publish --draft` |
| **CDP PDF 上传** | set-file-input 注入 PDF | PDF 文件 | 附件 | ⚠️ | `redbook/scripts/opencli_cdp.py` |
| **MCP Server** | 12 工具 MCP 服务 | MCP 协议 | JSON-RPC | ✅ | `redbook/mcp/server.py` |
| **Skill 文档** | 完整流水线文档 | — | SKILL.md | ✅ | `.claude/skills/redbook-publish/` |

### 1.2 已注册 Skill

```
arxiv-search, metadata-extract, pdf-parse, pdf-download,
deepseek-summarize, citation-collect, graph-build, quality-score,
narrative-generate, graph-visualize, redbook-publish
```

### 1.3 当前瓶颈

1. **数据源单一**：仅依赖 arXiv，无法覆盖顶会正式接收论文（OpenReview/CVF/ACL Anthology）
2. **论文筛选粗糙**：5维度评分中，引用权重、新颖性测度不够精细
3. **发布时间固定**：缺乏数据驱动的发布时间优化
4. **仅支持小红书**：尚未扩展到其他平台（知乎、Twitter、B站）
5. **无反馈闭环**：发布后的互动数据未被用于优化筛选逻辑
6. **PDF 附件半自动**：CDP `set-file-input` 不稳定，需手动补传

---

## 第 2 章：数据源扩展方案

### 2.1 数据源类型（优先级）

| 优先级 | 来源 | 类型 | 采集方式 | 更新频率 |
|--------|------|------|----------|----------|
| **P0** | arXiv API | 预印本 | `arxiv` Python 库 | 实时 |
| **P0** | OpenReview | 顶会论文 | 官方 API (`api.openreview.net`) | 每日 |
| **P1** | CVF Open Access | CV 顶会 | HTML 爬取 `cv-foundation.org` | 会议后 |
| **P1** | ACL Anthology | NLP 顶会 | BibTeX API (`aclanthology.org`) | 会议后 |
| **P1** | Semantic Scholar | 全领域 | REST API (`api.semanticscholar.org`) | 每日 |
| **P2** | Papers With Code | 含代码论文 | REST API | 每日 |
| **P2** | 机构 RSS/主页监控 | 特定机构 | RSS Parser / HTML diff | 每日 |
| **P2** | Twitter/X 学术账号 | 社交媒体 | 需 API (受限) | 实时 |

### 2.2 具体采集方式

#### OpenReview (P0)
```
GET https://api.openreview.net/notes?invitation=<conf>/2026/-/Blind_Submission
```
- ICML/NeurIPS/ICLR 接收论文列表可直接获取
- 返回 JSON：标题、作者、摘要、PDF 链接、评分、decision

#### CVF Open Access (P1)
- 爬取 `https://openaccess.thecvf.com/<conf>2026` 的论文列表页
- 解析 HTML `<dt>` (标题) 和 `<dd>` (作者/PDF 链接)

#### ACL Anthology (P1)
- `https://aclanthology.org/events/<conf>-2026/` 返回 BibTeX
- 无需爬虫，直接解析 BibTeX

#### Semantic Scholar (P1)
```
GET https://api.semanticscholar.org/graph/v1/paper/search?query=<keyword>&year=2026-
```
- 返回论文元数据 + 引用数 + 影响力评分

### 2.3 统一元数据格式 (JSON Schema)

```json
{
  "paper_id": "2607.07108",
  "source_type": "arxiv",
  "source_url": "https://arxiv.org/abs/2607.07108",
  "title": "Seeing and Reflecting: ...",
  "authors": [{"name": "Hao Cong", "affiliation": "Tsinghua University"}],
  "abstract": "...",
  "pdf_url": "https://arxiv.org/pdf/2607.07108",
  "conference": null,
  "year": 2026,
  "keywords": ["recommendation", "multimodal", "agent"],
  "github_url": null,
  "citation_count": 5,
  "influential_citations": 2,
  "fetched_at": "2026-07-30T12:00:00Z"
}
```

### 2.4 去重策略

1. **主键**：优先使用 DOI，其次 arXiv ID
2. **标题模糊匹配**：Levenshtein 距离 < 5 且作者重叠 > 50% 视为重复
3. **合并逻辑**：保留最早出现的元数据，补充后续来源的增量字段（如 GitHub URL、会议信息）
4. **去重优先级**：OpenReview > arXiv > Semantic Scholar（OpenReview 有正式接收信息）

### 2.5 实施计划

**可实施性评分**：⭐⭐⭐⭐ (4/5)
**实施时间估算**：3-4 天
- Day 1：OpenReview API 接入 + 统一元数据 Schema
- Day 2：CVF + ACL Anthology 爬虫
- Day 3：Semantic Scholar API + 去重逻辑
- Day 4：集成测试 + 替换现有 arXiv-only 流程

---

## 第 3 章：质量评分体系优化

### 3.1 新评分维度

| 维度 | 权重 | 数据来源 | 计算方式 |
|------|------|----------|----------|
| **学术影响力** (引用质量) | 25% | Semantic Scholar | 施引文献 Q1 占比 = Q1引用数 / 总引用数 |
| **颠覆性** (Disruption Index) | 15% | Semantic Scholar API | CD₅ = (nᵢ - nⱼ) / (nᵢ + nⱼ + nₖ) |
| **主题新颖性** (绝对) | 20% | arXiv + OpenReview 历史数据 | 1 - (同问题-方法组合出现次数 / 总论文数) |
| **知识演化潜力** | 15% | 解析结果 | 方法改进幅度 (SOTA delta) + 新数据集引入 + 新任务定义 |
| **合作网络** (量化) | 10% | 作者元数据 | log(团队规模) × 机构数量 × 跨国系数 |
| **内容完整度** | 15% | MinerU 解析结果 | PDF 解析完整度 + 摘要质量 + 图片数量 |

### 3.2 综合权重与阈值

```python
WEIGHTS = {
    "academic_influence": 0.25,
    "disruption": 0.15,
    "topic_novelty": 0.20,
    "evolution_potential": 0.15,
    "collaboration": 0.10,
    "content_completeness": 0.15,
}

# 阈值
FULL_ANALYSIS_THRESHOLD = 0.7  # ≥0.7 触发完整分析 + 图谱可视化
BASIC_PUBLISH_THRESHOLD = 0.5  # ≥0.5 自动发布
SKIP_THRESHOLD = 0.3           # <0.3 跳过
```

### 3.3 理论基础

- Disruption Index：Funk & Owen-Smith (2017), *Management Science*
- Q1 引用权重：基于 Scimago Journal Rank (SJR) 分区
- 主题新颖性：基于 TF-IDF + 问题-方法 co-occurrence 矩阵

**可实施性评分**：⭐⭐⭐ (3/5)
**实施时间估算**：5-7 天（主要瓶颈在 Disruption Index 计算和 Semantic Scholar API 集成）

---

## 第 4 章：发布时间优化

### 4.1 基准数据

小红书学术类笔记的流量高峰（基于行业报告）：
- **工作日**：12:00-13:00 (午休) > 20:00-22:00 (睡前)
- **周末**：10:00-12:00 > 15:00-17:00

### 4.2 策略方案

| 策略 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| **A. 固定时间** | 每日固定 12:30 发布 | 简单，可预期 | 未针对本账号优化 |
| **B. 数据驱动** | 基于历史互动数据，计算每小时平均互动率 | 个性化最优 | 需要 ≥30 篇发布积累 |
| **C. 事件触发** | 监控高价值论文上线，30 分钟内发布 | 抢占热点 | 需要实时监控 + 快速处理 |
| **D. 混合策略** | 事件触发(C) + 非高峰期用固定时间(A) | 兼顾热点和稳定性 | 复杂度高 |

**当前推荐**：A→B 渐进式。先固定时间积累 30 篇，再切换到数据驱动。

### 4.3 评估指标

```python
METRICS = {
    "engagement_rate": "(点赞 + 收藏 + 评论) / 曝光量",
    "collection_rate": "收藏数 / 曝光量",  # 论文分享的核心指标
    "comment_depth": "有内容评论数 / 总评论数",  # 过滤 emoji-only
    "follower_conversion": "新增关注 / 曝光量",
}
```

**可实施性评分**：⭐⭐⭐⭐ (4/5)
**实施时间估算**：2-3 天

---

## 第 5 章：多平台发布扩展

### 5.1 平台可行性评估

| 平台 | 技术难度 | 风控风险 | 受众契合 | API/CLI | 优先级 |
|------|----------|----------|----------|---------|--------|
| **知乎** | ⭐⭐ | 低 | ⭐⭐⭐⭐⭐ | 有 Selenium 方案 | **P1** |
| **Twitter/X** | ⭐⭐ | 中 | ⭐⭐⭐ | `twitter-cli` (同作者) | **P1** |
| **B站动态** | ⭐⭐⭐ | 中 | ⭐⭐⭐ | `bilibili-cli` (同作者) | P2 |
| **即刻** | ⭐⭐⭐ | 低 | ⭐⭐ | 无开源工具 | P3 |
| **微信公众号** | ⭐⭐⭐⭐ | 高 | ⭐⭐⭐⭐ | 无公开 API | P3 |

### 5.2 优先扩展：知乎 + Twitter

**理由**：
1. 知乎是学术内容消费主阵地，受众高度匹配
2. Twitter 有 `twitter-cli`（jackwener 作品，与 OpenCLI 同架构），集成成本最低

### 5.3 统一 Publisher 接口

```python
class Publisher(ABC):
    @abstractmethod
    def publish(self, paper: PaperMeta, content: Content, dry_run: bool) -> PublishResult:
        ...
    
    @abstractmethod
    def get_stats(self, post_id: str) -> InteractionStats:
        ...
```

**可实施性评分**：⭐⭐⭐ (3/5)
**实施时间估算**：5-7 天（知乎 + Twitter）

---

## 第 6 章：反馈闭环

### 6.1 数据采集

- **小红书**：OpenCLI `creator-notes` 命令可获取已发布笔记的阅读/点赞/收藏数据
- **存储**：SQLite 本地数据库，`data/feedback/posts.db`

### 6.2 关键指标

```python
FEEDBACK_METRICS = {
    "collection_like_ratio": "收藏数 / 点赞数",  # >1.5 为高质量
    "engagement_rate": "(点赞+收藏+评论) / 阅读量",
    "topic_score": "该话题下所有笔记的平均互动率",
    "institution_score": "该机构论文的平均互动率",
}
```

### 6.3 权重自动调优

```python
def adjust_weights(feedback_history):
    # 如果某机构论文连续 5 篇互动率 > 均值 1.2x，提高 "合作网络" 权重 5%
    for inst in institutions:
        recent = feedback_history.filter(institution=inst).last(5)
        if recent.avg_engagement > global_avg * 1.2:
            WEIGHTS["collaboration"] *= 1.05
```

**可实施性评分**：⭐⭐⭐ (3/5)
**实施时间估算**：4-5 天

---

## 第 7 章：图片智能拼接

### 7.1 已实现

`redbook/scripts/merge_images.py`：
- ✅ 2x2 网格拼接（ICS 机制图）
- ✅ 横向拼接（层稀疏对比）
- ✅ Pillow PIL 实现

### 7.2 待优化

| 功能 | 当前 | 目标 |
|------|------|------|
| 分组判断 | 手动指定文件 | 基于文件名前缀+Caption 相似度自动分组 |
| 布局选择 | 手动选择 2x2/横向 | 自动根据数量选布局 |
| 标题生成 | 无 | 从 Caption 提取 + LLM 润色 |
| 异常处理 | 无 | 尺寸不一致时自动 resize/pad |

### 7.3 分组逻辑

```
1. 文件名前缀匹配 → 同一前缀(如 ics_a, ics_b) = 同组
2. Caption 文本相似度 → Figure X(a)(b)(c) 模式识别
3. 页面相邻位置 → 同一页的连续图片 = 同组
4. 视觉相似度 → 尺寸/纵横比接近的图片
```

### 7.4 布局规则

| 数量 | 布局 | 适用 |
|------|------|------|
| 2 | 横向 1×2 | 对比图、前后结果 |
| 3 | 横向 1×3 | 方法步骤、消融实验 |
| 4 | 2×2 网格 | ICS/机制四阶段 |
| 5-6 | 2×3 网格 | 多数据集对比 |
| 7+ | 3×N 网格 | 大量子图 |

**可实施性评分**：⭐⭐⭐⭐ (4/5)
**实施时间估算**：2-3 天

---

## 附录：完整流水线检查清单

```
□ 1. 论文发现 (arxiv-search / OpenReview API)
□ 2. PDF 下载 (pdf-download)
□ 3. PDF 解析 (pdf-parse → MinerU)
□ 4. 摘要生成 (deepseek-summarize)
□ 5. HD 图片提取 (extract-paper-images)
□ 6. 图片智能拼接 (merge_images.py)
□ 7. 质量评分 (quality-score) → ≥0.5 继续
□ 8. 正文生成 (模板A: emoji + 结构化 + 链接)
□ 9. OpenCLI 草稿创建 (文+图+话题)
□ 10. PDF 上传 (⚠️ 手动 / CDP)
□ 11. 审核发布 (手动)
□ 12. 反馈收集 (creator-notes → 互动数据)
```
