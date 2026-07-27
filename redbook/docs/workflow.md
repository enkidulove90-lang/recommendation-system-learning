# 论文解析 → 小红书发布 完整工作流

## 概述

从论文 PDF 解析到小红书帖子发布的端到端工作流，支持自动提取论文内容、生成摘要、选择架构图并发布到小红书。

## 目录结构

```
redbook/
├── docs/
│   └── workflow.md          # 本文档
├── scripts/                 # 工具脚本
│   ├── inject_cookies.py    # 从 Chrome 提取小红书 Cookie
│   ├── save_cookies.py      # 手动保存 Cookie
│   ├── login_qr.py          # 扫码登录（Playwright 浏览器）
│   ├── playwright_browser.py # Playwright 浏览器封装（camoufox 替代）
│   ├── setup_camoufox.py    # 注册本地 camoufox 浏览器
│   ├── publish_paper.py     # 发布脚本（基于旧版 xhs-cli + Playwright）
│   ├── redbook_bot.py       # 完整自动化 bot（搜索+爬取+发布）
│   ├── fetch_target_post2.py # 爬取目标用户帖子
│   └── fetch_tencent_post.py # 搜索特定帖子内容
├── tests/                   # 测试脚本
│   ├── smoke_test.py        # 冒烟测试（登录/搜索/whoami）
│   ├── verify_login.py      # 验证登录状态
│   ├── test_creator_dns.py  # DNS 解析测试
│   ├── test_ip_access.py    # IP 直连测试
│   └── test_publish_page.py # 发布页面连通性测试
└── xhs-cli/                 # xhs-cli 源码（本地安装版）
```

## 环境要求

- **Python 3.8+**
- **xhs-cli**（已随 xiaohongshu-cli 安装）: `pip install xiaohongshu-cli`
- **camoufox 浏览器**: 本地路径 `C:\Users\xu.yan1\workspace\camoufox-152.0.4-beta.28-win.x86_64\`
- **小红书账号**: LoveForever (小红书号 27214398832)

## 关键技术选型

| 组件 | 选择 | 原因 |
|------|------|------|
| CLI 工具 | xiaohongshu-cli v0.6.4 | 使用**逆向 HTTP API**，不需要浏览器访问 `creator.xiaohongshu.com` |
| Cookie 管理 | `~/.xiaohongshu-cli/cookies.json` | 扁平格式 `{"a1": "...", "web_session": "..."}` |
| 图片选择 | 论文解析目录 `data/parsed/` | 从 `content.json` 识别架构图（非公式图） |
| 帖子格式 | 仿"乌萨奇今天读paper了吗" | Motivation→贡献→核心设计→实验→来源→#标签 |

## 工作流步骤

### 1. 登录认证

**方法 A: 手动 Cookie 注入（推荐）**

在 Chrome 中登录 `xiaohongshu.com`，F12 → Application → Cookies 获取 `a1` 和 `web_session` 值：

```bash
# 保存 Cookie
python scripts/save_cookies.py

# 或手动创建 cookies.json
mkdir -p ~/.xiaohongshu-cli
echo '{"a1":"你的值","web_session":"你的值"}' > ~/.xiaohongshu-cli/cookies.json
```

**方法 B: QR 码扫码登录**

```bash
python scripts/login_qr.py
```

### 2. 验证登录

```bash
xhs status
xhs whoami
```

预期输出：
```
👤 LoveForever
│ Red ID  │ 27214398832                │
│ User ID │ 694d197a000000002b0043dc   │
```

### 3. 冒烟测试

```bash
python tests/smoke_test.py
```

验证项：Cookie 文件存在 → 登录状态有效 → whoami → 搜索功能正常。

### 4. 爬取目标帖子（参考格式）

```bash
# 搜索目标用户的帖子
python scripts/fetch_tencent_post.py
```

该脚本搜索"乌萨奇今天读paper了吗"发布的"腾讯：端到端强化多模态视觉思维链"帖子，提取标题、正文格式、标签等信息作为参考模板。

### 5. 准备论文内容

论文数据位于项目根目录的 `data/` 下：

```
data/
├── parsed/
│   └── <arxiv_id>_<论文中文名>/
│       ├── <uuid>_origin.pdf          # 原始 PDF
│       ├── <arxiv_id>_content.json    # 解析内容（含图片标注）
│       ├── <arxiv_id>_layout.json     # 布局信息（图片→页码映射）
│       └── images/                    # 提取的图片
└── summaries/
    └── <arxiv_id>_<论文中文名>_summary.md  # AI 生成的论文摘要
