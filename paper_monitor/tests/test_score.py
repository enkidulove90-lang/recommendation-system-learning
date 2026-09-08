"""打分测试：信号越高分越高；兴趣画像匹配加分。"""
from paper_monitor.ingest.base import build_paper
from paper_monitor.process.score import score_all, score_paper


def test_higher_signals_higher_score():
    low = build_paper(source="t", title="x",
                      influential_citation_count=0, upvotes=0, github_stars=0, cited_by_count=0)
    high = build_paper(source="t", title="x",
                       influential_citation_count=100, upvotes=80, github_stars=500, cited_by_count=200)
    assert score_paper(high) > score_paper(low)
    assert score_paper(low) == 0.0


def test_interest_match_boost():
    rel = build_paper(source="t", title="LLM-based recommendation agent for multimodal sequential data",
                      abstract="sequential user modeling")
    irre = build_paper(source="t", title="a study on cooking pasta recipes")
    assert score_paper(rel) > score_paper(irre)


def test_score_all_assigns_and_orders():
    papers = [
        build_paper(source="t", title="low", influential_citation_count=1),
        build_paper(source="t", title="high", influential_citation_count=90, upvotes=70),
    ]
    score_all(papers)
    assert papers[0].score != 0 or papers[1].score != 0
    assert papers[1].score > papers[0].score
