"""Stage 7 分发自动化测试：M13/M14/M16 离线 payload + curl 占位。"""

from content_factory.distribution import (
    AppnestABAdapter, BufferAdapter, DevToAdapter, Distributor,
)


def _pkg(title: str = "示例标题") -> dict:
    return {
        "platform": "wechat",
        "title": title,
        "body_markdown": "正文…",
        "links": {"paper": "https://arxiv.org/abs/2506.07261"},
        "metadata": {
            "bound_fields": {"hook": ["problem"]},
            "title_variants": [
                {"text": "标题A", "score": 80}, {"text": "标题B", "score": 75},
            ],
        },
    }


def test_buffer_schedule_builds_payload_and_stub():
    j = BufferAdapter().schedule(_pkg(), at="2026-08-10T09:00:00Z")
    assert j.adapter == "Buffer"
    assert "text" in j.payload and j.payload["scheduled_at"]
    assert "curl" in j.offline_stub


def test_devto_canonical_attaches_source_url():
    j = DevToAdapter().schedule_canonical(_pkg(), canonical_url="https://blog.example.com/x")
    assert j.adapter == "Dev.to"
    assert j.payload["article"]["canonical_url"] == "https://blog.example.com/x"
    assert j.payload["article"]["published"] is False


def test_appnest_assign_emits_ab_event():
    j = AppnestABAdapter().assign("cf_title_ab", ["标题A", "标题B"], _pkg())
    assert j.adapter == "appnest-ab-test"
    assert j.payload["experiment"] == "cf_title_ab"
    assert j.payload["ga4_event"] == "ab_assign"
    assert "<ab-test" in j.payload["web_component"]


def test_distributor_builds_jobs_for_package():
    jobs = Distributor().build(
        [_pkg()], schedule_at="2026-08-10T09:00:00Z",
        ab_experiment="cf_title_ab",
        ab_variants=["标题A", "标题B"],
    )
    adapters = {j.adapter for j in jobs}
    assert "Buffer" in adapters and "Dev.to" in adapters and "appnest-ab-test" in adapters


def test_publish_offline_without_key():
    j = BufferAdapter().schedule(_pkg())
    out = BufferAdapter().publish(j, dry_run=True)
    assert out["mode"] == "offline"
    assert out["stub"]
