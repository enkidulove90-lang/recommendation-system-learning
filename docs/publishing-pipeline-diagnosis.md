# 小红书 + 微信公众号发布链路诊断报告

> 诊断日期：2026-08-06
> 基准分支：experiments（与 phase1 对齐确认：redbook/ 代码在两分支间无差异）

## 一、现有架构全景

### 1.1 redbook/ 模块清单

| 层级 | 模块 | 状态 | 说明 |
|------|------|------|------|
| **domain** | `domain/media.py` | ✅ | WorkflowCheckpoint / WorkflowStage 状态机 |
| **application** | `application/paper_workflow.py` | ✅ | 图片选择工作流（arXiv 源 → PDF 高清回退 → MinerU 兜底） |
| **application** | `application/evidence_pack.py` | ✅ | 开放证据包解析 |
| **application** | `application/paper_detail_card.py` | ✅ | 论文详情卡 |
| **infrastructure** | `infrastructure/xiaohongshu_delivery.py` | ✅ | OpenCLI CDP 草稿投递（含 PDF 附件） |
| **infrastructure** | `infrastructure/publishing/strategy.py` | ✅ | 发布时间策略（Fixed→DataDriven→Hybrid UCB） |
| **infrastructure** | `infrastructure/publishing/scheduler.py` | ⚠️ | 调度器，与 strategy.py 有部分功能重叠 |
| **infrastructure** | `infrastructure/modelscope_vision.py` | ✅ | ModelScope 视觉模型图片审查 |
| **infrastructure** | `infrastructure/paper_sources/` | ✅ | arXiv + OpenReview 论文源 |
| **automation** | `automation/publishing.py` | ⚠️ | PublicationPackage + FilePublisher + render_package |
| **automation** | `automation/scoring.py` | ✅ | 7 维质量评分（QualityScorerV2） |
| **automation** | `automation/scheduling.py` | ✅ | UCB 时间选择 + 事件触发门控 |
| **automation** | `automation/images.py` | ✅ | 图片清单 + 分组 + Pillow 组合 |
| **automation** | `automation/sources.py` | ✅ | JSONL 源 + 去重 |
| **automation** | `automation/feedback.py` | ✅ | FeedbackStore（快照式指标记录） |
| **automation** | `automation/common.py` | ✅ | 共享工具（JSON/JSONL/hash/text） |
| **services** | `services/figure_retrieval.py` | ✅ | 图片选择服务 |
| **services** | `services/persona_composer.py` | ✅ | 6 角色驱动的帖子文案组合 |
| **personas** | 6 个 YAML 角色文件 | ✅ | research_translator, evidence_auditor 等 |
| **mcp** | `mcp/server.py` | ✅ | JSON-RPC MCP 服务器（封装 OpenCLI XHS 命令） |
| **scripts** | 22 个脚本 | ⚠️ | 含旧版 publish_paper.py / redbook_bot.py 等 |
| **xhs-cli** | 内嵌 xhs-cli 工具 + SKILL.md | ✅ | 小红书 CLI（搜索/阅读/发布） |
| **config** | automation.yaml 等 | ✅ | 调度/质量/图片策略配置 |

### 1.2 已发布记录

| 日期 | 平台 | 论文 | 帖子 ID |
|------|------|------|---------|
| 2026-07-27 | 小红书 | MixRAGRec (2605.28175) | `6a672624000000000f0111fa` |
| 2026-07-27 | 小红书 | MixRAGRec (2605.28175) | `6a67203f000000000c015f3e` |
| 2026-07-27 | 小红书 | MMEACR (2607.07108) | `6a671181000000001102d253` |
| 2026-07-27 | 小红书 | MMEACR (2607.07108) | `6a67066c00000000010336f4` |

## 二、小红书发布链路断点诊断

### 2.1 链路应闭合的 6 个环节

```
论文摘要 (data/summaries/*.md)
  → 内容渲染 (persona_composer → PostDraft)
  → 图片选择 (paper_workflow → FigureAsset 列表)
  → 草稿创建 (xiaohongshu_delivery → OpenCLI CDP / xhs post)
  → 人工审核 (草稿箱 → 修改 → 发布)
  → 指标回收 (FeedbackStore → 快照 → 调度优化)
```

