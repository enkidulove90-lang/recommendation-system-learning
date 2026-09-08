"""主题分类测试：50 样本命中率 + 父 topic 召回。"""
from paper_monitor.ingest.base import build_paper
from paper_monitor.process.classify import classify, matches_topic

REC_SYS = ["recommender systems", "information retrieval", "collaborative filtering",
           "ranking", "personalization", "knowledge graph", "graph neural network",
           "deep learning", "natural language processing", "multimodal"]
NON_REC = ["quantum physics", "astrophysics", "organic chemistry", "marine biology",
           "numismatics", "archaeology", "fluid dynamics", "thermodynamics",
           "botany", "geology"]


def _mk(topic, title="paper"):
    return build_paper(source="t", title=title, topics=[{"display_name": topic, "level": 3}])


def test_keep_recsys_drop_other():
    rec = [_mk(t) for t in REC_SYS]
    non = [_mk(t) for t in NON_REC]
    kept, dropped = classify(rec + non)
    assert len(kept) == len(REC_SYS)
    assert len(dropped) == len(NON_REC)


def test_parent_recall():
    # 叶子 topic 名不直接命中，但父 topic 命中 -> 应保留（父 topic 保召回）
    p = build_paper(source="t", title="x", topics=[
        {"display_name": "sequential recommendation models", "level": 3,
         "parent_display_name": "recommender systems"}])
    assert matches_topic(p)


def test_fifty_sample_accuracy():
    # 构造 50 样本（25 正 / 25 负），逐篇人工标签 = topic 是否在 allowlist 语义内
    labels, papers = [], []
    for t in REC_SYS[:25]:
        papers.append(_mk(t)); labels.append(1)
    for t in NON_REC[:25]:
        papers.append(_mk(t)); labels.append(0)
    kept, dropped = classify(papers)
    kept_set = {id(p) for p in kept}
    correct = sum(1 for p, lab in zip(papers, labels) if (id(p) in kept_set) == bool(lab))
    acc = correct / len(papers)
    # 合成集应 100% 命中
    assert acc == 1.0, f"classify accuracy={acc}"


def test_filter_disabled_keeps_all():
    papers = [_mk("quantum physics"), _mk("recommender systems")]
    kept, dropped = classify(papers, enable=False)
    assert len(kept) == 2 and len(dropped) == 0
