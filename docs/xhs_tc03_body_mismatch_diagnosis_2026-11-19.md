# TC-03 既有草稿正文 mismatch 诊断（2026-11-19）

## 结论

`s:93a910ec-4bf2-4011-8a7a-e410146bdbbe` 不是 spec 漂移，也不是
`_verify_saved_draft()` 的空白归一化缺陷。它是一次已被平台持久化的正文缺失：
草稿内容缺少完整的「⚠️ 局限」段，而当前 spec 在草稿创建前的提交中已包含该段。

因此验证器的失败结论正确；不得通过放宽比较或覆盖旧草稿来关闭 TC-03。

## 只读证据

- 复核命令：`python -m redbook.cli note 2611.17921 --verify --draft-id s:93a910ec-4bf2-4011-8a7a-e410146bdbbe`
- 返回：`body_ok=false`、`topics_ok=true`、`pdf_ok=true`；见
  `data/workflow_state/2611.17921/acceptance/t3_reverify_2026-11-19.json`。
- 同一登录态下以 IndexedDB `image-draft` 的只读事务读取该草稿：实际 `desc`
  缺失局限段，而三个话题实体及 PDF 元数据均存在。
- `git log --follow -- redbook/notes/2611.17921.yaml` 表明该 note 于
  `c1c4db86` 创建时已包含局限段；草稿保存发生在其后的 checkpoint
  `2026-11-18T16:52:31Z`。因此排除"草稿保存后才修改 spec"。
- 去除全部空白后，`expected in actual` 仍为 `false`；逐行 diff 见
  `data/workflow_state/2611.17921/acceptance/t3_body_diff_2026-11-19.diff`。

## 归因与下一步

根因边界定位在写入路径或平台正文序列化：提交给校验器的当前正文有 756 个字符，
持久化草稿正文有 734 个字符，并在 PDF/话题成功的同时丢失局限段。现有证据不能
进一步区分编辑器填充、保存组件或平台序列化的具体责任点；在没有一个明确批准的
隔离金丝雀前，不应猜测性修改生产逻辑。

这是执行计划 T3 未列出的第三种归因分支。建议后续以独立、明确批准的金丝雀做
最小复现：保存含唯一哨兵局限段的草稿，立即只读回查；只有复现后才以 TDD 修正
填充/保存路径。原草稿不修改、不删除，且不公开发布。
