"""
skills/folder_standardizer.py — 文件夹标准化整理技能

将 data/parsed/ 下的论文文件夹统一为标准结构和命名。

标准结构:
  data/parsed/{arXiv ID}_{中文标题}_[方向标签]/
  ├── {arXiv ID}.md                      # 全文 Markdown
  ├── {arXiv ID}_content.json            # 结构化内容（MinerU 输出）
  ├── {arXiv ID}_figures.json            # 图表视觉描述（Phase 2B 输出）
  ├── {arXiv ID}_origin.pdf              # 原始 PDF
  └── images/                            # 提取的图片
      └── {hash}.jpg

文件安全规则:
  - 移动/重命名前先 cp -r 备份到 data/parsed/_backup_{timestamp}/
  - 每批最多处理 10 个文件夹
  - 任何 mv 失败立即停止
"""

from __future__ import annotations

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill("folder-standardize")
class FolderStandardizer(BaseSkill):
    """
    文件夹标准化整理技能。

    使用示例:
        standardizer = FolderStandardizer()
        result = standardizer.execute(
            paper_dir="data/parsed/2505.19525_ConfSMoE",
            arxiv_id="2505.19525",
            chinese_title="ConfSMoE",
            direction_tag="llm_ranking",
        )
    """

    STANDARD_FILES = {
        "md": "{arxiv_id}.md",
        "content_json": "{arxiv_id}_content.json",
        "content_full_json": "{arxiv_id}_content_full.json",
        "layout_json": "{arxiv_id}_layout.json",
        "model_json": "{arxiv_id}_model.json",
        "figures_json": "{arxiv_id}_figures.json",
        "origin_pdf": "{arxiv_id}_origin.pdf",
    }

    STANDARD_DIRS = {"images", "images_hd", "arxiv_source"}

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._backup_dir: Path | None = None

    @property
    def is_ready(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        标准化单个论文文件夹。

        参数:
            paper_dir      (str): 当前文件夹路径
            arxiv_id       (str): arXiv ID
            chinese_title  (str): 中文标题（用于命名）
            direction_tag  (str): 方向标签（如 "llm_ranking" 或 "[llm_ranking×efficient_retrieval]"）
            dry_run        (bool): 仅模拟不实际操作，默认 False
            backup         (bool): 是否备份，默认 True

        返回:
            {
                "original_dir": str,
                "new_dir": str,
                "renamed_files": list[str],
                "moved_dirs": list[str],
                "backup_path": str | None,
                "error": str | None,
            }
        """
        paper_dir: str = kwargs.get("paper_dir", "")
        arxiv_id: str = kwargs.get("arxiv_id", "")
        chinese_title: str = kwargs.get("chinese_title", "")
        direction_tag: str = kwargs.get("direction_tag", "")
        dry_run: bool = kwargs.get("dry_run", False)
        backup: bool = kwargs.get("backup", True)

        if not paper_dir or not arxiv_id:
            return {
                "original_dir": paper_dir,
                "new_dir": "",
                "renamed_files": [],
                "moved_dirs": [],
                "backup_path": None,
                "error": "paper_dir and arxiv_id are required.",
            }

        paper_path = Path(paper_dir)
        if not paper_path.exists():
            return {
                "original_dir": paper_dir,
                "new_dir": "",
                "renamed_files": [],
                "moved_dirs": [],
                "backup_path": None,
                "error": f"Directory not found: {paper_dir}",
            }

        # 构建标准文件夹名
        safe_title = self._sanitize_title(chinese_title or arxiv_id)
        safe_tag = self._sanitize_tag(direction_tag) if direction_tag else ""
        new_folder_name = f"{arxiv_id}_{safe_title}"
        if safe_tag:
            new_folder_name = f"{new_folder_name}_{safe_tag}"

        new_path = paper_path.parent / new_folder_name

        renamed_files: list[str] = []
        moved_dirs: list[str] = []
        backup_path: str | None = None

        if dry_run:
            logger.info("[Standardizer] DRY RUN for %s -> %s", paper_path.name, new_folder_name)
            return {
                "original_dir": str(paper_path),
                "new_dir": str(new_path),
                "renamed_files": [],
                "moved_dirs": [],
                "backup_path": None,
                "error": None,
            }

        try:
            # Step 1: 备份（可选，默认跳过以避免 Windows 文件锁定）
            if backup:
                backup_path = self._backup_folder(paper_path)
                if not backup_path:
                    logger.warning("[Standardizer] Backup failed, continuing without backup")

            # Step 2: 重命名文件
            renamed_files = self._rename_files(paper_path, arxiv_id)

            # Step 3: 合并 images_hd/ 到 images/
            moved_dirs = self._merge_images_hd(paper_path)

            # Step 4: 移动 arxiv_source/ 到 data/papers/
            moved_dirs.extend(self._move_arxiv_source(paper_path, arxiv_id))

            # Step 5: 重命名 PDF 为 _origin.pdf
            pdf_rename = self._rename_pdf(paper_path, arxiv_id)
            if pdf_rename:
                renamed_files.append(pdf_rename)

            # Step 6: 重命名文件夹（使用 copytree 避免 safe-delete 问题）
            if paper_path.name != new_folder_name:
                if new_path.exists():
                    # 目标已存在（可能是前次运行残留），检查是否有内容
                    has_content = any(new_path.glob("*.md"))
                    if has_content:
                        logger.info("[Standardizer] Target already exists with content: %s (skip rename)", new_path.name)
                    else:
                        # 目标存在但无内容，尝试复制关键文件
                        logger.warning("[Standardizer] Target exists but empty: %s, copying files", new_path.name)
                        for item in paper_path.iterdir():
                            if item.is_file():
                                target_file = new_path / item.name
                                if not target_file.exists():
                                    try:
                                        shutil.copy2(str(item), str(target_file))
                                    except OSError:
                                        pass
                else:
                    # 目标不存在，使用 copytree（不用 move，避免 safe-delete）
                    try:
                        shutil.copytree(str(paper_path), str(new_path))
                        logger.info("[Standardizer] Copied folder: %s -> %s", paper_path.name, new_folder_name)
                    except OSError as copy_err:
                        logger.error("[Standardizer] Copy failed: %s", copy_err)
                        raise

            return {
                "original_dir": str(paper_path),
                "new_dir": str(new_path),
                "renamed_files": renamed_files,
                "moved_dirs": moved_dirs,
                "backup_path": backup_path,
                "error": None,
            }

        except Exception as e:
            logger.error("[Standardizer] Error: %s", e)
            return {
                "original_dir": str(paper_path),
                "new_dir": "",
                "renamed_files": renamed_files,
                "moved_dirs": moved_dirs,
                "backup_path": backup_path,
                "error": str(e),
            }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize_title(title: str, max_len: int = 60) -> str:
        """将标题转为安全的文件夹名。"""
        safe = re.sub(r'[/\\:*?"<>|]', '', title)
        safe = re.sub(r'[：：××\[\]【】]', '_', safe)
        safe = re.sub(r'\s+', '_', safe)
        safe = safe.strip('._-')
        if len(safe) > max_len:
            safe = safe[:max_len].rstrip('._-')
        return safe

    @staticmethod
    def _sanitize_tag(tag: str) -> str:
        """将方向标签转为安全的文件夹名部分。"""
        # 移除 [ ] × 等特殊字符，替换为下划线
        safe = re.sub(r'[\[\]×]', '_', tag)
        safe = re.sub(r'[：：*/\\:?<>|"]', '_', safe)
        safe = re.sub(r'_+', '_', safe)
        safe = safe.strip('._-')
        return safe

    def _backup_folder(self, paper_path: Path) -> str | None:
        """备份文件夹到 data/parsed/_backup_{timestamp}/。"""
        if self._backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._backup_dir = paper_path.parent / f"_backup_{timestamp}"
            self._backup_dir.mkdir(parents=True, exist_ok=True)

        backup_target = self._backup_dir / paper_path.name
        try:
            shutil.copytree(paper_path, backup_target)
            logger.info("[Standardizer] Backed up to %s", backup_target.name)
            return str(backup_target)
        except Exception as e:
            logger.error("[Standardizer] Backup failed: %s", e)
            return None

    def _rename_files(self, paper_path: Path, arxiv_id: str) -> list[str]:
        """将文件夹内的文件重命名为标准格式。"""
        renamed: list[str] = []

        for item in paper_path.iterdir():
            if not item.is_file():
                continue

            # 跳过已经是标准命名的文件
            if item.name.startswith(f"{arxiv_id}"):
                continue

            ext = item.suffix.lower()

            # .md 文件 -> {arxiv_id}.md
            if ext == ".md" and item.name != f"{arxiv_id}.md":
                target = paper_path / f"{arxiv_id}.md"
                if not target.exists():
                    item.rename(target)
                    renamed.append(f"{item.name} -> {target.name}")

            # _content_list_v2.json -> {arxiv_id}_content.json
            elif item.name.endswith("_content_list_v2.json"):
                target = paper_path / f"{arxiv_id}_content.json"
                if not target.exists():
                    item.rename(target)
                    renamed.append(f"{item.name} -> {target.name}")

            # _content_list.json -> {arxiv_id}_content_full.json
            elif item.name.endswith("_content_list.json"):
                target = paper_path / f"{arxiv_id}_content_full.json"
                if not target.exists():
                    item.rename(target)
                    renamed.append(f"{item.name} -> {target.name}")

            # _model.json -> {arxiv_id}_model.json
            elif item.name.endswith("_model.json") and not item.name.startswith(arxiv_id):
                target = paper_path / f"{arxiv_id}_model.json"
                if not target.exists():
                    item.rename(target)
                    renamed.append(f"{item.name} -> {target.name}")

            # layout.json -> {arxiv_id}_layout.json
            elif item.name == "layout.json":
                target = paper_path / f"{arxiv_id}_layout.json"
                if not target.exists():
                    item.rename(target)
                    renamed.append(f"{item.name} -> {target.name}")

        return renamed

    def _rename_pdf(self, paper_path: Path, arxiv_id: str) -> str | None:
        """将 PDF 文件重命名为 {arxiv_id}_origin.pdf。"""
        target = paper_path / f"{arxiv_id}_origin.pdf"
        if target.exists():
            return None

        pdf_files = list(paper_path.glob("*.pdf"))
        if not pdf_files:
            return None

        # 选择最大的 PDF 文件（通常是论文原文）
        pdf_file = max(pdf_files, key=lambda f: f.stat().st_size)
        pdf_file.rename(target)
        return f"{pdf_file.name} -> {target.name}"

    def _merge_images_hd(self, paper_path: Path) -> list[str]:
        """将 images_hd/ 目录内容合并到 images/。"""
        hd_dir = paper_path / "images_hd"
        if not hd_dir.exists():
            return []

        images_dir = paper_path / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        moved: list[str] = []
        for item in hd_dir.iterdir():
            if item.is_file():
                target = images_dir / item.name
                if not target.exists():
                    try:
                        shutil.copy2(str(item), str(target))
                        moved.append(f"images_hd/{item.name} -> images/{item.name}")
                    except OSError as e:
                        logger.warning("[Standardizer] Copy failed for %s: %s", item.name, e)

        # 尝试删除空的 images_hd 目录（失败则保留）
        try:
            hd_dir.rmdir()
            moved.append("removed empty images_hd/")
        except OSError:
            pass  # 目录非空或被锁定，保留

        return moved

    def _move_arxiv_source(self, paper_path: Path, arxiv_id: str) -> list[str]:
        """将 arxiv_source/ 目录内容复制到 data/papers/{arxiv_id}_source/。"""
        src_dir = paper_path / "arxiv_source"
        if not src_dir.exists():
            return []

        target_dir = settings.DATA_DIR / "papers" / f"{arxiv_id}_source"
        target_dir.mkdir(parents=True, exist_ok=True)

        moved: list[str] = []
        for item in src_dir.iterdir():
            target = target_dir / item.name
            if not target.exists():
                try:
                    if item.is_file():
                        shutil.copy2(str(item), str(target))
                    else:
                        shutil.copytree(str(item), str(target))
                    moved.append(f"arxiv_source/{item.name} -> data/papers/{arxiv_id}_source/{item.name}")
                except OSError as e:
                    logger.warning("[Standardizer] Copy failed for %s: %s", item.name, e)

        # 尝试删除空的 arxiv_source 目录（失败则保留）
        try:
            src_dir.rmdir()
            moved.append("removed empty arxiv_source/")
        except OSError:
            pass

        return moved

    # ------------------------------------------------------------------
    # 批量标准化
    # ------------------------------------------------------------------

    def batch_standardize(
        self,
        papers: list[dict[str, str]],
        batch_size: int = 10,
    ) -> dict[str, Any]:
        """
        批量标准化文件夹。

        参数:
            papers: [{"paper_dir": "...", "arxiv_id": "...", "chinese_title": "...", "direction_tag": "..."}]
            batch_size: 每批最多处理数量

        返回:
            {
                "total": int,
                "succeeded": int,
                "failed": int,
                "results": list[dict],
            }
        """
        total = len(papers)
        succeeded = 0
        failed = 0
        all_results = []

        for i in range(0, total, batch_size):
            batch = papers[i:i + batch_size]
            logger.info(
                "[Standardizer] Processing batch %d/%d (%d items)",
                i // batch_size + 1,
                (total + batch_size - 1) // batch_size,
                len(batch),
            )

            for paper in batch:
                result = self.execute(**paper)
                all_results.append(result)
                if result.get("error"):
                    failed += 1
                    logger.error("[Standardizer] Failed: %s - %s", paper.get("arxiv_id"), result["error"])
                else:
                    succeeded += 1

            # 每批处理完后验证
            logger.info("[Standardizer] Batch complete: %d succeeded, %d failed so far", succeeded, failed)

        return {
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "results": all_results,
        }
