# T4 金丝雀失败记录（2026-11-19）

## 结果

已获授权的 `python -m redbook.cli note 2611.17921 --save-draft` 金丝雀未创建草稿，
返回 `E_TOPIC_UNAVAILABLE`。当前 Creator Center 没有提供精确的「论文分享」可点击
话题芯片，适配器观测到 `available=[]`。

在用户确认登录、Bridge 与三个原话题均可继续后，第二次尝试前的 preflight 与 drafts
登录探针均通过，但话题面板仍返回 `available=[]`。因此停止重试，不将平台临时空面板
误判为内容或认证问题。

## 安全边界

失败发生在 `OpenCliXiaohongshuDelivery._bind_topics()`；执行尚未到达 PDF 附件或
`_save_draft()`。草稿 ID 为空，且 `data/logs/runs.jsonl` 记录本次 `save_draft`
为 `ok=false`。没有公开发布。

T4 不能标记为 accepted，也不能通过把话题写成正文 `#文本` 或绕开真实实体绑定来继续。
下一次尝试前，必须由人工确认 Creator Center 中可用的真实话题实体，或批准对 note spec
的允许话题作相应修改；不得盲目重试。

## 证据

- `data/workflow_state/2611.17921/acceptance/t4_canary_failure_2026-11-19.json`
- `data/workflow_state/2611.17921/acceptance/t4_canary_retry_2026-11-19.json`
- `data/logs/runs.jsonl` 最后一条 `2026-11-19T18:07:16` note/save_draft 失败事件
- T4 前置 preflight：OpenCLI 2.0.2、Bridge 已连接、扩展 1.0.27、`extension_outdated=false`
