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


import json  # noqa: E402  (used by exclusion test above)
