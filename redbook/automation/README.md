# Redbook automation

六章实现均是本地文件优先，默认不会公开发布。

```powershell
# 第 1 章：将来源 JSONL 写入 inbox/state
python -m redbook.automation.cli --data-root data source-jsonl --name arxiv --input data/fixture.jsonl

# 第 1 章：标准化和去重
python -m redbook.automation.cli --data-root data normalize data/inbox/2026-07-29/arxiv.jsonl

# 第 2 章：离线评分
python -m redbook.automation.cli score --evidence data/evidence.json

# 第 4 章：只生成审核包，不对外发布
python -m redbook.automation.cli --data-root data stage --platform wechat --paper data/paper.json --canonical-url https://example.com/papers/id/

# 第 5 章：导入一份已读取的创作端指标
python -m redbook.automation.cli --data-root data snapshot --note-id NOTE_ID --age-hours 168 --metrics data/metrics.json

# 第 6 章：生成 manifest 和组合候选
python -m redbook.automation.cli manifest --output data/figures/manifest.jsonl data/parsed/paper/images/*.jpg
python -m redbook.automation.cli compose --manifest data/figures/manifest.jsonl --output-dir redbook/assets/composed
```

`compose` 只处理具有同一 Figure/图注证据的 2–4 张高清图；其他图保持原样。平台 `stage` 的输出在 `data/publish_queue/`，需要由平台适配器或人工审核后才可公开。