```

**选择架构图（非公式图）的方法：**

1. 从 `content.json` 找到 `"type": "image"` 的元素
2. 查看对应 `image_caption` 或 `page_aside_text`
3. 优选 Figure 1-3（框架图、对比图、案例图）
4. 排除含大量 `equation_interline` 的页面

本次发布选用的 5 张图片：

| 图片 | 内容 | 页码 |
|------|------|------|
| `98edc66...jpg` | Figure 1: MMEACR vs 传统 Agent 架构对比 | Page 0 |
| `e02c05b...jpg` | Figure 2: MMEACR 双轨架构总览 | Page 3 |
| `6edeb0d...jpg` | Figure 3: 记忆演化 Case Study | Page 6 |
| `2c78718...jpg` | Figure 6: 结构化查询模板 | Page 11 |
| `fb67018...jpg` | Figure 8: Prompt 模板 | Page 12 |

### 6. 发布帖子

**使用 xiaohongshu-cli 的 API 模式（推荐）：**

```bash
xhs post \
  --title "标题（≤20字）" \
  --body "正文（emoji + 链接 + 空行分段）" \
  --images "图片1.jpg" \
  --images "图片2.jpg" \
  --topic "推荐系统" \
  --topic "LLM" \
  --topic "论文分享"
```

关键点：
- `--topic` 创建**蓝色可点击**的话题标签（比正文 `#` 更有效）
- `--body` 中的 URL（arxiv、github）会自动转为可点击链接
- Emoji 直接写在 body 文本中即可正常显示

此命令通过 HTTP API 直接调用创作中心，**不需要浏览器访问 `creator.xiaohongshu.com`**，绕过了网络限制。

**使用旧版 xhs-cli 的浏览器模式（需要 camoufox）：**

```bash
python scripts/publish_paper.py
```

## 帖子格式模板

两种模板，根据内容类型选择。

### 模板 A：单篇论文深度解读

> 适用：一篇论文详细介绍。参考「符号看象限Ai」(166赞/211藏/81分享)、「三无者也」(393藏/175分享)。

**标题公式：**

```
[会议/期刊]+[录取率/排名]｜[一句话卖点]+[先河/首次/SOTA/突破]
```

示例：`ICML26Top2.2%｜VLA隐式思维链先河`、`ICLR2026中南大学｜ConCM持续学习新框架`

标题关键词库：`先河` `首次` `突破` `SOTA` `新范式` `开源` `即插即用` `Oral` `Spotlight`

**正文模板：**

```
🎓 [1段，3-5句：问题背景+痛点，口语化制造冲突]
   "当前XX模型普遍面临一个尴尬：..."
   "更关键的是，...根本没法用语言描述清楚。"
   "所以现有方法要么不做XX，要么做得又慢又笨。"
   "[方法名]算是第一个系统性把「XX」引入XX的工作。"

✨ [2-3句：核心亮点，用数字制造冲击]
   "比SOTA强出14%？"
   "在10个真实任务上，分别高出13%、14%和14%。"
   "一句话：又准又快。"

🧠 [3-5个bullet：方法拆解，技术深度 + 可读性]
   "隐式CoT：把视觉、点云、本体感知压缩成连续隐序列..."
   "MoT双系统：低频Reason Expert做时空推理，高频Action Expert跑闭环..."
   "训练策略：用Open-X 400K轨迹预训练，SFT阶段余弦相似度监督..."

📊 [1-2句：实验效果，只列最亮眼的数字]
   "Amazon Fashion域：N@1 ↑45.45%，推理时间 ↓16%。"

💡 [3个可探索的方向，给读者「带走的价值」]
   方向一：[一句话描述]
   方向二：[一句话描述]
   方向三：[一句话描述]

arxiv 🔗：https://arxiv.org/abs/XXXX.XXXXX
github 🔗：https://github.com/xxx/xxx（如有）
📎 原文 PDF：https://arxiv.org/pdf/XXXX.XXXXX
```