### 2.2 实际断点

| 环节 | 代码状态 | 运行时状态 | 断点 |
|------|---------|-----------|------|
| 论文摘要 | ✅ 75 篇 | ✅ 已就绪 | — |
| 内容渲染 | ✅ PersonaPostComposer | ⚠️ 依赖 DeepSeek API | API key 需确认 |
| 图片选择 | ✅ PaperCreationWorkflow | ⚠️ 依赖 arXiv e-print / PDF | 部分论文无 arXiv 源图 |
| 草稿创建-A | `xiaohongshu_delivery.py` OpenCLI CDP | ❌ **未验证** | OpenCLI 未安装或不可用 |
| 草稿创建-B | `xhs post` CLI 命令 | ✅ 已验证可用 | **cookie 可能已过期**（上次 2026-07-27） |
| 人工审核 | ✅ 草稿箱 | ✅ 手动 | — |
| 指标回收 | ✅ FeedbackStore | ❌ **未连接** | 无自动化指标采集脚本 |

### 2.3 双投递路径冲突

当前存在两条并行的草稿投递路径，但未统一：

**路径 A：`xiaohongshu_delivery.py`（OpenCLI CDP）**
- 入口：`cli.py save-xhs-draft` 命令
- 流程：OpenCLI 创建图片草稿 → CDP 绑定话题 → CDP 上传 PDF 附件
- 问题：依赖 `opencli` 二进制（`shutil.which("opencli")` 未安装时 fallback 为 "opencli" 字符串）
- 状态：**代码完整但从未成功执行**（发布记录均通过路径 B）

**路径 B：`xhs post` CLI 命令**
- 入口：`scripts/publish_paper.py` 或手动命令行
- 流程：`xhs post --title ... --body ... --images ... --topic ...`
- 问题：cookie 文件 `~/.xiaohongshu-cli/cookies.json` 可能已过期
- 状态：**已验证可用**，但 `--topic` 多值支持需手动修补 site-packages

### 2.4 内容渲染缺口

`publishing.py` 的 `render_package()` 支持的平台：

| 平台 | render 函数 | 状态 |
|------|-----------|------|
| `x_thread` | ✅ 内联 | 280 字 + 1-4 图 |
| `jike` | ✅ 内联 | 100-220 字 |
| `zhihu_answer` | ✅ 内联 | 800-1500 字 |
| `generic` | ✅ 默认 | Markdown |
| **`xhs`** | ❌ **缺失** | 设计文档有模板，但无 render_xhs() |
| **`wechat`** | ❌ **缺失** | 设计文档有规格，但无 render_wechat() |

小红书文案实际由 `PersonaPostComposer.compose()` 生成（不经过 `render_package`），这造成了**两条独立的内容生成路径**，且格式不统一。

## 三、微信公众号链路缺口

### 3.1 设计文档规格（已定义）

来源：`redbook/docs/design/04-multi-platform-publishing.md`

| 维度 | 规格 |
|------|------|
| 写入路径 | `opencli weixin create-draft`（只创建草稿） |
| 内容形态 | 深度图文 |
| 字数 | 1,200-2,000 字 |
| 结构 | 背景→方法→实验→局限→实践启发 |
| 图片 | 5-7 张 |
| 链接 | 文末统一参考链接 |
| 风控 | 低（草稿先审） |
| 优先级 | P0 |

### 3.2 实现缺口

| 组件 | 状态 | 说明 |
|------|------|------|
| `render_wechat()` | ❌ 未实现 | publishing.py 中无 wechat 渲染分支 |
| `WeChatPublisher` | ❌ 未实现 | 无 stage/publish/metrics 实现 |
| OpenCLI weixin 命令验证 | ❌ 未验证 | `opencli weixin create-draft` 从未在本机执行 |
| 微信公众号 Cookie | ❌ 未配置 | 无公众号登录态 |
| 内容模板 | ⚠️ 设计有 | 设计文档定义了结构但无代码模板 |
| CLI 命令 | ⚠️ 部分 | `automation/cli.py stage --platform wechat` 可生成审核包但不投递 |

