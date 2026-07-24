"""
skills/pdf_parser.py — MinerU v4 PDF 精准解析技能

基于 MinerU v4 精准解析 API (/api/v4/extract/task)：
- 异步提交解析任务 → 轮询状态 → 下载 ZIP 包 → 解压得到 MD + JSON
- 支持 pipeline / vlm / MinerU-HTML 三种模型版本
- 文件大小 ≤ 200MB，页数 ≤ 200 页

需要用户在 .env 中配置 MINERU_API_KEY。
"""

from __future__ import annotations

import json
import logging
import os
import time
import zipfile
from pathlib import Path
from typing import Any

import httpx

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)

# MinerU v4 API 端点
MINERU_API_BASE = "https://mineru.net"
MINERU_TASK_URL = f"{MINERU_API_BASE}/api/v4/extract/task"


@register_skill("pdf-parse")
class PDFParser(BaseSkill):
    """
    MinerU v4 精准解析 PDF 技能。

    工作流程:
      1. POST {url, model_version} → 获取 task_id
      2. 轮询 GET /api/v4/extract/task/{task_id} → 等待完成
      3. 下载结果 ZIP → 解压到 data/parsed/{paper_id}/

    使用示例:
        parser = PDFParser()
        result = parser.execute(
            pdf_url="https://arxiv.org/pdf/2602.21756",
            arxiv_id="2602.21756",
        )
        # → data/parsed/2602.21756/2602.21756.md
        # → data/parsed/2602.21756/2602.21756.json
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key: str = settings.MINERU_API_KEY or kwargs.get("api_key", "")
        self._model_version: str = kwargs.get("model_version", settings.MINERU_MODEL_VERSION)
        self._poll_interval: float = settings.MINERU_POLL_INTERVAL
        self._poll_max_retries: int = settings.MINERU_POLL_MAX_RETRIES

    @property
    def is_ready(self) -> bool:
        """检查 MinerU API 是否已配置。"""
        return bool(self._api_key)

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        执行 PDF 精准解析（异步提交 + 轮询 + 下载）。

        参数:
            pdf_url    (str): PDF 在线地址
            pdf_path   (str): 本地 PDF 文件路径（暂不支持 v4 API 直接上传）
            arxiv_id   (str): arXiv ID
            title      (str): 论文标题，用于命名输出文件夹（会做文件名安全处理）
            output_dir (str): 输出目录，默认 data/parsed/

        返回:
            {
                "ready": bool,
                "arxiv_id": str,
                "markdown_path": str | None,   # 本地 .md 文件路径
                "json_path": str | None,        # 本地 .json 文件路径
                "content": {"text": str, ...} | None,
                "error": str | None,
            }
        """
        if not self.is_ready:
            logger.warning("MinerU API key not configured; returning empty result.")
            return {
                "ready": False,
                "arxiv_id": kwargs.get("arxiv_id", ""),
                "markdown_path": None,
                "json_path": None,
                "content": None,
                "error": "MINERU_API_KEY not set in .env",
            }

        pdf_url: str = kwargs.get("pdf_url", "")
        pdf_path: str = kwargs.get("pdf_path", "")
        arxiv_id: str = kwargs.get("arxiv_id", "")
        title: str = kwargs.get("title", "")
        output_dir: str = kwargs.get("output_dir", "")

        # ---- 确定输出目录（使用标题命名） ----
        if not output_dir:
            folder_name = arxiv_id
            if title:
                # 将标题转为安全的文件夹名：保留字母数字和中文，限制长度
                safe_title = PDFParser._sanitize_folder_name(title, max_len=80)
                folder_name = f"{arxiv_id}_{safe_title}"
            output_dir = str(settings.DATA_DIR / "parsed" / folder_name)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        md_path = out_path / f"{arxiv_id}.md"
        json_path = out_path / f"{arxiv_id}.json"

        # ---- Step 1: 提交解析任务 ----
        logger.info("[MinerU] Submitting parse task | url=%s model=%s", pdf_url or pdf_path, self._model_version)
        task_id = self._submit_task(pdf_url, pdf_path)
        if not task_id:
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "markdown_path": None,
                "json_path": None,
                "content": None,
                "error": "Failed to submit MinerU task.",
            }
        logger.info("[MinerU] Task created | task_id=%s", task_id)

        # ---- Step 2: 轮询等待完成 ----
        download_url = self._poll_task(task_id)
        if not download_url:
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "markdown_path": None,
                "json_path": None,
                "content": None,
                "error": f"Task {task_id} did not complete in time.",
            }

        # ---- Step 3: 下载并解压结果 ----
        logger.info("[MinerU] Downloading result for task %s ...", task_id)
        success = self._download_and_extract(download_url, out_path, arxiv_id)
        if not success:
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "markdown_path": None,
                "json_path": None,
                "content": None,
                "error": "Failed to download/extract MinerU result.",
            }

        # ---- Step 4: 读取解析内容 ----
        content = {}
        if md_path.exists():
            content["text"] = md_path.read_text(encoding="utf-8")
        if json_path.exists():
            try:
                content["json_data"] = json.loads(json_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                content["json_data"] = None

        logger.info(
            "[MinerU] Parse complete | id=%s text_len=%d",
            arxiv_id, len(content.get("text", "")),
        )

        return {
            "ready": True,
            "arxiv_id": arxiv_id,
            "markdown_path": str(md_path) if md_path.exists() else None,
            "json_path": str(json_path) if json_path.exists() else None,
            "content": content if content else None,
            "error": None,
        }

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_folder_name(title: str, max_len: int = 80) -> str:
        """
        将论文标题转为安全的文件夹名。

        保留: 中文、英文、数字、空格、连字符
        移除: 特殊字符 / \ : * ? " < > |
        空格转下划线，限制长度。
        """
        import re
        # 移除不安全字符
        safe = re.sub(r'[/\\:*?"<>|]', '', title)
        # 多余空格转下划线
        safe = re.sub(r'\s+', '_', safe)
        # 移除首尾特殊字符
        safe = safe.strip('._-')
        # 截断
        if len(safe) > max_len:
            safe = safe[:max_len].rstrip('._-')
        return safe

    # ------------------------------------------------------------------
    # 内部方法: 提交任务
    # ------------------------------------------------------------------

    def _submit_task(self, pdf_url: str, pdf_path: str) -> str | None:
        """
        提交解析任务到 MinerU v4 API。

        返回 task_id，失败返回 None。
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        # 构建请求体
        if pdf_url:
            data: dict[str, Any] = {
                "url": pdf_url,
                "model_version": self._model_version,
            }
        else:
            # v4 API 的本地文件上传需要不同方式，这里暂用 URL 模式
            data = {
                "url": f"file://{pdf_path}",
                "model_version": self._model_version,
            }

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(MINERU_TASK_URL, headers=headers, json=data)
                resp.raise_for_status()
                result = resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error("[MinerU] Submit HTTP %d: %s", exc.response.status_code, exc.response.text[:500])
            return None
        except Exception as exc:
            logger.error("[MinerU] Submit error: %s", exc)
            return None

        # 解析 task_id（MinerU API 返回格式: {"code": 0, "data": {"task_id": "..."}}）
        task_data = result.get("data", {})
        task_id = task_data.get("task_id", "")
        if not task_id:
            logger.error("[MinerU] No task_id in response: %s", result)
            return None
        return task_id

    # ------------------------------------------------------------------
    # 内部方法: 轮询任务
    # ------------------------------------------------------------------

    def _poll_task(self, task_id: str) -> str | None:
        """
        轮询任务状态直到完成。

        返回下载 URL，超时或失败返回 None。
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        poll_url = f"{MINERU_TASK_URL}/{task_id}"

        for attempt in range(1, self._poll_max_retries + 1):
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.get(poll_url, headers=headers)
                    resp.raise_for_status()
                    result = resp.json()
            except Exception as exc:
                logger.error("[MinerU] Poll attempt %d error: %s", attempt, exc)
                time.sleep(self._poll_interval)
                continue

            data = result.get("data", {})
            state = data.get("state", data.get("status", ""))

            if state in ("done", "success", "completed", "ready"):
                # 任务完成，获取下载链接
                # MinerU v4 API 返回 full_zip_url 字段
                download_url = (
                    data.get("full_zip_url")
                    or data.get("download_url")
                    or data.get("result_url")
                    or data.get("url")
                    or ""
                )
                if not download_url:
                    # 某些版本直接在 data 中返回 markdown/json 字段
                    files = data.get("files", {})
                    download_url = files.get("zip", files.get("markdown", ""))
                logger.info("[MinerU] Task completed | task_id=%s state=%s url=%s", task_id, state, download_url[:80] if download_url else "N/A")
                return download_url if download_url else None

            elif state in ("failed", "error", "cancelled"):
                err_msg = data.get("error", data.get("message", "Unknown error"))
                logger.error("[MinerU] Task failed | task_id=%s error=%s", task_id, err_msg)
                return None

            else:
                # 处理中: pending / processing / running
                logger.info(
                    "[MinerU] Poll %d/%d | task_id=%s state=%s",
                    attempt, self._poll_max_retries, task_id, state,
                )
                time.sleep(self._poll_interval)

        logger.error("[MinerU] Poll timeout | task_id=%s after %d attempts", task_id, self._poll_max_retries)
        return None

    # ------------------------------------------------------------------
    # 内部方法: 下载与解压
    # ------------------------------------------------------------------

    def _download_and_extract(self, download_url: str, output_dir: Path, arxiv_id: str) -> bool:
        """
        下载解析结果 ZIP 包并解压到指定目录。

        ZIP 包内通常包含:
          - {arxiv_id}.md   (或 {name}.md)
          - {arxiv_id}.json (或 {name}.json)
        """
        if not download_url:
            logger.error("[MinerU] No download URL provided.")
            return False

        # 构建完整 URL
        if not download_url.startswith("http"):
            download_url = f"{MINERU_API_BASE}{download_url}"

        zip_path = output_dir / f"{arxiv_id}_result.zip"

        try:
            # 下载 ZIP
            logger.info("[MinerU] Downloading from %s ...", download_url[:120])
            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                resp = client.get(download_url)
                resp.raise_for_status()
                zip_path.write_bytes(resp.content)
            logger.info("[MinerU] Downloaded %d bytes -> %s", len(resp.content), zip_path)

            # 解压
            with zipfile.ZipFile(zip_path, "r") as zf:
                file_list = zf.namelist()
                logger.info("[MinerU] ZIP contains %d files: %s", len(file_list), file_list)

                for member in file_list:
                    # 跳过目录条目
                    if member.endswith("/"):
                        continue

                    # 提取文件，重命名关键文件
                    basename = Path(member).name
                    ext = Path(member).suffix.lower()

                    if basename == "full.md":
                        # 主 Markdown 文件
                        target = output_dir / f"{arxiv_id}.md"
                    elif basename.endswith("_content_list_v2.json"):
                        target = output_dir / f"{arxiv_id}_content.json"
                    elif basename.endswith("_content_list.json"):
                        target = output_dir / f"{arxiv_id}_content_full.json"
                    elif basename.endswith("_model.json"):
                        target = output_dir / f"{arxiv_id}_model.json"
                    elif basename == "layout.json":
                        target = output_dir / f"{arxiv_id}_layout.json"
                    elif ext == ".json":
                        target = output_dir / basename
                    elif "images/" in member:
                        # 保持 images/ 子目录结构
                        img_dir = output_dir / "images"
                        img_dir.mkdir(parents=True, exist_ok=True)
                        target = img_dir / basename
                    else:
                        target = output_dir / basename

                    with zf.open(member) as src:
                        target.write_bytes(src.read())
                    logger.info("[MinerU] Extracted: %s", target.name)

            # 清理 ZIP
            zip_path.unlink(missing_ok=True)
            return True

        except zipfile.BadZipFile as exc:
            logger.error("[MinerU] Corrupted ZIP: %s", exc)
            return False
        except Exception as exc:
            logger.error("[MinerU] Download/extract error: %s", exc)
            return False
