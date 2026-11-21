"""Sentinel paper pool acceptance (TC8-TC12, TC16)."""
from __future__ import annotations

import threading

import pytest

from redbook.sentinel.paper_pool import (
    InvalidPoolTransition, PaperPool, load_exclusions,
)


@pytest.fixture()
def pool(tmp_path) -> PaperPool:
    return PaperPool(tmp_path / "state" / "orchestration.sqlite")


def _add(pool: PaperPool, cid: str, arxiv_id: str = "", doi: str = "") -> dict:
    return pool.add_candidate(canonical_id=cid, arxiv_id=arxiv_id,
                              doi=doi, title=f"paper {cid}")


def test_add_candidate_unique_canonical_id(pool):  # TC8
    first = _add(pool, "2506.23485")
    assert first["added"] is True and first["reason"] == ""
    second = _add(pool, "2506.23485")
    assert second["added"] is False and second["reason"] == "duplicate"
    with pool._connection() as connection:
        row = connection.execute(
            "SELECT canonical_id, status, pending_delivery FROM paper_pool "
            "WHERE canonical_id = '2506.23485'").fetchone()
    assert (row["status"], row["pending_delivery"]) == ("discovered", 1)


def test_exclusion_list_rejected_with_reason(pool, tmp_path):  # TC9
    exclusion_file = tmp_path / "exclusions.json"
    exclusion_file.write_text(json.dumps(["2601.00001"]), encoding="utf-8")
    exclusions = load_exclusions(exclusion_file)
    result = pool.add_candidate(canonical_id="2601.00001",
                                arxiv_id="2601.00001",
                                exclusions=exclusions)
    assert result == {"added": False, "reason": "excluded",
                      "canonical_id": "2601.00001"}


def test_site_exclusion_schema_and_missing_file_fail_closed(tmp_path):
    exclusion_file = tmp_path / "exclusions.json"
    exclusion_file.write_text(json.dumps({"excluded_ids": ["2504.00678"]}), encoding="utf-8")
    assert load_exclusions(exclusion_file) == {"2504.00678"}
    exclusion_file.unlink()
    import pytest
    with pytest.raises(FileNotFoundError):
        load_exclusions(exclusion_file)


def test_duplicate_id_or_doi_is_idempotent(pool):  # TC10
    _add(pool, "aaa", arxiv_id="2601.11111", doi="10.1000/x")
    again_by_doi = pool.add_candidate(canonical_id="bbb", doi="10.1000/x")
    assert again_by_doi["added"] is False
    assert again_by_doi["canonical_id"] == "aaa"  # idempotent hit


def test_invalid_transition_rejected(pool):  # TC11
    _add(pool, "c1")
    with pytest.raises(InvalidPoolTransition):
        pool.set_status("c1", "published")  # discovered -> published is illegal


def test_pending_fifo_take_order(pool):  # TC12
    for index, cid in enumerate(["late-b", "early-a", "mid-c"]):
        pool.add_candidate(canonical_id=cid)
        # discovered_at ordering: force distinct timestamps via direct update
        with pool._connection() as connection:
            connection.execute(
                "UPDATE paper_pool SET discovered_at = ? WHERE canonical_id = ?",
                (f"2026-11-21T10:0{index}:00+00:00", cid))
    taken = pool.take_pending(limit=3)
    assert [entry.canonical_id for entry in taken] == ["early-a", "late-b", "mid-c"]
    assert all(entry.status == "queued" for entry in taken)


def test_take_pending_is_atomic_across_consumers(pool):  # TC16
    for index in range(5):
        _add(pool, f"paper-{index}")
    results: list[list[str]] = []
    lock = threading.Lock()

    def consume() -> None:
        entries = pool.take_pending(limit=10)
        with lock:
            results.append([e.canonical_id for e in entries])

    threads = [threading.Thread(target=consume) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    all_ids = [cid for batch in results for cid in batch]
    assert sorted(all_ids) == sorted(f"paper-{i}" for i in range(5))
    assert len(all_ids) == len(set(all_ids))  # no paper taken twice


def test_platform_claims_are_independent_for_the_same_paper(pool):
    _add(pool, "arxiv:2601.00003", arxiv_id="2601.00003")

    homepage = pool.take_pending_for_platform("homepage")
    xiaohongshu = pool.take_pending_for_platform("xiaohongshu")

    assert [entry.canonical_id for entry in homepage] == ["arxiv:2601.00003"]
    assert [entry.canonical_id for entry in xiaohongshu] == ["arxiv:2601.00003"]
    assert pool.take_pending_for_platform("homepage") == []
    assert pool.platform_delivery_status("arxiv:2601.00003", "homepage") == "queued"
    assert pool.platform_delivery_status("arxiv:2601.00003", "xiaohongshu") == "queued"
    with pool._connection() as connection:
        global_status = connection.execute(
            "SELECT status FROM paper_pool WHERE canonical_id = 'arxiv:2601.00003'"
        ).fetchone()["status"]
    assert global_status == "discovered"


def test_export_pending_candidates_is_read_only_and_excludes_claimed_rows(pool):
    _add(pool, "arxiv:2601.00001", arxiv_id="2601.00001", doi="10.1/one")
    _add(pool, "arxiv:2601.00002", arxiv_id="2601.00002", doi="10.1/two")
    with pool._connection() as connection:
        connection.execute(
            "UPDATE paper_pool SET discovered_at = ? WHERE canonical_id = ?",
            ("2026-11-21T10:00:00+00:00", "arxiv:2601.00001"),
        )
        connection.execute(
            "UPDATE paper_pool SET discovered_at = ? WHERE canonical_id = ?",
            ("2026-11-21T10:01:00+00:00", "arxiv:2601.00002"),
        )
    pool.take_pending(limit=1)

    exported = pool.export_pending_candidates()

    assert exported == [{
        "canonical_id": "arxiv:2601.00002",
        "arxiv_id": "2601.00002",
        "doi": "10.1/two",
        "title": "paper arxiv:2601.00002",
    }]
    with pool._connection() as connection:
        states = [tuple(row) for row in connection.execute(
            "SELECT canonical_id, status FROM paper_pool ORDER BY canonical_id"
        ).fetchall()]
    assert states == [
        ("arxiv:2601.00001", "queued"),
        ("arxiv:2601.00002", "discovered"),
    ]


def test_homepage_export_excludes_candidates_with_completed_homepage_leg(pool):
    _add(pool, "arxiv:2601.00004", arxiv_id="2601.00004")
    pool.take_pending_for_platform("homepage")
    for state in ("parsed", "summarized", "composed", "staged", "SAVED_UNVERIFIED", "VERIFIED", "published"):
        pool.set_platform_status("arxiv:2601.00004", "homepage", state)

    assert pool.export_pending_candidates() == []


import json  # noqa: E402  (used by exclusion test above)