**语言风格对照：**

| ❌ 平庸（论文翻译腔） | ✅ 爆款（中文互联网风格） |
|---------------------|--------------------------|
| 提出MMEACR框架，通过双轨记忆架构... | 现有LLM推荐Agent有个尴尬的问题：只读文本不看图。更致命的是... |
| 在三个数据集上显著超越基线 | 比AgentCF高出45.45%？Fashion域直接拉满 |
| 采用属性引导的记忆演化机制 | 让Agent学会「做对了就记住，做错了就反思」 |
| 实现推荐性能提升 | 又准又快，推理时间还降了16% |
| 为多模态推荐系统提供新范式 | 推荐Agent终于能「看见」商品了 |

---

### 模板 B：综述/多篇汇总

> 适用：综述论文、会议中稿汇总、领域方向盘点。参考「IDEA工作坊」的 `LLM4CO｜大模型求解组合优化问题综述`、`ICML 2026 Tool-Use Agent中稿汇总（一）`。

**标题公式：**

```
[缩写/领域]｜[中文描述]+[综述/汇总/盘点/一览]
```

示例：`LLM4CO｜大模型求解组合优化问题综述`、`ICML26 Agent中稿汇总｜Tool-Use + Multi-Agent 一文打尽`

**正文模板：**

```
📖 [1-2段：领域背景+为什么这个方向重要]
   "组合优化是运筹学与AI的交叉核心问题..."
   "随着LLM的爆发，用大模型求解CO问题成为新范式——即LLM4CO。"
   "本文系统梳理了XX篇论文，按XX个维度分类，并指出XX个可探索方向。"

🗂 分类体系
   [用表格或分点展示论文分类]
   • 类别1（XX篇）：[一句话描述]
     - 代表工作：[论文名] ([会议], 2026) — [一句话亮点]
     - 代表工作：[论文名] ([会议], 2026) — [一句话亮点]
   • 类别2（XX篇）：[一句话描述]
     - 代表工作：[论文名] ([会议], 2026) — [一句话亮点]

🧩 方法论对比
   [用对比表展示不同路线的优劣]
   | 方法路线 | 代表工作 | 优势 | 局限 |
   |---------|---------|------|------|
   | LLM as Optimizer | OPRO, PromptCO | 零样本泛化 | 精度不如专用求解器 |
   | LLM as Heuristic | LLaMoCo, EoH | 即插即用 | 依赖prompt设计 |
   | LLM + Solver | LLM4Solver, TSP-Agent | 精度高 | 推理开销大 |

🔮 可探索的研究方向（必选板块）
   方向一：[方向名]
   [2-3句：为什么值得做 + 当前瓶颈 + 建议切入点]

   方向二：[方向名]
   [2-3句：为什么值得做 + 当前瓶颈 + 建议切入点]

   方向三：[方向名]
   [2-3句：为什么值得做 + 当前瓶颈 + 建议切入点]

   ...（一般 3-5 个方向）

📚 参考论文列表（含链接）
   [1] [标题]. [会议], 2026. arXiv 🔗：https://arxiv.org/abs/XXXX
   [2] [标题]. [会议], 2026. arXiv 🔗：https://arxiv.org/abs/XXXX
   ...

💻 相关 GitHub 仓库
   • https://github.com/xxx/xxx — [简介]
   • https://github.com/yyy/yyy — [简介]

📎 综述原文 PDF：https://arxiv.org/pdf/XXXX.XXXXX
```

