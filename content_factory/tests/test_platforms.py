"""Stage 6 平台适配测试：platforms.yaml 规则执行。"""

from pathlib import Path

import pytest

from content_factory.platforms import PlatformAdapter, load_platforms

YAML = Path(__file__).resolve().parent.parent / "platforms.yaml"


@pytest.fixture
def adapter():
    return load_platforms(YAML)


def test_xhs_truncates_title_to_20(adapter):
    out = adapter.adapt("xhs", "这是一个明显超过二十个汉字长度的超长小红书标题测试一下", "lead")
    assert len(out["title"]) <= 20


def test_wechat_strips_emoji_when_forbidden(adapter):
    out = adapter.adapt("wechat", "🎓 我们提出 RADAR 框架", "lead")
    assert "🎓" not in out["title"]


def test_hn_forces_statement_no_question(adapter):
    out = adapter.adapt("hn", "推荐系统为什么需要异步检索？", "lead")
    assert not out["title"].endswith("？")
    assert not out["title"].endswith("?")


def test_missing_platform_uses_default(adapter):
    out = adapter.adapt("unknown_platform", "任意标题", "lead")
    assert out["title"] == "任意标题"
