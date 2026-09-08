"""PWC(#13) 替换源测试：S2 key 多命名兼容 + Hugging Face 代码关联富集。"""
import os

from paper_monitor.config import Config
from paper_monitor.ingest.base import build_paper
from paper_monitor.ingest.huggingface_code import enrich_code_links


def test_s2_key_env_fallback():
    # 用户配置的环境变量名为 Semantic_Scholar_API_Key，应被识别。
    # 注意：Windows 上 os.environ 大小写不敏感，故不要以不同大小写去 pop 同一变量。
    # 只暂存本测试触碰的少数变量（避免恢复整个超大环境变量报错）。
    keys = ("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY", "Semantic_Scholar_API_Key")
    saved = {k: os.environ.get(k) for k in keys}
    try:
        os.environ["Semantic_Scholar_API_Key"] = "user_provided_key"
        os.environ.pop("S2_API_KEY", None)  # 不同变量，无冲突
        assert Config().s2_api_key == "user_provided_key"
        # S2_API_KEY 仍优先
        os.environ["S2_API_KEY"] = "direct_key"
        assert Config().s2_api_key == "direct_key"
    finally:
        for k in keys:
            if saved[k] is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = saved[k]


def test_enrich_code_links_offline():
    os.environ["PM_OFFLINE_FIXTURE"] = "1"
    papers = [
        build_paper(source="arxiv", title="A", arxiv_id="2401.00001"),
        build_paper(source="openalex", title="B", doi="10.1/x"),  # 无 arxiv_id -> 不富集
    ]
    out = enrich_code_links(papers)
    a = next(p for p in out if p.arxiv_id)
    b = next(p for p in out if not p.arxiv_id)
    assert a.code_count is not None and a.code_count > 0
    assert a.github_repo and "github.com" in a.github_repo
    assert b.code_count is None
    del os.environ["PM_OFFLINE_FIXTURE"]