**综述类加分项：**
| 要素 | 效果 |
|------|------|
| 论文分类表格/思维导图 | 一眼看完领域全貌 |
| 方法论对比表 | 帮读者快速选型 |
| 可探索研究方向 | **收藏率最高**的板块——给读者「带走的价值」 |
| PDF 附件 | xhs 支持上传 PDF 附件，读者可下载原文 |
| 标签分级标注 | 用 `[ICLR-Oral]` `[NeurIPS-Spotlight]` 前缀区分论文级别 |

---

### 通用格式规则

| 要素 | 做法 | 效果 |
|------|------|------|
| Emoji 段落标题 | `🎓` `✨` `🧠` `📊` `💡` `🔮` | 视觉层次 |
| 段落间空行 | `\n\n` | 避免拥挤 |
| 论文链接 | `arxiv 🔗：https://arxiv.org/abs/XXXX` | 可长按复制打开 |
| 代码链接 | `github 🔗：https://github.com/xxx` | 可长按复制打开 |
| 原文 PDF | `📎 原文 PDF：https://arxiv.org/pdf/XXXX` | 可长按复制下载 |
| 话题标签 | `--topic "推荐系统"` CLI 参数 | **蓝色可点击**超链接 |
| 要点列表 | `•` 或数字开头 | 结构化呈现 |
| 数字冲击 | `↑45.45%` `14倍` `Top 2.2%` | 制造记忆点 |
| 方向/展望板块 | 模板 A 3个方向，模板 B 3-5个 | 提高收藏率 |

### 图片排版要求

- 竖版 **2550×3300** 或 **2100×2996** 像素，适配手机全屏
- **重新排版的信息图**，不要直接截论文 PDF
- 每张图配一句话说明，形成「看图说话」体验
- 优先：架构图 → 对比表 → 效果图 → Case Study
- 避免：公式密集图、文字截图、小尺寸图标

## 常见问题

### Q: `xhs post` 报 `not_authenticated`

检查 Cookie 格式：
- 新版 xiaohongshu-cli 使用 `~/.xiaohongshu-cli/cookies.json`
- 格式为**扁平 JSON**: `{"a1":"...", "web_session":"..."}`
- 旧版 xhs-cli 使用 `~/.xhs-cli/cookies.json`
- 格式为**嵌套 JSON**: `{"cookies": {"a1":"...", "web_session":"..."}}`

### Q: `creator.xiaohongshu.com` 超时

浏览器模式（xhs-cli）需要访问创作中心，但该域名在某些网络环境下不可达。解决方案：
- **推荐**: 使用 xiaohongshu-cli API 模式（`xhs post --title ...`）
- 备选: 用 `--host-resolver-rules` DNS 映射（见 `tests/test_creator_dns.py`）

### Q: camoufox 版本不兼容

本地 camoufox (152.0.4-beta.28) 的版本号超过 MAX_VERSION=1 限制：
- 修改 `camoufox/__version__.py` 中的 `MAX_VERSION = '999'`
- 确保 `browsers/official/stable/version.json` 存在
- 确保 `.0.5_FLAG` 文件存在
- 参考 `scripts/setup_camoufox.py`

### Q: 话题标签不显示 / 只有最后一个生效

**根因**: xiaohongshu-cli v0.6.4 的 `--topic` 选项不支持 `multiple=True`，传多个 `--topic` 时只有最后一个生效。

**修复** (已应用到本地 site-packages)：
编辑 `site-packages/xhs_cli/commands/creator.py`：
1. `@click.option("--topic", multiple=True, ...)` — 添加 `multiple=True`
2. `topic: tuple[str, ...] | None` — 类型改为 tuple
3. 循环处理 `for t in topic: topic_data = client.search_topics(t); topics.extend(...)` 

修复后即可 `--topic "推荐系统" --topic "LLM" --topic "Agent" ...` 全部生效。

### Q: 图片上传失败

