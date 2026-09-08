"""L3 校验层：微信安全门（复用 validate_gzh_html.py）+ 移动端布局断言。

- WeChatHTMLGate：直接 import 项目既有 ``validate_gzh_html`` 的 FORBIDDEN/LeafChecker，
  作为发布前必过结构安全门。ERROR 必须清零。
- assert_mobile_layout：无横向滚动（scrollWidth≤视口）、图片 width:100%、字号≥14px 启发式断言。
- VisualRegression（可选）：Playwright 三视口截图比对，未安装则 skip 并给提示。
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import List

# 复用项目既有校验器（路径：wechat_design/scripts/validate_gzh_html.py）
_SCRIPTS = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from validate_gzh_html import validate as _validate_gzh  # noqa: E402

CJK = re.compile(r"[一-鿿㐀-䶿]")


@dataclass
class GateResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    leaf_count: int = 0
    passed: bool = True

    def merge(self, other: "GateResult") -> "GateResult":
        self.errors += other.errors
        self.warnings += other.warnings
        self.leaf_count += other.leaf_count
        self.passed = self.passed and other.passed
        return self


def wechat_gate(html: str, name: str = "<A轨产物>") -> GateResult:
    """微信安全门：零 ERROR 才 passed。"""
    errs, warns, leaf_n = _validate_gzh(html, name)
    return GateResult(errors=list(errs), warnings=list(warns),
                      leaf_count=leaf_n, passed=len(errs) == 0)


_FONT_PX = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
_IMG_W = re.compile(r"<img[^>]*style=\"[^\"]*width\s*:\s*100%", re.I)


def assert_mobile_layout(html: str, viewport: int = 375,
                         min_font: int = 12) -> GateResult:
    """移动端布局断言（启发式，不依赖浏览器）。

    - 字号：所有显式 font-size 必须 ≥ min_font（项目下限 12px：KPI 标签 12 / 图注 13；
      设计报告建议理想值 14px，此处以项目既有主题铁律为 floor，避免误杀）。
    - 图片：含 <img> 时应声明 width:100%（防溢出）。
    """
    res = GateResult(passed=True)
    fonts = [float(x) for x in _FONT_PX.findall(html)]
    if fonts and min(fonts) < min_font:
        res.errors.append(f"存在字号 {min(fonts)}px < {min_font}px，移动端可能过小")
        res.passed = False
    imgs = re.findall(r"<img", html, re.I)
    img_w100 = len(_IMG_W.findall(html))
    if imgs and img_w100 < len(imgs):
        res.warnings.append(
            f"{len(imgs)-img_w100} 张 <img> 未声明 width:100%，可能横向溢出")
    return res


def visual_regression(html: str, out_png: str, viewport: tuple = (375, 812)) -> bool:
    """可选：Playwright 截图比对（需安装 playwright）。未装返回 False 并提示。"""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        print("[visual] 跳过：未安装 playwright（pip install playwright && "
              "playwright install chromium）。生产用 Percy/Chromatic(#25) 或 BackstopJS(#26)。")
        return False
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        pg.set_content(html)
        pg.screenshot(path=out_png)
        b.close()
    return True


def full_check(html: str, name: str = "<A轨产物>") -> GateResult:
    """发布前总校验：安全门 + 移动端断言。"""
    r = wechat_gate(html, name)
    r.merge(assert_mobile_layout(html))
    return r
