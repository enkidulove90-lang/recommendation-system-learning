"""Three-tier figure selection: strongest tier first, never the same figure twice.

The gate thresholds are deliberately not exercised here — this test only locks
the *selection* contract (tier order + de-duplication), because the gate itself
is owned by redbook.services.figure_retrieval.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.content_bridge import select_figures_with_fallback  # noqa: E402


def _candidate(figure_id, page, path):
    return SimpleNamespace(figure_id=figure_id, page=page, path=str(path), source="fixture")


class FakeService:
    def __init__(self, catalog):
        self.catalog = catalog

    def select(self, markdown_path, folder, limit=9, source="mineru"):
        picked = list(self.catalog.get(Path(folder).name, []))
        return picked[:limit], picked, {}


class FigureFallbackTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "paper.md").write_text("# t\n", encoding="utf-8")
        for name in ("images", "images_source"):
            (self.base / name).mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_strongest_tier_wins_and_duplicates_are_dropped(self):
        catalog = {
            "images_source": [_candidate("Figure 1", 3, self.base / "images_source/a.png"),
                              _candidate("Figure 2", 4, self.base / "images_source/b.png")],
            "images": [_candidate("Figure 1", None, self.base / "images/a.png"),
                       _candidate("Figure 3", 6, self.base / "images/c.png")],
        }
        with patch("redbook.services.figure_retrieval.FigureRetrievalService",
                   lambda *a, **k: FakeService(catalog)):
            selected, source_dir = select_figures_with_fallback(self.base / "paper.md", None)
        self.assertEqual([item.figure_id for item in selected], ["Figure 1", "Figure 2", "Figure 3"])
        self.assertEqual(source_dir.name, "images_source")

    def test_falls_back_to_mineru_when_higher_tiers_are_empty(self):
        catalog = {"images": [_candidate("Figure 1", 2, self.base / "images/a.png")]}
        with patch("redbook.services.figure_retrieval.FigureRetrievalService",
                   lambda *a, **k: FakeService(catalog)):
            selected, source_dir = select_figures_with_fallback(self.base / "paper.md", None)
        self.assertEqual(len(selected), 1)
        self.assertEqual(source_dir.name, "images")

    def test_returns_empty_when_no_tier_has_an_eligible_figure(self):
        with patch("redbook.services.figure_retrieval.FigureRetrievalService",
                   lambda *a, **k: FakeService({})):
            selected, source_dir = select_figures_with_fallback(self.base / "paper.md", None)
        self.assertEqual(selected, [])
        self.assertIsNone(source_dir)

    def test_page_is_used_when_a_crop_has_no_figure_id(self):
        catalog = {
            "images_source": [_candidate("", 5, self.base / "images_source/a.png")],
            "images": [_candidate("", 5, self.base / "images/a.png"),
                       _candidate("", 7, self.base / "images/b.png")],
        }
        with patch("redbook.services.figure_retrieval.FigureRetrievalService",
                   lambda *a, **k: FakeService(catalog)):
            selected, _source_dir = select_figures_with_fallback(self.base / "paper.md", None)
        self.assertEqual(len(selected), 2)


if __name__ == "__main__":
    unittest.main()
