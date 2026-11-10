# Repository agent instructions

本仓库用于推荐系统论文解析、摘要、分类与多平台发布。跨 IDE（WorkBuddy / Codex / Claude Code / Cursor）共用同一套仓库内约束；**规则不要写进任何一台机器的用户目录**。

## 路由表

| 任务 | 必读 | 入口 |
|---|---|---|
| 论文 → 小红书草稿 / 发帖 | `.agents/skills/xhs-paper-draft/SKILL.md` → `redbook/docs/xhs-content-spec.md` | `redbook.services.render_post.render_post` |
| 内容规则口径 | `config/xhs_content_rules.yaml`（单一事实源） | `redbook/services/xhs_content_gate.py` |
| 小红书投递实现 | `redbook/infrastructure/xiaohongshu_delivery.py` | `OpenCliXiaohongshuDelivery.deliver` |
| 链路历史诊断 | `docs/publishing-pipeline-diagnosis.md` | — |

## 硬性约束（小红书论文帖）

1. **内容只从 `render_post(platform, summary, figures)` 生成**。`compose-post` 是它的薄封装，`PublicationPackage` 是纯投递载体，两者都不自行生产正文。
2. 不要再新建 `build_xhs_draft_<name>.py` 手写 `BODY`，不要再直接调 `PersonaPostComposer().compose()` 当入口。历史上两条独立内容路径曾让两台机器产出的草稿差异极大。
3. 发布闸门五条：正文纯文本、≤1000 字、必须有「局限」段、话题在白名单内、`metadata.visual_review` 有真实目检记录。改口径只改 `config/xhs_content_rules.yaml`。
4. 只存草稿不公开发布；话题绑定成平台真实实体；PDF 附件在存草稿前完成。
5. `redbook/services/content_spec.py` 是 2026-10-28 冻结的 7 段结构口径（明确不限字数），与发布闸门是两层契约，**不要为加字数上限去改它**。

## 通用注意

- Windows 环境下 native 命令请显式传仓库绝对路径；Git Bash 里 `git -C /c/...` 会失败，用 `git -C "C:/..."`。
- 根目录 `.gitignore` 含 `*.json`，新增配置文件若需入库请用 `.yaml` 或显式加白名单例外。
- 入库前扫 `ntn_` / `sk-` / `LEETCODE_SESSION` / `csrftoken` 等密钥特征；`.env` 永不入包。
- 验证命令见 `redbook/docs/xhs-content-spec.md` §7。
