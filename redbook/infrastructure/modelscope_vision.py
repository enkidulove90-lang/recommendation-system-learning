"""OpenAI-compatible ModelScope Qwen multimodal adapter for image review."""
from __future__ import annotations

import base64
import json
from pathlib import Path
import re
from typing import Iterable

from openai import OpenAI

from config import settings
from redbook.domain.media import FigureCandidate, VisionReview


class ModelScopeVisionReviewer:
    """Review figure readability; this gate ranks, it never invents pixels."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.MODELSCOPE_API_KEY
        self.base_url = base_url or settings.MODELSCOPE_BASE_URL
        self.model = model or settings.MODELSCOPE_VISION_MODEL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None
        self.last_error = ""

    @property
    def is_ready(self) -> bool:
        return self.client is not None

    @staticmethod
    def _data_url(path: Path) -> str:
        suffix = path.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(suffix)
        if not mime:
            raise ValueError(f"Unsupported image type: {path}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    def review(self, candidates: Iterable[FigureCandidate], max_images: int = 4) -> dict[str, VisionReview]:
        selected = [candidate for candidate in candidates if candidate.eligible][:max_images]
        if not selected or not self.client:
            return {}
        content: list[dict] = [{
            "type": "text",
            "text": (
                "You are a strict academic-figure editor for Xiaohongshu. Review each image for "
                "readability on a phone, relevance to the stated paper figure caption, and legibility of chart/text. "
                "Do not assess novelty or make factual claims. Return ONLY JSON array with objects: "
                "{path, readability, relevance, text_legibility, verdict, reason}. Scores are 0-1; verdict is keep or reject.\n"
                + "\n".join(f"path={item.path}; caption={item.caption}; role={item.role}" for item in selected)
            ),
        }]
        for item in selected:
            content.append({"type": "image_url", "image_url": {"url": self._data_url(Path(item.path))}})
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                temperature=0,
                max_tokens=1000,
            )
            raw = response.choices[0].message.content or "[]"
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.IGNORECASE)
            rows = json.loads(raw)
        except Exception as error:
            # Vision is an optional ranking gate. A provider outage or account
            # policy must not discard high-quality local source figures.
            self.last_error = f"{type(error).__name__}: {str(error)[:240]}"
            return {}
        allowed = {item.path for item in selected}
        result: dict[str, VisionReview] = {}
        for row in rows if isinstance(rows, list) else []:
            path = str(row.get("path", ""))
            if path not in allowed:
                continue
            clamp = lambda value: max(0.0, min(1.0, float(value)))
            result[path] = VisionReview(
                path=path,
                readability=clamp(row.get("readability", 0)),
                relevance=clamp(row.get("relevance", 0)),
                text_legibility=clamp(row.get("text_legibility", 0)),
                verdict=str(row.get("verdict", "reject")).lower(),
                reason=str(row.get("reason", ""))[:240],
            )
        return result
