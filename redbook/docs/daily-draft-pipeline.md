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

内容声明、附件和平台投递均收束到同一篇 note 的单一入口。定时任务只生成并审查本地候选；人工确认后，按顺序执行：

```powershell
python -m redbook.cli note <slug> --validate
python -m redbook.cli note <slug> --stage
python -m redbook.cli note <slug> --save-draft
python -m redbook.cli note <slug> --verify --draft-id <draft-id>
```

`--save-draft` 强制 `draft_only`，并在话题绑定、图片计数或 CDP PDF 上传失败时删除本轮不完整草稿；`--verify` 仅回读校验，不会公开发布。`<draft-id>` 必须取自成功保存的回执。禁止在定时任务中改用旧的低层适配器命令或 `--publish`。

## 金丝雀操作顺序

金丝雀只可使用已通过 venue、公开 PDF、官方 GitHub、高清图片、真实话题实体和 PDF
附件全部门槛的 note，并且必须先取得人工明确授权。全程保持 `draft_only`：先运行
`opencli doctor`，再依次执行 `note <slug> --validate`、`--stage`、`--save-draft` 和
`--verify --draft-id <draft-id>`；最后保存草稿箱截图及 verify 原始 JSON 到
`data/workflow_state/<slug>/acceptance/`。任何一步失败都停止，不得改用 `--publish`。

## 孤儿草稿处置

`python -m redbook.cli note --reconcile` 只读读取平台草稿箱和 SQLite registry，输出
未登记或未验证的 `orphans` 候选，以及 SAVING、VERIFIED、UNCERTAIN 的对账结果；该命令
不会删除平台草稿。操作人须逐条检查候选并取得对应 draft ID 的二次人工批准，才可执行
平台删除；删除后再把 registry 记为 `ROLLED_BACK` 并归档回读和批准证据。不得批量删除，
也不得以 UNKNOWN/UNCERTAIN 结果推断为 mismatch。

## 旧脚本状态

`redbook/scripts/publish*.py`、`cdp_*.py`、`upload_pdf_test.py` 和 `rebuild_july_2026_drafts.py` 是一次性或旧 `xhs-cli` 试验脚本。它们不再是生产入口。新增功能只写入 application / infrastructure / config，并由上述自动任务调用。
