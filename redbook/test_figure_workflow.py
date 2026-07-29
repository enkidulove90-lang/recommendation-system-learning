from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from redbook.services.arxiv_source import ArxivSourceImageExtractor
from redbook.services.figure_retrieval import FigureRetrievalService, MineruCaptionIndex
from redbook.services.persona_composer import PersonaCatalog, PersonaPostComposer


class FigureWorkflowTests(unittest.TestCase):
    def test_caption_is_attached_to_all_preceding_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            markdown = Path(folder) / "paper.md"
            markdown.write_text(
                "## Method\n![a](images/a.png)\n![b](images/b.png)\nFigure 2: Architecture overview.\n",
                encoding="utf-8",
            )
            metadata = MineruCaptionIndex.build(markdown)
        self.assertEqual(metadata["a.png"]["figure_id"], "Figure 2")
        self.assertEqual(metadata["b.png"]["caption"], "Architecture overview.")

    def test_source_collector_prefers_original_assets_and_records_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "source"
            figures = root / "figures"
            figures.mkdir(parents=True)
            Image.new("RGB", (1200, 800), "white").save(figures / "architecture.png")
            Image.new("RGB", (400, 300), "white").save(root / "logo.png")
            (root / "main.tex").write_text(
                "\\begin{figure}\\includegraphics{figures/architecture}\\caption{System architecture overview}\\end{figure}"
                "\\begin{tikzpicture} x \\end{tikzpicture}", encoding="utf-8"
            )
            result = ArxivSourceImageExtractor().collect(root, Path(folder) / "out")
            manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
        self.assertEqual(len(result.images), 2)
        self.assertTrue(result.tikz_detected)
        self.assertTrue(manifest[0]["preferred_directory"])
        self.assertEqual(manifest[0]["caption"], "System architecture overview")

    def test_quality_gate_rejects_small_or_extreme_aspect_assets(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            markdown = root / "paper.md"
            markdown.write_text("", encoding="utf-8")
            Image.new("RGB", (1800, 1200), "white").save(root / "good.png")
            Image.new("RGB", (1600, 200), "white").save(root / "wide.png")
            selected, candidates, _ = FigureRetrievalService().select(markdown, root)
        self.assertEqual([Path(item.path).name for item in selected], ["good.png"])
        self.assertFalse(next(item for item in candidates if item.path.endswith("wide.png")).eligible)

    def test_persona_changes_structure_without_losing_source_links(self) -> None:
        summary = """# 测试论文\n\n## 主要贡献\n解决冷启动推荐的对齐问题。\n\n## 方法论\n使用双塔检索和重排序。\n\n## 实验结果\n在两个公开基准上优于基线。\n\n## 对推荐系统的借鉴价值\n可迁移到新用户表征。\n"""
        composer = PersonaPostComposer()
        coach = composer.compose(summary, "2607.00001", "study_coach", "https://github.com/example/repo")
        auditor = composer.compose(summary, "2607.00001", "evidence_auditor")
        self.assertIn("① 问题", coach.body)
        self.assertIn("证据链", auditor.body)
        self.assertIn("https://arxiv.org/abs/2607.00001", coach.body)
        self.assertIn("GitHub：暂无官方代码", auditor.body)
        self.assertIn("不可外推", coach.generation_prompt)
        self.assertIn("research_basis", coach.generation_prompt)
        self.assertEqual(coach.persona_id, "study_coach")
        self.assertIn("success_signal", PersonaCatalog().load("study_coach").strategy)
        self.assertNotEqual(coach.title, auditor.title)
        self.assertGreaterEqual(len(PersonaCatalog().list()), 6)

    def test_missing_official_code_avoids_reproduction_persona(self) -> None:
        summary = "# 示例\n\n## 主要贡献\n\n一个可验证方法。\n\n## 核心方法\n\n组合模块。\n\n## 实验结果\n\n平均分提升。"
        draft = PersonaPostComposer().compose(summary, "2607.00002", "implementation_reviewer")
        self.assertEqual(draft.persona_id, "research_translator")
        self.assertEqual(draft.requested_persona_id, "implementation_reviewer")
        self.assertIn("无官方代码", draft.persona_selection_reason)
        self.assertNotIn("复现判断", draft.body)
        self.assertIn("核心亮点", draft.body)


if __name__ == "__main__":
    unittest.main()
