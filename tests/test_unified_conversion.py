from redbook.automation.sources import PaperRecord


def test_discovery_record_converts_to_unified_and_quarantines_agenda_url():
    record = PaperRecord(record_id="recsys:bonsai", title="BONSAI",
        source_records=[{"source_type": "proceedings"}],
        authors=[{"name": "Author", "affiliation": ["Example University"]}],
        venue={"name": "RecSys 2026", "year": 2026, "track": "Research"},
        urls={"landing": "https://recsys.acm.org/recsys26/session-1/",
              "github": "https://github.com/example/bonsai"},
        provenance={"official_github_verification": {"verified": True},
                    "affiliation_verification": {"state": "verified"},
                    "topic_source": "conference_session"})
    unified = record.to_unified()
    assert unified.canonical_id == "recsys:bonsai"
    assert unified.paper_url == ""
    assert unified.venue_name == "RecSys 2026"
    assert unified.urls["github"] == "https://github.com/example/bonsai"
    assert "affiliation" in unified.evidence and "code" in unified.evidence


def test_unverified_github_is_not_promoted():
    record = PaperRecord(record_id="arxiv:2601.00001", title="T",
        source_records=[{"source_type": "arxiv"}], urls={"landing": "https://arxiv.org/abs/2601.00001",
        "github": "https://github.com/example/project"})
    assert record.to_unified().urls["github"] == ""