### 3.3 Agent-Reach 参考

Agent-Reach 仓库（https://github.com/Panniantong/Agent-Reach）提供了 15 平台的**读取/搜索**能力：
- ✅ 小红书（3 后端：OpenCLI / xiaohongshu-mcp / xhs-cli）
- ✅ Twitter/X、B站、V2EX、Reddit、Facebook、Instagram、YouTube、GitHub、LinkedIn、雪球、小宇宙、RSS、Web
- ❌ **无微信公众号 channel**
- ❌ **无发布/写操作能力**（SKILL.md 明确标注 "NOT for: 发帖/评论/点赞等写操作"）

Agent-Reach 的可借鉴设计：
1. **多后端路由**：`backends` 有序列表 + `active_backend` 探测
2. **Channel base class**：`can_handle(url)` + `check(config)` → (status, message)
3. **SKILL.md 路由表**：用户意图 → 分类 → 详细文档引用
4. **Cookie 安全边界**：不替用户登录、不读取浏览器 Cookie、只接受显式导出

## 四、修复方案

### 4.1 统一发布链路

```
论文摘要 (data/summaries/{aid}_summary.json)
  → render_post(platform, summary, figures)  [新增统一入口]
    → XHS: PersonaPostComposer.compose() [复用现有]
    → WeChat: render_wechat() [新增]
    → 知乎: render_package(zhihu_answer) [复用现有]
  → 图片选择 (PaperCreationWorkflow.prepare_figures) [复用现有]
  → stage(platform, package) [统一 stage 接口]
    → XHS: xhs post / OpenCLI CDP [双路径统一选择器]
    → WeChat: opencli weixin create-draft [新增]
  → 人工审核 (草稿箱)
  → publish (手动触发)
  → metrics_snapshot [FeedbackStore 自动采集]
```

### 4.2 WeChatPublisher 实现方案

```python
class WeChatPublisher(FilePublisher):
    """微信公众号草稿投递器 — 只写入草稿箱，不群发。"""

    def stage(self, package: PublicationPackage) -> dict:
        # 1. validate (标题 ≤ 64 字, 正文非空, 图片 ≤ 9 张)
        # 2. write_json(publish_queue/{paper_id}/wechat.json)
        # 3. return {"ok": True, "status": "staged", ...}

    def publish(self, staged_id: str) -> dict:
        # 调用 opencli weixin create-draft
        # 或 fallback 为本地 HTML 预览
        # 返回草稿 ID
```

### 4.3 内容版本矩阵

| 版本 | 长度 | 图片 | 结构 |
|------|------|------|------|
| `xhs` | 300-700 字 + emoji | 5 张 | 🎓✨🧠📊💡 + #话题 + 链接 |
| `wechat` | 1,200-2,000 字 | 5-7 张 | 背景→方法→实验→局限→实践启发→参考 |
| `zhihu_answer` | 800-1,500 字 | 1-3 张 | 先回答→再论证→来源 |
| `x_thread` | ≤280 字 × 2-5 条 | 1-4 张 | 结论→方法→结果→链接 |

### 4.4 Skill 封装方案

新建 `~/.workbuddy/skills/multi-platform-publishing/`：

```
SKILL.md                      # 主文档：触发词 + 路由表 + 快速命令
references/
  xhs-publishing.md           # 小红书发布详细指南
  wechat-publishing.md         # 微信公众号发布详细指南
  content-templates.md        # 平台内容模板（A/B 两套）
  image-pipeline.md           # 图片选择与合成流水线
```

## 五、风险与依赖

| 风险 | 影响 | 缓解 |
|------|------|------|
| OpenCLI 未安装 | CDP 路径不可用 | 保留 xhs-cli API 路径作为 fallback |
| XHS cookie 过期 | 发布失败 | 添加 cookie 过期检查 |
| 公众号无登录态 | 草稿创建失败 | 先用本地 HTML 预览，手动上传 |
| DeepSeek API 配额 | 文案生成阻塞 | 缓存已生成文案，手动编辑 fallback |
