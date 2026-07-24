"""
skills/pdf_parser.py — MinerU PDF 解析技能

基于 MinerU API 对论文 PDF 进行解析，提取:
  - 结构化文本（段落、标题层级）
  - 表格数据
  - 图片引用
  - 公式（LaTeX）

需要用户在 .env 中配置 MINERU_API_KEY。
若未配置，本技能将返回未就绪状态，不会报错中断主流程。

接口设计为异步友好，后续可替换为本地 MinerU 部署。
"""

from __future__ import annotations

import logging
import base64
import time
from pathlib import Path
from typing import Any

import httpx

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

# MinerU API 端点（以官方文档为准）
MINERU_API_ENDPOINT = "https://mineru.net/api/v1/parse"


@register_skill("pdf-parse")
class PDFParser(BaseSkill):
    """
    MinerU PDF 解析技能。

    支持两种输入方式:
      1. 本地 PDF 路径  -> 读取并上传解析
      2. PDF URL       -> 由 MinerU 服务端直接拉取

    返回结构化解析结果，包含文本、表格、图片等信息。

    使用示例:
        parser = PDFParser()
        result = parser.execute(
            pdf_url="https://arxiv.org/pdf/2503.21460",
            parse_mode="auto",
        )
        content = result["content"]
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key: str = settings.MINERU_API_KEY or kwargs.get("api_key", "")

    @property
    def is_ready(self) -> bool:
        """检查 MinerU API 是否已配置。"""
        return bool(self._api_key)

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行 PDF 解析。

        参数:
            pdf_url    (str) : PDF 在线地址（与 pdf_path 二选一）
            pdf_path   (str) : 本地 PDF 文件路径
            parse_mode (str) : "auto" | "text" | "full" — 解析模式
            max_retries(int) : 最大重试次数，默认 3

        返回:
            {
                "ready": bool,
                "arxiv_id": str,
                "content": {  # 仅 ready=True 时有意义
                    "text": str,
                    "sections": [...],
                    "tables": [...],
                    "figures": [...],
                },
                "error": str | None,
            }
        """
        if not self.is_ready:
            logger.warning("MinerU API key not configured; returning empty result.")
            return {
                "ready": False,
                "arxiv_id": kwargs.get("arxiv_id", ""),
                "content": None,
                "error": "MINERU_API_KEY not set in .env",
            }

        pdf_url: str = kwargs.get("pdf_url", "")
        pdf_path: str = kwargs.get("pdf_path", "")
        parse_mode: str = kwargs.get("parse_mode", "auto")
        max_retries: int = kwargs.get("max_retries", 3)

        # ---- 准备请求载荷 ----
        if pdf_url:
            payload = {"url": pdf_url, "mode": parse_mode}
        elif pdf_path:
            local_path = Path(pdf_path)
            if not local_path.exists():
                return {
                    "ready": True,
                    "arxiv_id": kwargs.get("arxiv_id", ""),
                    "content": None,
                    "error": f"File not found: {pdf_path}",
                }
            payload = self._build_file_payload(local_path, parse_mode)
        else:
            return {
                "ready": True,
                "arxiv_id": kwargs.get("arxiv_id", ""),
                "content": None,
                "error": "Either pdf_url or pdf_path must be provided.",
            }

        # ---- 调用 API（含重试） ----
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }

        for attempt in range(1, max_retries + 1):
            try:
                with httpx.Client(timeout=120.0) as client:
                    resp = client.post(MINERU_API_ENDPOINT, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                return {
                    "ready": True,
                    "arxiv_id": kwargs.get("arxiv_id", ""),
                    "content": self._normalize_response(data),
                    "error": None,
                }
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "MinerU HTTP %d on attempt %d/%d: %s",
                    exc.response.status_code, attempt, max_retries, exc,
                )
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
            except Exception as exc:
                logger.error("MinerU request error attempt %d/%d: %s", attempt, max_retries, exc)
                if attempt < max_retries:
                    time.sleep(2 ** attempt)

        return {
            "ready": True,
            "arxiv_id": kwargs.get("arxiv_id", ""),
            "content": None,
            "error": f"Failed after {max_retries} retries.",
        }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _build_file_payload(local_path: Path, mode: str) -> dict[str, Any]:
        """为本地文件构建 base64 编码载荷。"""
        with open(local_path, "rb") as fh:
            raw = fh.read()
        b64_content = base64.b64encode(raw).decode("ascii")
        return {
            "file": b64_content,
            "filename": local_path.name,
            "mode": mode,
        }

    @staticmethod
    def _normalize_response(data: dict[str, Any]) -> dict[str, Any]:
        """
        将 MinerU 原始响应标准化为统一结构。

        目标输出:
          - text     : 全文纯文本（按阅读顺序）
          - sections : 按段落/章节分割的结构化文本
          - tables   : 提取的表格列表
          - figures  : 图片引用列表
          - formulas : LaTeX 公式列表
        """
        # 以下字段名需根据实际 MinerU API 响应调整
        return {
            "text": data.get("text", data.get("content", "")),
            "sections": data.get("sections", data.get("paragraphs", [])),
            "tables": data.get("tables", []),
            "figures": data.get("figures", data.get("images", [])),
            "formulas": data.get("formulas", data.get("equations", [])),
            "raw_response": data,
        }
