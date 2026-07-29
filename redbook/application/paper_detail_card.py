"""Render an evidence-labelled final page for a local paper draft."""
from __future__ import annotations

import json
from pathlib import Path
import textwrap
from typing import Any

from PIL import Image, ImageDraw, ImageFont


class PaperDetailCardRenderer:
    size = (1080, 1440)

    @staticmethod
    def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = (
            (r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf")
            if bold
            else (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simsun.ttc")
        )
        for candidate in candidates:
            if Path(candidate).is_file():
                return ImageFont.truetype(candidate, size)
        return ImageFont.load_default()

    @staticmethod
    def _wrapped(
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        width: int,
        font: ImageFont.FreeTypeFont,
        color: str,
        gap: int = 8,
    ) -> int:
        chars_per_line = max(12, width // max(10, font.size))
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            lines.extend(textwrap.wrap(paragraph, width=chars_per_line, break_long_words=False) or [""])
        for line in lines:
            draw.text((x, y), line, font=font, fill=color)
            y += font.size + gap
        return y

    def render(self, paper_metadata: Path, lineage_evidence: Path, output: Path) -> Path:
        paper: dict[str, Any] = json.loads(paper_metadata.read_text(encoding="utf-8"))
        lineage: dict[str, Any] = json.loads(lineage_evidence.read_text(encoding="utf-8"))
        image = Image.new("RGB", self.size, "#F7F9FC")
        draw = ImageDraw.Draw(image)
        title, small = self._font(42, True), self._font(20)
        x, y, width = 64, 56, 952

        draw.text((x, y), "知识图谱 · 论文详情", font=title, fill="#102A43")
        y += 70
        draw.text((x, y), "引用锚点，不等同于严格因果发展链", font=small, fill="#526D82")
        y += 58
        draw.rounded_rectangle((x, y, x + width, y + 126), radius=24, fill="#153E75")
        draw.text(
            (x + 28, y + 20),
            f"{paper.get('published', '2026')[:4]} · {paper.get('topic', '论文研究图谱')}",
            font=self._font(26, True),
            fill="white",
        )
        self._wrapped(draw, paper["title"], x + 28, y + 59, width - 56, self._font(20), "#DCEBFF", 2)
        y += 164

        draw.text((x, y), "论文中可定位的引用锚点", font=self._font(30, True), fill="#102A43")
        y += 54
        for index, anchor in enumerate(lineage["anchors"], 1):
            card_h = 185
            draw.rounded_rectangle((x, y, x + width, y + card_h), radius=20, fill="white", outline="#D9E2EC", width=2)
            draw.ellipse((x + 24, y + 28, x + 82, y + 86), fill="#2F80ED")
            draw.text((x + 41, y + 42), str(index), font=self._font(22, True), fill="white")
            draw.text((x + 104, y + 24), f"{anchor['year']}  {anchor['relation']}", font=small, fill="#356AA0")
            next_y = self._wrapped(draw, anchor["title"], x + 104, y + 56, width - 132, self._font(22, True), "#102A43", 2)
            self._wrapped(draw, anchor["evidence"], x + 104, next_y + 7, width - 132, self._font(18), "#526D82", 1)
            y += card_h + 18

        draw.line((x, y + 2, x + width, y + 2), fill="#C9D8E8", width=2)
        y += 26
        draw.text((x, y), "可追溯信息", font=self._font(26, True), fill="#102A43")
        y += 45
        y = self._wrapped(draw, f"论文：{paper['source_url']}", x, y, width, small, "#245B93", 5)
        y = self._wrapped(draw, f"PDF：{paper['pdf_url']}", x, y, width, small, "#245B93", 5)
        self._wrapped(draw, f"代码：{paper['github_status']}", x, y, width, small, "#526D82", 5)
        draw.text((x, 1388), "图谱关系、论文链接与代码状态均来自本地解析及官方来源核验。", font=self._font(16), fill="#748AA0")
        output.parent.mkdir(parents=True, exist_ok=True)
        image.save(output, quality=95, subsampling=0)
        return output
