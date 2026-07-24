"""
skills/pdf_downloader.py — arXiv PDF 下载技能

从 arXiv 下载论文 PDF 到本地 data/papers/ 目录。
以 arxiv_id 命名，支持断点续传检测。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import httpx

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("pdf-download")
class PDFDownloader(BaseSkill):
    """
    arXiv PDF 下载技能。

    从 arXiv 下载论文 PDF 到本地存储。

    使用示例:
        downloader = PDFDownloader()
        result = downloader.execute(
            arxiv_id="2602.21756",
        )
        # → data/papers/2602.21756.pdf
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._output_dir: Path = settings.DATA_DIR / "papers"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        下载论文 PDF。

        参数:
            arxiv_id   (str): arXiv ID，如 "2602.21756"
            pdf_url    (str): 直接指定 PDF URL（可选，否则从 arXiv ID 构建）
            output_dir (str): 自定义输出目录（可选）

        返回:
            {
                "arxiv_id": str,
                "pdf_path": str | None,      # 本地 PDF 文件路径
                "pdf_url": str,
                "file_size": int,            # 文件大小（字节）
                "downloaded": bool,          # 是否本次下载
                "error": str | None,
            }
        """
        arxiv_id: str = kwargs.get("arxiv_id", "")
        pdf_url: str = kwargs.get("pdf_url", "")
        output_dir: str = kwargs.get("output_dir", "")

        if not arxiv_id and not pdf_url:
            return {
                "arxiv_id": "",
                "pdf_path": None,
                "pdf_url": "",
                "file_size": 0,
                "downloaded": False,
                "error": "Either arxiv_id or pdf_url must be provided.",
            }

        # 构建 PDF URL
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

        # 从 URL 提取 arXiv ID（如果未提供）
        if not arxiv_id:
            # 从 URL 中提取: https://arxiv.org/pdf/2602.21756
            arxiv_id = pdf_url.rstrip("/").rsplit("/", 1)[-1]
            if arxiv_id.endswith(".pdf"):
                arxiv_id = arxiv_id[:-4]

        # 确定本地路径
        if output_dir:
            out_path = Path(output_dir) / f"{arxiv_id}.pdf"
        else:
            out_path = self._output_dir / f"{arxiv_id}.pdf"

        # 如果已存在，跳过下载
        if out_path.exists():
            file_size = out_path.stat().st_size
            if file_size > 0:
                logger.info("[PDF Download] Already exists: %s (%d bytes)", out_path.name, file_size)
                return {
                    "arxiv_id": arxiv_id,
                    "pdf_path": str(out_path),
                    "pdf_url": pdf_url,
                    "file_size": file_size,
                    "downloaded": False,
                    "error": None,
                }

        # 下载 PDF
        logger.info("[PDF Download] Downloading %s -> %s ...", pdf_url, out_path.name)
        try:
            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                resp = client.get(pdf_url)
                resp.raise_for_status()
                out_path.write_bytes(resp.content)

            file_size = len(resp.content)
            logger.info("[PDF Download] Saved %d bytes -> %s", file_size, out_path)
            return {
                "arxiv_id": arxiv_id,
                "pdf_path": str(out_path),
                "pdf_url": pdf_url,
                "file_size": file_size,
                "downloaded": True,
                "error": None,
            }

        except httpx.HTTPStatusError as exc:
            logger.error("[PDF Download] HTTP %d for %s: %s", exc.response.status_code, arxiv_id, exc)
            return {
                "arxiv_id": arxiv_id,
                "pdf_path": None,
                "pdf_url": pdf_url,
                "file_size": 0,
                "downloaded": False,
                "error": f"HTTP {exc.response.status_code}",
            }
        except Exception as exc:
            logger.error("[PDF Download] Error for %s: %s", arxiv_id, exc)
            return {
                "arxiv_id": arxiv_id,
                "pdf_path": None,
                "pdf_url": pdf_url,
                "file_size": 0,
                "downloaded": False,
                "error": str(exc),
            }
