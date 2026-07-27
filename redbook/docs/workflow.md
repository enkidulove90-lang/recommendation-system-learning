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
  --title "多模态记忆Agent推荐框架" \
  --body "正文内容..." \
  --images "图片1.jpg" \
  --images "图片2.jpg" \
  ...
```

此命令通过 HTTP API 直接调用创作中心，**不需要浏览器访问 `creator.xiaohongshu.com`**，绕过了网络限制。

**使用旧版 xhs-cli 的浏览器模式（需要 camoufox）：**

```bash
python scripts/publish_paper.py
```

## 帖子格式模板

仿照"乌萨奇今天读paper了吗"的帖子风格：

```
Motivation
[问题背景，1-2段]

贡献：
[核心贡献，1-2段]

核心设计：
🔹 要点1
🔹 要点2
🔹 ...

实验：
[数据集 + 关键指标]

来源：arXiv <id> | 作者：<机构列表>

#推荐系统 #LLM #多模态 #Agent #论文分享 #AI
```

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

### Q: 图片上传失败

- 确保图片路径为绝对路径
- 图片格式支持 jpg/png
- 单张图片不超过 20MB
- 一次最多上传 18 张图片

## 发布记录

| 日期 | 帖子 ID | 论文 | 标题 |
|------|---------|------|------|
| 2026-07-27 | `6a67066c00000000010336f4` | MMEACR (2607.07108) | 多模态记忆Agent推荐框架 |
