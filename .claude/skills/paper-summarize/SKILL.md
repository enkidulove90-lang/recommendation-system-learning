---
name: paper-summarize
description: Deprecated compatibility pointer. Route paper parsing/summary tasks to the repository's canonical paper-summarize skill under .agents/skills/.
status: deprecated
---

# 已废弃：仅作路由指针

论文下载与标准化 Summary 任务先读仓库根 `AGENTS.md`，再读 `.agents/skills/paper-summarize/SKILL.md`。唯一解析入口是 `python main.py`（crawl/parse/summarize 子命令），按该技能的 8 必填区块格式产出 Summary。

本文件不提供可执行的解析步骤。原文完整保存在 `.agents/skills/paper-summarize/SKILL.md`（规范正文，可执行入口以仓库根 AGENTS.md 路由表为准）。
