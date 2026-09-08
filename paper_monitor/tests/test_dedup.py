"""去重测试：同一 DOI 三种 ID 表达归并为 1；跨源 overlap。"""
from paper_monitor.ingest.base import build_paper
from paper_monitor.process.dedup import cross_source_overlap, dedup


def test_three_id_expressions_merge_to_one():
    # 设计文档§5：同一 DOI 的 OpenAlex ID / arXiv ID / DOI 三种表达 → 1 条
    p_oa = build_paper(source="openalex", title="Same Paper",
                       openalex_id="https://openalex.org/W1", doi="10.1000/abc")
    p_arx = build_paper(source="arxiv", title="Same Paper",
                        arxiv_id="2401.00001", doi="10.1000/abc")
    p_doi = build_paper(source="openalex2", title="Same Paper", doi="10.1000/abc")
    out = dedup([p_oa, p_arx, p_doi])
    assert len(out) == 1
    m = out[0]
    # 跨源信号补全
    assert m.arxiv_id == "2401.00001"
    assert m.id == "https://openalex.org/W1"
    assert "arxiv" in m.source and "openalex" in m.source


def test_arxiv_and_oa_merge_without_doi():
    p_oa = build_paper(source="openalex", title="T", openalex_id="https://openalex.org/W9")
    p_arx = build_paper(source="arxiv", title="T", arxiv_id="2401.99999", openalex_id="https://openalex.org/W9")
    out = dedup([p_oa, p_arx])
    assert len(out) == 1
    assert out[0].arxiv_id == "2401.99999"


def test_cross_source_overlap_full():
    a = [build_paper(source="openalex", title="T", doi="10.1/a")]
    b = [build_paper(source="arxiv", title="T", doi="10.1/a")]
    assert cross_source_overlap(a, b) == 1.0


def test_cross_source_overlap_partial():
    a = [build_paper(source="openalex", title="T1", doi="10.1/a"),
         build_paper(source="openalex", title="T2", doi="10.1/b")]
    b = [build_paper(source="arxiv", title="T1", doi="10.1/a"),
         build_paper(source="arxiv", title="T3", doi="10.1/c")]
    # 交集 1 (a), 并集 3 (a,b,c) -> 1/3
    assert abs(cross_source_overlap(a, b) - 1 / 3) < 1e-9
