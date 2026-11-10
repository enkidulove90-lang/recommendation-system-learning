"""content_spec 冻结口径单元测试（2026-10-28 验收标准）。

覆盖：Hook 14/15/20/21；有/无 venue；alias 未收录；年份缺失告警；
标题软超长告警；7 段缺段/空段/乱序；正文含 # 与 Markdown；超长/超短正文通过。
"""
from __future__ import annotations

import unittest

from redbook.services.content_composer import compose_content
from redbook.services.content_spec import (
    SECTION_HEADERS,
    HashtagInBodyError,
    MarkdownInBodyError,
    TemplateSectionMissing,
    TitleHookLengthError,
    VenueAliasUnregistered,
    hook_weight,
    validate_body,
    validate_title,
)


def _seven_body(**overrides: str) -> str:
    contents = {
        "📌 解决什么问题": "生成式推荐冷启动没信号",
        "✨ 创新点/贡献": "非对称梯度边界",
        "🧪 Benchmark": "Amazon Beauty",
        "⚙️ 实验条件": "Qwen3-8B，单卡",
        "📊 效果": "论文报告：冷启动召回 0.326→0.619",
        "📎 arXiv": "https://arxiv.org/abs/2601.21452",
        "💻 GitHub": "https://github.com/example/sage",
    }
    contents.update(overrides)
    return "\n\n".join(f"{header}\n{contents[header]}" for header in SECTION_HEADERS)


class HookLengthTests(unittest.TestCase):
    def test_hook_weight_counts_only_alnum(self) -> None:
        self.assertEqual(hook_weight("只换优化器，冷启动召回翻倍！"), 12)
        self.assertEqual(hook_weight("abc 123 !! ✨"), 6)

    def test_hook_below_minimum_fails(self) -> None:
        with self.assertRaises(TitleHookLengthError):
            validate_title(None, None, "a" * 14)

    def test_hook_boundaries_pass(self) -> None:
        self.assertEqual(validate_title(None, None, "a" * 15), "a" * 15)
        self.assertEqual(validate_title(None, None, "a" * 20), "a" * 20)

    def test_hook_above_maximum_fails(self) -> None:
        with self.assertRaises(TitleHookLengthError):
            validate_title(None, None, "a" * 21)


class TitleVenueTests(unittest.TestCase):
    def test_no_venue_title_is_bare_hook(self) -> None:
        title = validate_title(None, None, "a" * 15)
        self.assertEqual(title, "a" * 15)
        self.assertNotIn("【", title)

    def test_bare_hook_with_padding_over_budget_fails(self) -> None:
        # 15-20 有效字通过，但加 emoji 后总显示字符超 20 → 硬失败
        with self.assertRaises(TitleHookLengthError):
            validate_title(None, None, "a" * 18 + "✨✨✨✨")

    def test_venue_with_year_gets_prefix(self) -> None:
        title = validate_title("RecSys", 2026, "偏好是一个盒子")
        self.assertTrue(title.startswith("【RecSys 2026】"))

    def test_venue_lookup_is_case_insensitive(self) -> None:
        self.assertTrue(validate_title("recsys", 2026, "偏好是一个盒子").startswith("【RecSys 2026】"))

    def test_unregistered_venue_fails(self) -> None:
        with self.assertRaises(VenueAliasUnregistered):
            validate_title("NotARealVenue", 2026, "偏好是一个盒子")

    def test_missing_year_warns_but_passes(self) -> None:
        with self.assertLogs(level="WARNING") as logs:
            title = validate_title("RecSys", None, "偏好是个盒子")
        self.assertTrue(title.startswith("【RecSys 年份未披露】"))
        self.assertTrue(any("年份未披露" in message for message in logs.output))

    def test_prefix_counts_into_20_char_budget(self) -> None:
        title = validate_title("RecSys", 2026, "偏好不是一个点")
        self.assertEqual(title, "【RecSys 2026】偏好不是一个点")
        self.assertEqual(len(title), 20)

    def test_prefix_over_budget_fails_hard(self) -> None:
        with self.assertRaises(TitleHookLengthError):
            validate_title("NeurIPS", 2026, "a" * 20)
        # 13 + 8 = 21，恰好超预算一个字
        with self.assertRaises(TitleHookLengthError):
            validate_title("RecSys", 2026, "偏好不是一个点了")

    def test_prefixed_hook_ignores_15_20_rule(self) -> None:
        # 前缀消耗预算后，Hook 可以短于 15 有效字
        self.assertEqual(validate_title("KDD", 2025, "冷启别硬猜"), "【KDD 2025】冷启别硬猜")

    def test_empty_hook_with_prefix_fails(self) -> None:
        with self.assertRaises(TitleHookLengthError):
            validate_title("RecSys", 2026, "")


class BodyStructureTests(unittest.TestCase):
    def test_full_seven_sections_pass(self) -> None:
        validate_body(_seven_body())

    def test_very_long_and_very_short_bodies_pass(self) -> None:
        validate_body(_seven_body(**{"📌 解决什么问题": "长" * 5000, "💻 GitHub": "无"}))
        validate_body(_seven_body(**{"✨ 创新点/贡献": "短"}))

    def test_missing_section_fails(self) -> None:
        body = "\n\n".join(
            f"{header}\n内容" for header in SECTION_HEADERS if header != "⚙️ 实验条件"
        )
        with self.assertRaises(TemplateSectionMissing):
            validate_body(body)

    def test_empty_section_fails(self) -> None:
        with self.assertRaises(TemplateSectionMissing):
            validate_body(_seven_body(**{"📊 效果": ""}))

    def test_out_of_order_sections_fail(self) -> None:
        headers = list(SECTION_HEADERS)
        headers[0], headers[1] = headers[1], headers[0]
        body = "\n\n".join(f"{header}\n内容" for header in headers)
        with self.assertRaises(TemplateSectionMissing):
            validate_body(body)

    def test_hashtag_in_body_fails(self) -> None:
        with self.assertRaises(HashtagInBodyError):
            validate_body(_seven_body(**{"✨ 创新点/贡献": "看 #推荐系统 这个话题"}))

    def test_markdown_in_body_fails(self) -> None:
        with self.assertRaises(MarkdownInBodyError):
            validate_body(_seven_body(**{"📊 效果": "**加粗**不允放"}))


class ComposeContentTests(unittest.TestCase):
    def test_compose_fills_placeholder_and_validates(self) -> None:
        sections = {"📌 解决什么问题": "冷启动", "📎 arXiv": "https://arxiv.org/abs/1"}
        result = compose_content(sections, venue="RecSys", year=2026, hook="偏好不是一个点")
        self.assertIn("原文未披露", result["body"])
        self.assertEqual(result["title"], "【RecSys 2026】偏好不是一个点")
        self.assertEqual([line for line in result["body"].splitlines() if line in SECTION_HEADERS],
                         list(SECTION_HEADERS))

    def test_compose_without_venue_has_bare_hook(self) -> None:
        result = compose_content({}, hook="a" * 15)
        self.assertEqual(result["title"], "a" * 15)
        self.assertNotIn("【", result["body"].splitlines()[0])


if __name__ == "__main__":
    unittest.main()
