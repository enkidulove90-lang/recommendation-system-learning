"""DTLE 全层测试（stdlib unittest，零外部依赖）。

运行：
    python -m unittest wechat_design.dtle.tests.test_dtle -v
或：
    python wechat_design/dtle/tests/run.py
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from wechat_design.dtle import render_source  # noqa: E402
from wechat_design.dtle.core.components import REGISTRY, render_block_html  # noqa: E402
from wechat_design.dtle.core.document import parse_markdown  # noqa: E402
from wechat_design.dtle.core.types import ThemeTokens  # noqa: E402
from wechat_design.dtle.renderers.chart import render_svg  # noqa: E402
from wechat_design.dtle.tokens import build_all, derive_tokens, list_themes  # noqa: E402
from wechat_design.dtle.validation.gate import assert_mobile_layout, full_check  # noqa: E402

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "loopsbench_dtle.json")


class TestTokens(unittest.TestCase):
    def test_themes_present(self):
        self.assertEqual(set(list_themes()), {"recsys-blue", "minimal", "academic"})

    def test_derive_has_scale_and_roles(self):
        toks = derive_tokens({"name": "x", "type": {"baseFontSize": 15, "scaleRatio": 1.25}})
        self.assertIn("step0", toks["type"]["scale"])
        self.assertGreaterEqual(toks["type"]["roles"]["h1"], toks["type"]["roles"]["body"])

    def test_build_all_writes_products(self):
        m = build_all()
        gen = os.path.join(os.path.dirname(__file__), "..", "tokens", "generated")
        for name in m["themes"]:
            self.assertTrue(os.path.exists(os.path.join(gen, f"tokens.{name}.css")))
            self.assertTrue(os.path.exists(os.path.join(gen, f"tokens.{name}.json")))


class TestComponents(unittest.TestCase):
    def test_all_11_components_registered(self):
        names = set(REGISTRY.keys())
        expected = {"hook_title", "cover", "one_liner", "section_header", "body_para",
                    "rr_table", "kpi_cards", "figure", "limitation", "cta", "references"}
        self.assertEqual(names, expected)

    def test_each_component_wechat_safe(self):
        t = ThemeTokens.load("recsys-blue")
        sample = {
            "hook_title": {"title": "T", "subtitle": "S"},
            "cover": {"src": "u"},
            "one_liner": {"text": "一句话结论在这里"},
            "section_header": {"text": "小标题"},
            "body_para": {"text": "正文含**关键**词", "keywords": ["关键"]},
            "rr_table": {"headers": ["A", "B"], "rows": [["1", "2"]]},
            "kpi_cards": {"items": [{"value": "+8", "label": "指标"}]},
            "figure": {"src": "u", "caption": "图注"},
            "limitation": {"text": "局限说明"},
            "cta": {"text": "互动问题"},
            "references": {"items": [{"label": "论文", "url": "https://x.com"}],
                           "note": "注"},
        }
        for name, props in sample.items():
            html = render_block_html(name, props, t)
            self.assertNotIn("<div", html, f"{name} 不应含 <div>")
            self.assertNotIn("<style", html, f"{name} 不应含 <style>")
            self.assertNotIn(" class=", html, f"{name} 不应含 class")
            # 含中文的组件应出现 span leaf 包裹
            if any("一" <= c <= "鿿" for c in str(props)):
                self.assertIn('span leaf', html, f"{name} 中文应被 leaf 包裹")


class TestRenderers(unittest.TestCase):
    def test_wechat_render_safe_and_valid(self):
        out = render_source(EXAMPLE, track="wechat", theme="recsys-blue")
        html = out.html
        self.assertNotIn("<div", html)
        self.assertNotIn("<style", html)
        self.assertNotIn(" class=", html)
        self.assertIn('span leaf', html)
        gate = full_check(html)
        self.assertTrue(gate.passed, f"校验门失败: {gate.errors}")

    def test_xhs_card_dimension(self):
        out = render_source(EXAMPLE, track="xhs", theme="recsys-blue")
        self.assertIn("1242", out.html)
        self.assertIn("<html", out.html)

    def test_chart_svg(self):
        t = ThemeTokens.load("recsys-blue")
        for ctype in ("bar", "line", "pie"):
            spec = {"type": ctype, "title": "t",
                    "labels": ["a", "b"], "series": [{"name": "s", "data": [1, 2]}]}
            if ctype == "pie":
                spec = {"type": "pie", "labels": ["a", "b"], "values": [1, 2]}
            svg = render_svg(spec, t)
            self.assertTrue(svg.startswith("<svg"), f"{ctype} 应以 <svg 开头")

    def test_three_themes_render(self):
        for th in ("recsys-blue", "minimal", "academic"):
            out = render_source(EXAMPLE, track="wechat", theme=th)
            self.assertTrue(full_check(out.html).passed, f"{th} 校验失败")


class TestDocumentParse(unittest.TestCase):
    def test_markdown_mapping(self):
        md = ("# 主标题\n## 小节\n> 金句\n**重点**正文\n"
              "| 列1 | 列2 |\n| --- | --- |\n| a | b |\n")
        doc = parse_markdown(md, theme="recsys-blue")
        types = [b.type for b in doc.blocks]
        self.assertEqual(types[0], "hook_title")
        self.assertIn("section_header", types)
        self.assertIn("one_liner", types)
        self.assertIn("rr_table", types)


class TestValidation(unittest.TestCase):
    def test_bad_html_fails(self):
        bad = '<div class="x">文字</div><style>.a{}</style>'
        g = full_check(bad)
        self.assertFalse(g.passed)
        self.assertTrue(g.errors)

    def test_mobile_font_floor(self):
        r = assert_mobile_layout('<p style="font-size:11px">x</p>')
        self.assertFalse(r.passed)


class TestIntegration(unittest.TestCase):
    def test_render_for_publish(self):
        from wechat_design.dtle.integration import render_for_publish
        res = render_for_publish("# 标题\n正文", track="wechat", theme="recsys-blue")
        self.assertTrue(res["ok"])
        self.assertTrue(res["gate"]["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
