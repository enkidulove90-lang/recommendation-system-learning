"""摄入 DAG 编排（设计文档§1 数据流）：

  各源并行拉取 → 归一为 Paper → 以 dedup_key 去重 → OpenAlex topics 硬过滤
  → 打分排序 → 入库 → 按兴趣画像重排 → digest 投递 → 引用爆发回写
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .config import Config, get_config, log
from .ingest import get_adapter
from .models import Paper
from .notify import deliver, render_digest
from .process import classify, dedup, rerank, score_all
from .ingest.huggingface_code import enrich_code_links
from .store import SQLiteStore


def run_ingest(
    sources: list[str] | None = None,
    limit: int | None = None,
    since_date: date | None = None,
    config: Config | None = None,
) -> dict:
    cfg = config or get_config()
    sources = sources or ["openalex", "arxiv", "huggingface", "s2"]
    limit = limit or cfg.max_per_source

    # 1) 并行拉取
    log.info("摄入源: %s | limit/源=%d | 离线=%s", sources, limit, cfg.offline_fixture)
    raw: list[Paper] = []
    with ThreadPoolExecutor(max_workers=min(len(sources), 4)) as ex:
        futures = {
            ex.submit(get_adapter(s, config=cfg).fetch, limit, since_date): s
            for s in sources
        }
        for fut in futures:
            src = futures[fut]
            try:
                raw.extend(fut.result())
            except Exception as exc:
                log.warning("[orchestrator] source %s failed: %s", src, exc)
    log.info("原始聚合: %d 篇", len(raw))

    # 2) 去重（跨源合并）
    merged = dedup(raw)
    log.info("去重后: %d 篇", len(merged))

    # 2.5) 代码/模型/数据集关联富集（替换停用的 PWC #13）
    merged = enrich_code_links(merged, cfg)
    log.info("代码关联富集完成: %d 篇", len(merged))

    # 3) 主题硬过滤（OpenAlex topics）
    kept, dropped = classify(merged, enable=cfg.enable_topic_filter, config=cfg)
    log.info("主题过滤: 保留 %d / 剔除 %d", len(kept), len(dropped))

    # 4) 打分 + 重排
    score_all(kept, cfg)
    ranked = rerank(kept)

    # 5) 入库
    store = SQLiteStore(config=cfg)
    n = store.upsert_many(ranked)
    total = store.count()
    log.info("入库: %d 篇 (累计 %d)", n, total)

    # 6) 引用爆发检测
    bursts = store.detect_bursts()

    # 7) digest + 投递（防静默空推）
    digest = render_digest(ranked, bursts=bursts)
    delivery = {}
    if digest:
        delivery = deliver(digest, config=cfg)
    else:
        log.warning("[orchestrator] digest 为空：跳过投递（防静默空推）")

    store.close()
    return {
        "raw": len(raw),
        "merged": len(merged),
        "kept": len(kept),
        "dropped": len(dropped),
        "stored_total": total,
        "top_paper": ranked[0].title if ranked else None,
        "top_score": ranked[0].score if ranked else 0.0,
        "bursts": len(bursts),
        "delivery": delivery,
        "digest_empty": digest is None,
    }
