# 阶段一验证报告：自动化管线复用 gzh-design recsys-blue 组件库

> 日期：2026-08-12 ｜ 论文样本：2608.00267（LoopsBench）｜ 验证结论：✅ 路线可行

## 一、验证目标

证明 `redbook/` 自动化管线可以复用 `gzh-design` 的 `recsys-blue` 组件库，
产出与手工精排**视觉一致**、且自带 `<span leaf="">` 包裹的公众号 HTML，
从而让「自动化产出质量对齐手工」。

## 二、做了什么

1. **新建 `redbook/automation/gzh_components.py`**（组件库加载 + 参数化）。
   - 单一来源：`wechat_design/components/components.md`（与手工精排同一份文件）。
   - 逐行解析 11 个组件 ```` ```html ```` 块，暴露参数化函数：
     `section_header / one_liner / body_para / body_li / body_bul /
     kpi_cards / limitation / cta / references / cover / figure / hook_title`。
   - 内置与文件**逐字节一致**的 fallback，仅当 md 缺失时启用（实践中 11/11 全部从文件加载）。
2. **改造 `paper_to_wechat.py::render_wechat_html`**：
   - `_h / _box / _p / _li / _bul` 改为委托 `gzh.*`（原硬编码内联样式、无 `<span leaf>`）。
   - 参考文献块改用 `gzh.references(...)`（组件 #11，链接 + 学术声明，自带 leaf）。
   - 其余章节结构（开场钩子→§1–§7→分隔→参考文献）保持不变，仅底层渲染换组件。

## 三、验证结果（2608.00267）

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| `<span leaf>` 包裹 | 0 处（粘贴后样式丢失） | **41 处** |
| `validate_gzh_html` ERROR | 若干（缺 leaf） | **0** |
| `validate_gzh_html` WARNING | 若干 | **0** |
| 禁用标签（`<style>/<div>/class` 等） | 0 | 0 |
| 视觉来源 | 硬编码常量，与手工不一致 | **components.md 组件，与手工同源** |

- 组件库加载：11/11 来自文件（0 个 fallback）。
- 校验器运行：`python .workbuddy/skills/gzh-design/scripts/validate_gzh_html.py <body>` → 退出码 0，无 ERROR/WARNING。

## 四、插值变量缺口记录

- 改造中**未发现**插值变量不匹配：组件模板的占位符
  （`小标题文字`/`核心结论放这里，一句话讲清价值。`/`指标说明`/`图 N｜说明文字…` 等）
  均能被 `render` 函数的实参精确替换。
- 唯一需注意：组件 #5 `body-para` 原始模板是一句示例长文，无法做「插槽替换」，
  故 `body_para()` 改为按「整段文本 + 可选关键词下划线」参数化重建（行为等价，仍合规）。
- `assets` 摘要字段（11 维）已覆盖章节所需全部插槽，无需新增 `assets` 字段。

## 五、遗留 / 下一步

- ✅ 阶段一「最小验证」已通过（实际一步到位扩展到全量组件映射，整体零 ERROR）。
- 🔜 任务 #60 `<span leaf>`：已随组件复用自然解决（41 处全覆盖），可标记完成。
- 🔜 任务 #61 校验门禁：建议把 `validate_gzh_html` 调用嵌入
  `WeChatPublisher.publish()`（草稿生成后、发布前），不通过则阻断发布。
- 🔜 任务 #62 多图配图：正文插图目前仅封面 1 张，下一步用 `gzh.figure` 按章节注入论文原图。
- 🔜 关键词下划线：当前 `body_para(keyword=...)` 已支持，但未自动抽取关键词，
  后续可接论文摘要高频词或人工标注槽位。

## 六、关键文件

- 新增：`redbook/automation/gzh_components.py`
- 改造：`redbook/automation/paper_to_wechat.py`（`render_wechat_html` 委托组件库）
- 验证脚本：`data/logs/verify_wechat_component_mvp.py`
- 产物预览：`publish_preview/wechat/循环工程评估基准.html`
- 正文 body：`data/logs/wechat_body_2608.00267_mvp.html`
