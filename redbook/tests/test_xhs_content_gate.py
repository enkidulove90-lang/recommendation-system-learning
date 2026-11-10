"""发布闸门 + 统一内容入口回归测试。

覆盖用户点名的四条需求：
1. compose-post 与 PublicationPackage 收敛到 render_post
2. research_translator 的 problem/method 不再各出现两次
3. 五条铁律（纯文本/字数/局限段/话题白名单/目检标记）在两侧共用
4. 规则数据来自 config/xhs_content_rules.yaml，改配置即改行为
"""
from __future__ import annotations

import unittest
from pathlib import Path

from redbook.automation.publishing import PublicationPackage, XhsPublisher
from redbook.services.persona_composer import PersonaCatalog, PersonaPostComposer
from redbook.services.render_post import render_package, render_post
from redbook.services.xhs_content_gate import (
    ContentSpecError,
    load_rules,
    validate_visual_review,
    validate_xhs_content,
    validate_xhs_post,
)

GOOD_TOPICS = ["论文分享", "人工智能", "推荐系统", "深度学习", "AI"]

SUMMARY = """# SIDRec

## 主要贡献
语义ID只靠内容表征会漏掉协同偏好，SIDRec 把它和点击监督放进同一套端到端框架。

## 创新点
自更新融合让协同视角在训练中持续更新可微量化器。

## 方法论
用已训练推荐模型的物品 embedding 与多模态内容向量共同构造 SID，再用共享专家和任务门控联合优化。

## 实验结果
相对 TransAct，GAUC 最大提升 5.15%，双组件同时移除时 AUC 下降 7.19%。

## 局限
仅报告公开数据集离线结果，未披露线上 A/B 与工业域延迟。

## 借鉴
离散表征要接受下游排序目标的直接监督。
"""


def _compliant_body() -> str:
    return "\n\n".join([
        "🎓 论文在解决什么？\n语义ID只靠内容表征会漏掉协同偏好。",
        "✨ 核心亮点\n自更新融合让协同视角在训练中持续更新。",
        "🧠 方法拆解\n共享专家加任务门控联合优化点击与SID预测。",
        "📊 关键实验\nGAUC 最大提升 5.15%，双组件移除时 AUC 下降 7.19%。",
        "📝 阅读注释\n离散表征要接受下游排序目标的直接监督。",
        "⚠️ 局限\n仅报告公开数据集离线结果，未披露线上实验。",
        "📎 论文与代码\n论文：https://arxiv.org/abs/2611.01136",
    ])


class GateRuleTests(unittest.TestCase):
    def test_compliant_content_passes(self) -> None:
        self.assertEqual(validate_xhs_content(_compliant_body(), GOOD_TOPICS), [])

    def test_markdown_markers_are_rejected(self) -> None:
        for marker in ("**", "__", "~~", "`", "]("):
            with self.subTest(marker=marker):
                errors = validate_xhs_content(_compliant_body() + marker + "x", GOOD_TOPICS)
                self.assertTrue(any("plain text" in item for item in errors))

    def test_hashtag_in_body_is_rejected(self) -> None:
        errors = validate_xhs_content(_compliant_body() + " #推荐系统", GOOD_TOPICS)
        self.assertTrue(any("'#'" in item for item in errors))

    def test_body_over_limit_is_rejected(self) -> None:
        body = _compliant_body().replace("仅报告公开数据集离线结果，未披露线上实验。", "长" * 1100)
        self.assertTrue(any("over the" in item for item in validate_xhs_content(body, GOOD_TOPICS)))

    def test_missing_limitation_section_is_rejected(self) -> None:
        body = _compliant_body().replace("⚠️ 局限\n仅报告公开数据集离线结果，未披露线上实验。",
                                        "📝 补充\n仅报告离线结果。")
        self.assertTrue(any("局限" in item for item in validate_xhs_content(body, GOOD_TOPICS)))

    def test_traffic_topic_outside_allowlist_is_rejected(self) -> None:
        errors = validate_xhs_content(_compliant_body(), ["AI新手村", "AI工具使用", "ai大模型"])
        self.assertEqual(len(errors), 3)
        self.assertTrue(all("allowlist" in item for item in errors))

    def test_academic_persona_topics_are_allowed(self) -> None:
        persona_topics = [topic for persona in PersonaCatalog().list() for topic in persona.topics]
        self.assertEqual(validate_xhs_content(_compliant_body(), persona_topics), [])

    def test_visual_review_marker_is_mandatory(self) -> None:
        self.assertTrue(validate_visual_review({}))
        self.assertTrue(validate_visual_review({"visual_review": "pending"}))
        self.assertEqual(validate_visual_review({"visual_review": "ViewImage 逐张目检 6 张"}), [])

    def test_full_post_gate_checks_title_and_images(self) -> None:
        post = {"title": "合规标题", "body": _compliant_body(), "topics": GOOD_TOPICS,
                "images": ["a.png", "b.png"],
                "metadata": {"visual_review": "ViewImage 逐张目检 2 张"}}
        self.assertEqual(validate_xhs_post(post), [])
        post["title"] = "x" * 21
        self.assertTrue(any("title" in item for item in validate_xhs_post(post)))
        post["title"] = "合规标题"
        post["images"] = []
        self.assertTrue(any("image count" in item for item in validate_xhs_post(post)))

    def test_rules_come_from_repo_config(self) -> None:
        rules = load_rules()
        self.assertEqual(rules["body_max_chars"], 1000)
        self.assertEqual(rules["title_max_chars"], 20)
        self.assertIn("局限", rules["required_section_keywords"])


