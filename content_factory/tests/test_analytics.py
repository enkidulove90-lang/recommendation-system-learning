"""Stage 8 分析回收测试：M18 事件 Schema / M17 GA4+Metabase / M8 标题 A/B（v1 合约）。"""

from content_factory.analytics import (
    AnalyticsSpec, EVENT_SCHEMA, TitleABTest, validate_event, InvalidEventError,
    SCHEMA_VERSION, PII_POLICY, EventCollector, FunnelAnalyzer, report_ab,
)

_COMMON = {
    "event_time": "2026-01-01T00:00:00Z", "schema_version": SCHEMA_VERSION,
    "platform": "wechat", "content_id": "cf_x", "session_id": "sid_1",
    "experiment_id": "exp1",
}


def test_event_schema_has_six_events():
    assert set(EVENT_SCHEMA) == {
        "impression", "scroll_depth", "quiz_answer", "play_run", "cta_click", "ab_assign"
    }
    assert EVENT_SCHEMA["scroll_depth"]["fields"]["percent"].startswith("int")
    assert "correct" in EVENT_SCHEMA["quiz_answer"]["required"]


def test_ga4_events_count_and_samples():
    specs = AnalyticsSpec().ga4_events()
    assert len(specs) == 6
    names = {s.name for s in specs}
    assert names == set(EVENT_SCHEMA)
    for s in specs:
        assert s.sample


# ── P1 合约校验 ──────────────────────────────────────────────────────
def test_validate_accepts_valid_event():
    ev = dict(_COMMON, component="title_ab")
    assert validate_event("impression", ev)["component"] == "title_ab"


def test_validate_rejects_missing_required():
    ev = dict(_COMMON)  # impression 还需 component，此处缺失
    try:
        validate_event("impression", ev)
        assert False, "应拒绝缺 component"
    except InvalidEventError:
        pass


def test_validate_rejects_bad_enum():
    ev = dict(_COMMON, percent=40)  # 不在 {25,50,75,100}
    try:
        validate_event("scroll_depth", ev)
        assert False, "应拒绝越界 percent"
    except InvalidEventError:
        pass


def test_validate_rejects_wrong_type():
    ev = dict(_COMMON, block_id="q1", correct="yes")  # correct 应为 bool
    try:
        validate_event("quiz_answer", ev)
        assert False, "应拒绝非 bool correct"
    except InvalidEventError:
        pass


def test_emit_auto_fills_defaults():
    out = AnalyticsSpec().emit([("impression", dict(_COMMON, component="title_ab"))])
    assert out[0]["schema_version"] == SCHEMA_VERSION
    assert "event_time" in out[0]


# ── P2 A/B 稳定随机分配 ─────────────────────────────────────────────
def test_assign_stable_per_session_and_covers():
    a = AnalyticsSpec()
    variants = ["A", "B", "C"]
    # 同 session 稳定
    v1, _ = a.assign_ab_variant("exp", variants, session_id="reader_1")
    v2, _ = a.assign_ab_variant("exp", variants, session_id="reader_1")
    assert v1 == v2
    # 跨 session 覆盖全部变体
    seen = {a.assign_ab_variant("exp", variants, session_id=f"r{i}")[0] for i in range(60)}
    assert seen == {"A", "B", "C"}


def test_assign_emits_valid_ab_assign_event():
    a = AnalyticsSpec()
    _, ev = a.assign_ab_variant("exp", ["A", "B"], session_id="r1")
    # assign_ab_variant 内部已通过 validate_event（否则会抛 InvalidEventError）
    assert ev["variant"] in ("A", "B")
    assert ev["algorithm"] == "hash_stable"
    assert ev["schema_version"] == SCHEMA_VERSION


# ── P9 多臂判定 ─────────────────────────────────────────────────────
def test_multi_arm_declares_winner():
    out = TitleABTest.multi_arm_winner([
        ("control", 100, 1000), ("B", 200, 1000), ("C", 105, 1000),
    ])
    assert out["winner"] == "B"
    assert out["arms"][1]["significant_vs_control"] is True
    assert out["arms"][2]["significant_vs_control"] is False


def test_multi_arm_inconclusive_when_close():
    out = TitleABTest.multi_arm_winner([
        ("control", 100, 1000), ("B", 105, 1000),
    ])
    assert out["winner"] == "inconclusive"


# ── P6 Metabase 看板 ────────────────────────────────────────────────
def test_metabase_has_sql_and_funnel():
    dash = AnalyticsSpec().metabase_dashboard()
    assert dash["source"] == "ga4_events"
    assert dash["version"] == SCHEMA_VERSION
    assert len(dash["cards"]) == 6
    viz = {c["visualization"] for c in dash["cards"]}
    assert "funnel" in viz and "line" in viz
    assert all("native_query" in c for c in dash["cards"])


