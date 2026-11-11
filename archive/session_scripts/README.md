# 归档：会话一次性脚本（2026-11-10）

这里共 12 个 `_*.py`，全部是某次会话里「用完就丢」的临时脚本：硬编码
`C:/Users/xu.yan1/.workbuddy/projects/...jsonl` 绝对路径、各自重写一遍解析逻辑、
输出再落到根目录 `_*.txt`。**勿执行**，能力已并进后端。

| 归档文件 | 后端替代 |
|---|---|
| `_dump_calls.py`、`_extract2.py`、`_extract3.py`、`_extract4.py`、`_extract5.py`、`_extract_session.py`、`_scan2.py`、`_scan_session.py` | `redbook/scripts/session_inspect.py`（会话 JSONL → 可读文本 / 用户问题 / 工具调用） |
| `_gatebox_clip.py` | `redbook/services/figure_crop.py::crop_figure_by_caption` |
| `_gatebox_card.py` | `redbook/services/cards.py` |
| `_fix_body.py` | `redbook/notes/<slug>.yaml` 的 `body: |-`（正文只改 spec，不改脚本） |
| `_republish_unipinrec.py` | `redbook/scripts/xhs_drafts.py`（先发新稿、确认成功、再删旧稿） |

后端运行记录另见 `redbook/infrastructure/run_log.py`，根目录 `_*.py` 已被 `.gitignore` 拦下。
旧的发布脚本（`build_xhs_draft_*.py`）在 `archive/xhs_drafts/`，与本目录不是同一批。
