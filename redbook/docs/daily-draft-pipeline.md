# 每日论文草稿：唯一执行链路

唯一的定时入口是 Codex 的 `redbook-daily-paper-draft` 自动任务；唯一的交付适配器是 `redbook.infrastructure.xiaohongshu_delivery.OpenCliXiaohongshuDelivery`。旧 `redbook/scripts/` 中的发布、CDP、PDF 测试脚本只保留作历史排障，不得由定时任务调用。

```text
官方实验室/高校与顶会候选
  → 近期性、venue、实验性、官方 GitHub 四重门控
  → PDF 下载到 data/papers/
  → MinerU 解析到 data/parsed/
  → arXiv 源码高清图优先，PDF 高清渲染兜底
  → persona 文案 + 可点击话题实体
  → OpenCLI 保存图文草稿
  → Browser Bridge CDP 上传同一 PDF 附件
  → 草稿箱复核（标题、图数、话题、PDF 文件名）
```

## 完成门槛

以下任一项失败，任务必须删除本轮不完整草稿并标记失败；不允许以正文 `#` 标签、PDF 外链或模糊截图降级冒充完成：

1. 本地原始 PDF、MinerU Markdown 和结构化布局文件存在；
2. 至少 4 张通过质量门的高清图，优先作者 LaTeX 源码；
3. 官方 GitHub 链接已核验；
4. OpenCLI 成功选择真实话题实体；
5. Browser Bridge CDP 成功将本地 PDF 作为文件组件添加到草稿；
6. 仅保存草稿，禁止自动公开发布。

交付命令仅有一个：

```powershell
python -m redbook.cli save-xhs-draft `
  --draft data/workflow_state/<paper>/research_translator_draft.json `
  --image <高清图1> --image <高清图2> --image <高清图3> --image <详情页> `
  --pdf data/papers/<paper>.pdf `
  --output data/workflow_state/<paper>/delivery_receipt.json
```

命令强制 `draft_only`，并在话题绑定、图片计数或 CDP PDF 上传失败时删除不完整草稿。

## 旧脚本状态

`redbook/scripts/publish*.py`、`cdp_*.py`、`upload_pdf_test.py` 和 `rebuild_july_2026_drafts.py` 是一次性或旧 `xhs-cli` 试验脚本。它们不再是生产入口。新增功能只写入 application / infrastructure / config，并由上述自动任务调用。