class PersonaDuplicateSlotTests(unittest.TestCase):
    def test_problem_and_method_each_appear_once(self) -> None:
        draft = PersonaPostComposer().compose(SUMMARY, "2611.01136", "research_translator")
        self.assertEqual(draft.body.count("语义ID只靠内容表征会漏掉协同偏好"), 1)
        self.assertEqual(draft.body.count("共享专家和任务门控"), 1)
        # 旧实现的"核心亮点"曾整段复述"论文在解决什么"与"方法拆解"
        self.assertIn("核心亮点", draft.body)
        self.assertIn("自更新融合", draft.body)

    def test_every_persona_has_a_limitation_section(self) -> None:
        for persona in PersonaCatalog().list():
            with self.subTest(persona=persona.id):
                draft = PersonaPostComposer().compose(SUMMARY, "2611.01136", persona.id)
                self.assertIn("⚠️ 局限", draft.body)
                self.assertEqual(
                    validate_xhs_content(draft.body, draft.topics), [],
                    msg=f"{persona.id} body or topics violate the shared gate",
                )

    def test_existing_figure_workflow_assertions_still_hold(self) -> None:
        """等价覆盖 redbook/test_figure_workflow.py 的 persona 断言（该文件在本机缺 openai）。"""
        composer = PersonaPostComposer()
        coach = composer.compose(SUMMARY, "2607.00001", "study_coach", "https://github.com/example/repo")
        auditor = composer.compose(SUMMARY, "2607.00001", "evidence_auditor")
        self.assertIn("① 问题", coach.body)
        self.assertIn("证据链", auditor.body)
        self.assertIn("https://arxiv.org/abs/2607.00001", coach.body)
        self.assertIn("GitHub：暂无官方代码", auditor.body)
        self.assertNotEqual(coach.title, auditor.title)


class UnifiedEntryPointTests(unittest.TestCase):
    def test_render_post_output_matches_save_xhs_draft_contract(self) -> None:
        post = render_post("xhs", SUMMARY, None, arxiv_id="2611.01136",
                           paper_title="SIDRec: End-to-End Semantic ID")
        for key in ("title", "body", "topics", "images", "metadata"):
            self.assertIn(key, post)
        self.assertLessEqual(len(post["title"]), 20)
        self.assertEqual(post["metadata"]["source"], "render_post")

    def test_render_post_rejects_traffic_topics(self) -> None:
        with self.assertRaises(ContentSpecError):
            render_post("xhs", SUMMARY, None, arxiv_id="2611.01136",
                        topics=["AI新手村", "AI工具使用"])

    def test_render_post_rejects_unknown_platform(self) -> None:
        with self.assertRaises(NotImplementedError):
            render_post("wechat", SUMMARY, None)

    def test_render_package_feeds_xhs_publisher_validation(self) -> None:
        post = render_post("xhs", SUMMARY, ["a.png", "b.png"], arxiv_id="2611.01136",
                           visual_review="ViewImage 逐张目检 2 张")
        package = render_package(
            post, canonical_url="https://arxiv.org/abs/2611.01136",
            links={"paper": "https://arxiv.org/abs/2611.01136",
                   "pdf": "https://arxiv.org/pdf/2611.01136"},
        )
        self.assertIsInstance(package, PublicationPackage)
        self.assertEqual(package.metadata["topics"], list(post["topics"]))
        errors = XhsPublisher(root=Path(".")).validate(package)
        self.assertEqual(errors, [])

    def test_publisher_rejects_package_without_visual_review(self) -> None:
        post = render_post("xhs", SUMMARY, ["a.png"], arxiv_id="2611.01136")
        package = render_package(post, canonical_url="https://arxiv.org/abs/2611.01136",
                                 links={"paper": "p", "pdf": "d"})
        errors = XhsPublisher(root=Path(".")).validate(package)
        self.assertTrue(any("visual_review" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
