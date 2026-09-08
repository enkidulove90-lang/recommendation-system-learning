# LOOPSBENCH 链路 A · 图片上传 Runbook（multi-platform-publishing）

> 配套 `loopsbench_v2_A_standard.html`（链路 A 标准成品，L0 已通过）。
> 目的：把 7 张本地图经公众号素材库上传，得到 `https://mmbiz.qpic.cn/...` 公网 URL，回填 `<img src>`，方可粘贴发布。

---

## 0. 当前状态（自动执行结论）

| 步骤 | 结果 |
|------|------|
| 重排为链路 A 标准成品 | ✅ `loopsbench_v2_A_standard.html`（7 图、章节编号、关键词下划线、KPI 深蓝、图注 #666、金句块、ZWJ emoji 修正） |
| L0a `validate_gzh_html.py` | ✅ 100 处 span-leaf，0 ERROR |
| L0b `component_lint.py` | ✅ 0 ERROR（仅其它主题库 2 个 WARN，与本篇无关） |
| L0c 图片路径检查 | ⚠️ 7 张仍为本地 `C:/` 路径，**需上传后清零** |
| 图床上传（浏览器桥） | ⛔ **未执行**：无已登录 mp.weixin.qq.com 的 Chrome 会话，且 path A 仅自动传 1 封面 |

---

## 1. 为什么这里不能直接上传

`multi-platform-publishing` 的图床上传依赖 `redbook/infrastructure/wechat_delivery.py::WeChatDraftDelivery`：
- 它驱动 **已登录 mp.weixin.qq.com 的 Chrome 会话**（复用 opencli browser 桥）。
- 本沙箱里 `opencli` 可被运行时解析到（`@jackwener/opencli`），但 **没有该登录会话**（连接器全部 disconnected，无 `redbook-wechat-draft` 浏览器会话）。
- 即便登录，`_upload_cover` 只自动传 **1 张封面**；正文 7 张图需手动在编辑器插入，或扩展 `_fill_body_html` 循环 `upload`。

→ 图床上传是**需要你本人登录态的外部动作**，无法在此沙箱无人值守完成。

---

## 2. 你来完成上传的两种方式

### 方式 A：浏览器桥自动建稿（推荐，需你登录一次）

1. Chrome 打开 https://mp.weixin.qq.com 并扫码/账密登录公众号后台，保持会话。
2. 在本机执行（opencli 已随运行时可用）：
   ```bash
   python -m redbook.automation.paper_to_wechat --paper-id 2608.00267
   ```
   或由 `WeChatPublisher.publish` 走 `WeChatDraftDelivery`：标题 verified 写入 + 正文 innerHTML 注入 + 封面自动上传。
3. 草稿落库后，**在编辑器里把正文 7 张图逐一用「图片」按钮插入**（桥当前仅自动传封面）。
4. 后台肉眼核对草稿 → 群发（自动化只建草稿，不群发）。

> 若要 7 张图也自动上传，需把 `wechat_delivery.py` 的 `_fill_body_html` 扩展为：遍历正文 `<img>`，对每个本地 `src` 走一次 `upload` + 选图回填。属小改造，需要我来做可说一声。

### 方式 B：路径 B 手动粘贴（无需 opencli）

1. 用浏览器打开 `loopsbench_v2_A_preview.html` 核对排版。
2. 打开公众号编辑器 → 逐张用「图片」上传 7 张本地图（位置见下表）→ 得到 mmbiz URL。
3. 复制 `loopsbench_v2_A_standard.html` 正文粘贴进编辑器（文字+样式保留；图片需在编辑器内重新插入到对应位置）。
4. 保存草稿 → 审核 → 发布。

---

## 3. 7 张图位置对照（上传后回填 src）

| # | 当前本地 src | 文中位置 | 类型 |
|---|--------------|----------|------|
| 封面 | `data/parsed/2608.00267/images/728f8cc2...jpg` | 顶部首屏 | 论文真实图（MinerU 提取） |
| 图1 | `wechat_design/illustration/01-scene-background.png` | 背景段后 | 概念插图 |
| 图2 | `wechat_design/illustration/02-framework-method.png` | 01 章节后 | 概念插图 |
| 图3 | `wechat_design/illustration/03-infographic-results.png` | 02 章节后 | 概念插图 |
| 图4 | `wechat_design/illustration/04-comparison-limitation.png` | 04 章节后 | 概念插图 |
| 图5 | `wechat_design/illustration/05-flowchart-practice.png` | 05 章节后 | 概念插图 |
| 图6 | `wechat_design/illustration/06-timeline-ending.png` | 07 章节后 | 概念插图 |

---

## 4. 一次性回填脚本（你上传拿到 mmbiz URL 后）

把 7 个 `https://mmbiz.qpic.cn/...` 填入下方字典，运行即可生成最终可粘贴文件：

```python
import pathlib, re
m = {
  "728f8cc2...": "https://mmbiz.qpic.cn/COVER",
  "01-scene-background": "https://mmbiz.qpic.cn/IMG1",
  "02-framework-method": "https://mmbiz.qpic.cn/IMG2",
  "03-infographic-results": "https://mmbiz.qpic.cn/IMG3",
  "04-comparison-limitation": "https://mmbiz.qpic.cn/IMG4",
  "05-flowchart-practice": "https://mmbiz.qpic.cn/IMG5",
  "06-timeline-ending": "https://mmbiz.qpic.cn/IMG6",
}
html = pathlib.Path("wechat_design/examples/loopsbench_v2_A_standard.html").read_text(encoding="utf-8")
for k, v in m.items():
    html = html.replace(f'"{k}', f'"{v')  # 粗匹配，建议用精确路径替换
out = html
pathlib.Path("wechat_design/examples/loopsbench_v2_A_published.html").write_text(out, encoding="utf-8")
```
