# publish_queue 真实语料 fixture

由 content_factory 真实管线于 2026-11-22 从 `2506.07261`（RADAR，摘要取自
`content_factory/tests/fixtures/sample_summary.json`，后者重建自
`data/summaries/2506.07261_延迟异步检索增强召回_summary.md`）生成，
**非手编数据**。用途：`content_events/tests/test_serve.py` 的
`_copy_real_queue` 语料源——原先依赖仓库根 `publish_queue/`（可再生产物、
未入库且本地已不存在），导致 test_status / dryrun_on_real_corpus 在换环境必挂
（整改计划 P1-2，见 `docs/agent_behavior_remediation_plan_2026-11-22.md`）。

再生方式（如需更换语料）：

```bash
python -c "
import sys, shutil, tempfile
from pathlib import Path
sys.path.insert(0, '.')
tmp = Path(tempfile.mkdtemp())
shutil.copy2('content_factory/tests/fixtures/sample_summary.json',
             tmp / '2506.07261_延迟异步检索增强召回_summary.json')
from content_factory.factory import ContentFactory
f = ContentFactory(root=Path('content_events/tests/fixtures'),
                   summaries_dir=tmp, parsed_dir=Path('data/parsed'))
f.stage(f.run('2506.07261'))
"
```

注意：`content_hash`/`staged_at` 含时间戳，重新生成会改变目录名——
更新后需同步复核 test_serve 断言（`processed >= 1`、`skipped_idempotent >= 1`）
仍成立即可，无硬编码目录名。

`state.json` 为真实管线 dryrun 处理后的状态侧车（2026-11-22 用
`content_events.queue_processor.process_queue(root, 'dryrun', dry_run=True)`
实跑生成后烤回）——`/status` 接口依赖它，缺失时 test_status 返回空列表。