# ── P5 snippet：会话 + 去重 ──────────────────────────────────────────
def test_snippet_has_session_and_dedup():
    snip = AnalyticsSpec().tracking_snippet(content_id="cf_x", experiment="exp", variants=["A", "B"])
    assert "cfSession" in snip and "localStorage.cf_sid" in snip
    assert "cfSent" in snip          # 去重集合
    assert "ab_assign" in snip       # A/B 钩子
    assert "gtag" in snip and "scroll_depth" in snip


# ── P7 合规策略 ─────────────────────────────────────────────────────
def test_pii_policy_present():
    assert PII_POLICY["session_id"]
    assert "哈希" in PII_POLICY["session_id"]


# ── 既有 M8 两臂测试（保留）──────────────────────────────────────────
def test_ab_winner_declared_only_at_95():
    out = TitleABTest.pick_winner(a_clicks=10, a_impr=1000, b_clicks=200, b_impr=1000)
    assert out["significant"] is True
    assert out["winner"] == "B"
    out2 = TitleABTest.pick_winner(a_clicks=100, a_impr=1000, b_clicks=105, b_impr=1000)
    assert out2["winner"] == "inconclusive"
    assert out["A"]["ci"][1] < out["B"]["ci"][0]


def test_wilson_bounds_valid():
    lo, hi = TitleABTest()._wilson(50, 100)[1], TitleABTest()._wilson(50, 100)[2]
    assert 0.0 <= lo <= 0.5 <= hi <= 1.0


# ── Phase 2 本地-first 分析引擎 ──────────────────────────────────────────
def _ev(name, **kw):
    e = dict(_COMMON, **kw)
    e.setdefault("schema_version", SCHEMA_VERSION)
    e.setdefault("event_time", "2026-01-01T00:00:00Z")
    e["event"] = name
    return e


def _session_events():
    return [
        _ev("impression", session_id="s1", component="t"),
        _ev("scroll_depth", session_id="s1", percent=75),
        _ev("cta_click", session_id="s1", variant="A"),
        _ev("ab_assign", session_id="s1", variant="A", algorithm="hash_stable"),
        _ev("impression", session_id="s2", component="t"),
        _ev("scroll_depth", session_id="s2", percent=50),
        _ev("ab_assign", session_id="s2", variant="B", algorithm="hash_stable"),
    ]


def test_collector_rejects_invalid_and_persists():
    import os
    import tempfile
    c = EventCollector()
    assert c.add("impression", dict(_COMMON, component="x")) is True
    assert c.add("impression", dict(_COMMON)) is False  # 缺 component
    assert c.error_count() == 1
    assert len(c.events()) == 1
    fd, p = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    c._path = p
    assert c.flush() == 1
    c2 = EventCollector(p)
    c2.load()
    assert len(c2.events()) == 1
    os.remove(p)


def test_funnel_and_conversion():
    fa = FunnelAnalyzer(_session_events())
    f = fa.funnel(["impression", "scroll_depth", "cta_click"])
    assert f[0]["count"] == 2 and f[1]["count"] == 2 and f[2]["count"] == 1
    assert fa.conversion("impression", "cta_click") == 0.5


def test_engagement():
    eng = FunnelAnalyzer(_session_events()).engagement()
    assert eng["avg_scroll_percent"] == 62.5
    assert eng["cta_click_rate"] == 0.5


def test_ab_lift_and_report():
    events = _session_events()
    lift = FunnelAnalyzer(events).ab_lift()
    assert "A" in lift and "B" in lift
    rep = report_ab(events)
    assert rep["winner"] in ("A", "B", "inconclusive")


def test_cli_analyze_events_end_to_end(capsys):
    import os
    import tempfile
    from content_factory.cli import main

    events = _session_events()
    fd, p = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    c = EventCollector(p)
    for ev in events:
        c.add(ev["event"], {k: v for k, v in ev.items() if k != "event"})
    assert c.flush() == len(events)

    rc = main(["--analyze-events", p])
    out = capsys.readouterr().out
    assert rc == 0
    assert "已载入" in out
    assert "漏斗" in out
    assert "参与度" in out
    assert "A/B" in out
    os.remove(p)


def test_cli_analyze_missing_file_returns_3():
    import tempfile
    from content_factory.cli import main

    p = tempfile.mktemp(suffix=".jsonl")  # 故意不存在
    assert main(["--analyze-events", p]) == 3
