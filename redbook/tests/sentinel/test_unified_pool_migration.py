import sqlite3

from redbook.sentinel.paper_pool import PaperPool


def test_pool_schema_migrates_existing_rows_without_rebuild(tmp_path):
    path = tmp_path / "old.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE paper_pool (
            canonical_id TEXT PRIMARY KEY, arxiv_id TEXT NOT NULL DEFAULT '', doi TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'daily_discovery',
            status TEXT NOT NULL DEFAULT 'discovered', pending_delivery INTEGER NOT NULL DEFAULT 0,
            platforms TEXT NOT NULL DEFAULT '', discovered_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            reason TEXT NOT NULL DEFAULT '')""")
        db.execute("INSERT INTO paper_pool(canonical_id,title,discovered_at,updated_at) VALUES('arxiv:2601.00001','Paper','t','t')")
        before_columns = {item[1] for item in db.execute("PRAGMA table_info(paper_pool)")}
    pool = PaperPool(path)
    pool._ensure_schema()
    with sqlite3.connect(path) as db:
        row = db.execute("SELECT canonical_id,title,identity_status,admission FROM paper_pool").fetchone()
        columns = {item[1] for item in db.execute("PRAGMA table_info(paper_pool)")}
    assert before_columns <= columns
    assert row == ("arxiv:2601.00001", "Paper", "discovered", "{}")
    assert {"title_zh", "venue_name", "paper_url", "github_url", "published_at", "identity_status", "admission"} <= columns


def test_pool_add_candidate_accepts_unified_snapshot(tmp_path):
    pool = PaperPool(tmp_path / "pool.sqlite")
    class Unified:
        title_zh = "论文"
        venue_name = "RecSys"
        paper_url = "https://arxiv.org/abs/2601.00001"
        urls = {"github": "https://github.com/example/p"}
        published_at = "2026-01-01"
        identity_status = "identity_verified"
        admission = {"homepage": {"state": "eligible"}}
    pool.add_candidate(canonical_id="arxiv:2601.00001", title="Paper", unified=Unified())
    with pool._connection() as db:
        row = db.execute("SELECT title_zh,venue_name,paper_url,github_url,published_at,identity_status,admission FROM paper_pool").fetchone()
    assert tuple(row[:6]) == ("论文", "RecSys", "https://arxiv.org/abs/2601.00001",
                              "https://github.com/example/p", "2026-01-01", "identity_verified")


def test_catalog_sync_updates_only_metadata_columns(tmp_path):
    pool = PaperPool(tmp_path / "sync.sqlite")
    pool.add_candidate(canonical_id="arxiv:2601.00001", title="Paper")
    pool.set_status("arxiv:2601.00001", "queued")
    with pool._connection() as db:
        before = db.execute("SELECT status FROM paper_pool WHERE canonical_id='arxiv:2601.00001'").fetchone()[0]
    changed = pool.sync_catalog_snapshots([{
        "catalog_id": "arxiv:2601.00001", "canonical_id": "arxiv:2601.00001",
        "title_zh": "论文", "venue_name": "RecSys",
        "paper_url": "https://arxiv.org/abs/2601.00001", "identity_state": "identity_verified",
        "admission": {"homepage": {"state": "eligible"}}, "updated_at": "2026-11-21T00:00:00+00:00",
    }])
    assert changed == 1
    with pool._connection() as db:
        entry = db.execute("SELECT status,title_zh FROM paper_pool WHERE canonical_id='arxiv:2601.00001'").fetchone()
    assert entry[0] == before == "queued"
    assert entry[1] == "论文"