- 确保图片路径为绝对路径
- 图片格式支持 jpg/png
- 单张图片不超过 20MB
- 一次最多上传 18 张图片

## 高质量论文下载源（除 arXiv）

| 源 | 适用 | 方式 |
|----|------|------|
| **OpenReview** | ICML/NeurIPS/ICLR | `openreview.net` 直接下载，常有 camera-ready |
| **CVF Open Access** | CVPR/ICCV/ECCV | `cv-foundation.org` 高质量 PDF |
| **ACL Anthology** | ACL/EMNLP/NAACL | `aclanthology.org` |
| **PMLR** | 许多 ML 会议 | `proceedings.mlr.press` |
| **Papers With Code** | 全领域 | `paperswithcode.com` 聚合多源 |
| **Semantic Scholar** | 全领域 | `semanticscholar.org` 提供 PDF 直链 |
| **作者主页** | 任意 | 搜索 `[作者] homepage`，常有 preprint |
| **直接联系作者** | 任意 | Email/Twitter 索要高清 Figure |

推荐优先级：**作者主页 > OpenReview > CVF > arXiv**（后三者通常 PDF 质量递减）

## 高质量图片提取方案

### 问题诊断

当前 `data/parsed/<paper>/images/` 中的图片由 PDF 解析器自动提取，质量取决于源 PDF 分辨率。arXiv PDF 通常质量一般（150-300 DPI），导致截图模糊。

### 方案对比

| 方案 | 质量 | 自动化 | 适用 |
|------|------|--------|------|
| **PyMuPDF (fitz)** | ★★★★ | ✅ | 提取 PDF 内嵌图片，保持原始分辨率 |
| **pdfimages (poppler)** | ★★★★ | ✅ | 命令行提取，无损原图 |
| **Ghostscript 渲染** | ★★★★ | ✅ | `gs -r600` 600DPI 渲染整页 |
| **作者主页 slides/poster** | ★★★★★ | ❌ | 最高清，需手动下载 |
| **OpenReview camera-ready** | ★★★ | ✅ | 通常比 arXiv 版本新 |
| **矢量图提取 (PDF/EPS)** | ★★★★★ | ⚠️ | 无限分辨率，需代码解析 |

### 推荐方案：PyMuPDF 高清提取

```python
import fitz  # pip install PyMuPDF

doc = fitz.open("paper.pdf")
for page_num in range(len(doc)):
    page = doc[page_num]
    # 渲染整页 600 DPI
    pix = page.get_pixmap(dpi=600)
    pix.save(f"page_{page_num}_600dpi.png")

    # 提取内嵌图片
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image["ext"]  # png/jpg
        with open(f"img_page{page_num}_{img_index}.{ext}", "wb") as f:
            f.write(image_bytes)
```

### 图片筛选准则

从提取的图片中筛选帖子配图：
1. **架构图/流程图**（Figure 1-2）→ 必选，展示方法全貌
2. **对比表/结果图**（Table/Chart）→ 支撑性能声明
3. **Case Study** → 展示实际效果
4. ❌ 跳过：公式密集图、文字密集表、小尺寸图标

## 发布记录

| 日期 | 帖子 ID | 论文 | 标题 | 备注 |
|------|---------|------|------|------|
| 2026-07-27 | `6a672624000000000f0111fa` | MixRAGRec (2605.28175) | KDD26｜MixRAGRec多Agent混合专家推荐 | v3：修复--topic多值，6话题全绑定真实ID |
| 2026-07-27 | `6a67203f000000000c015f3e` | MixRAGRec (2605.28175) | KDD26｜MixRAGRec多Agent混合专家推荐 | v2：模板A，仅1个topic(CLI bug) |
| 2026-07-27 | `6a671181000000001102d253` | MMEACR (2607.07108) | 多模态记忆Agent推荐框架 | v2 优化版：emoji + 链接 + topic |
| 2026-07-27 | `6a67066c00000000010336f4` | MMEACR (2607.07108) | 多模态记忆Agent推荐框架 | v1 初版：格式待优化 |
