"""端到端冒烟：离线 DAG 跑通 + digest 非空且含高信号论文；空推防护。"""
import os

from paper_monitor.models import Paper
from paper_monitor.notify.digest import render_digest
from paper_monitor.orchestrator import run_ingest


def _set_env(tmp_path):
    os.environ["PM_OFFLINE_FIXTURE"] = "1"
    os.environ["PM_TOPIC_FILTER"] = "0"          # 离线 fixture 保证全保留
    os.environ["PM_DB_PATH"] = str(tmp_path / "pm.sqlite")
    os.environ["PM_DELIVERY"] = "file"
    os.environ["PM_DIGEST_PATH"] = str(tmp_path / "digest")


def test_e2e_offline_dag(tmp_path):
    _set_env(tmp_path)
    summary = run_ingest(sources=["openalex", "arxiv", "huggingface", "s2"], limit=3)
    assert summary["raw"] >= 4                      # 4 源各 ≥1
    assert summary["merged"] >= 4
    assert summary["kept"] >= 1
    assert summary["digest_empty"] is False         # 防静默空推
    assert "file" in summary["delivery"]
    # digest 文件应存在且非空，且含高 upvotes 论文（hf fixture）
    digest_file = tmp_path / "digest" / "digest_*.md"
    import glob
    files = glob.glob(str(digest_file))
    assert files, "digest 文件未生成"
    content = open(files[0], encoding="utf-8").read()
    assert "Daily Digest" in content
    assert "👍" in content or "upvotes" in content or "⭐" in content


def test_empty_digest_returns_none():
    assert render_digest([]) is None
    assert render_digest([Paper(title="x")]) is not None
