"""
skills/vision_enhancer.py — 多平台视觉模型图表理解技能（L2 增强层）

对论文 images/ 目录下的架构图、结果表等关键图片执行视觉理解，
转为结构化文本描述，输出 _figures.json，供摘要生成（Phase 3）使用。

支持多 provider 自动 fallback（按优先级）：
  1. ModelScope (Qwen3.5-397B-A17B)
  2. SiliconFlow (Qwen2.5-VL-72B / GLM-4.6V 等)
  3. Zhipu AI (GLM-4V)

当某个 provider 返回 429（配额耗尽）或 401（认证失败）时，
自动切换到下一个 provider，直到所有 provider 均不可用。

所有 provider 均使用 OpenAI 兼容格式（base64 image + text prompt）。
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import settings
from skills.base_module import BaseSkill, register_skill

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Prompt 模板
# ------------------------------------------------------------------

PROMPT_ARCHITECTURE = (
    "这是一篇推荐系统论文的方法架构图。"
    "请识别图中的模块名称、模块间数据流向、输入输出，用结构化列表描述。"
    "只描述图中可见内容，不可推测。"
    "输出格式：\n"
    "1. 图中识别到的模块列表（名称 + 作用）\n"
    "2. 模块间数据流向（A -> B -> C）\n"
    "3. 输入与输出\n"
    "4. 其他可见标注（如 loss 标注、维度标注等）"
)

PROMPT_RESULT_TABLE = (
    "这是一篇推荐系统论文的实验结果表。"
    "请逐行提取：数据集名称、基线方法、指标名称、指标数值、本文方法的提升幅度。"
    "只提取表中可见数字，不可补全。"
    "输出格式：\n"
    "| 数据集 | 指标 | 基线方法 | 基线数值 | 本文方法 | 提升幅度 |"
)

PROMPT_LOSS_CURVE = (
    "这是一篇推荐系统论文的训练曲线图（loss/收敛曲线）。"
    "请描述：横轴/纵轴含义、曲线趋势、关键拐点、是否有过拟合迹象。"
    "只描述图中可见内容。"
)

PROMPT_GENERAL = (
    "这是一篇推荐系统论文中的图片。"
    "请描述图片内容：类型（架构图/流程图/结果表/散点图/其他）、"
    "关键元素、标注文字、与论文方法的关联。"
    "只描述图中可见内容，不可推测。"
)


# ------------------------------------------------------------------
# 图表类型识别关键词
# ------------------------------------------------------------------

ARCH_KEYWORDS = ["arch", "framework", "model", "overview", "pipeline", "structure", "network", "system"]
TABLE_KEYWORDS = ["table", "result", "performance", "comparison", "ablation", "baseline"]
CURVE_KEYWORDS = ["loss", "curve", "convergence", "training", "epoch", "tuning", "sensitivity", "analysis"]


def _classify_figure(filename: str) -> str:
    """根据文件名关键词推断图表类型。"""
    name_lower = filename.lower()
    for kw in ARCH_KEYWORDS:
        if kw in name_lower:
            return "architecture"
    for kw in TABLE_KEYWORDS:
        if kw in name_lower:
            return "result_table"
    for kw in CURVE_KEYWORDS:
        if kw in name_lower:
            return "loss_curve"
    return "other"


def _get_prompt(figure_type: str) -> str:
    """根据图表类型返回对应 prompt。"""
    prompts = {
        "architecture": PROMPT_ARCHITECTURE,
        "result_table": PROMPT_RESULT_TABLE,
        "loss_curve": PROMPT_LOSS_CURVE,
        "other": PROMPT_GENERAL,
    }
    return prompts.get(figure_type, PROMPT_GENERAL)


def _encode_image_base64(image_path: Path) -> str:
    """将图片文件编码为 base64 字符串。"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_mime_type(image_path: Path) -> str:
    """根据文件扩展名返回 MIME 类型。"""
    ext = image_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_map.get(ext, "image/jpeg")


@register_skill("vision-enhance")
class VisionEnhancer(BaseSkill):
    """
    Qwen3.5 视觉模型图表理解技能。

    对论文 images/ 目录下的关键图片执行视觉理解，生成 _figures.json。

    使用示例:
        enhancer = VisionEnhancer()
        result = enhancer.execute(
            paper_dir="data/parsed/2505.19525_ConfSMoE",
            arxiv_id="2505.19525",
        )
        # -> data/parsed/2505.19525_ConfSMoE/2505.19525_figures.json
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # ---- 多 provider 支持 ----
        # 优先使用 kwargs 传入的，否则从 settings.VISION_PROVIDERS 加载
        if kwargs.get("api_key"):
            # 单 provider 模式（向后兼容）
            self._providers: list[dict[str, Any]] = [{
                "name": kwargs.get("provider_name", "Custom"),
                "api_key": kwargs["api_key"],
                "base_url": kwargs.get("base_url", "https://api-inference.modelscope.cn/v1"),
                "model": kwargs.get("model", "Qwen/Qwen3.5-397B-A17B"),
                "client": OpenAI(
                    api_key=kwargs["api_key"],
                    base_url=kwargs.get("base_url", "https://api-inference.modelscope.cn/v1"),
                ),
            }]
        else:
            self._providers = []
            for p in settings.VISION_PROVIDERS:
                self._providers.append({
                    "name": p["name"],
                    "api_key": p["api_key"],
                    "base_url": p["base_url"],
                    "model": p["model"],
                    "client": OpenAI(api_key=p["api_key"], base_url=p["base_url"]),
                })

        # 记录本次运行中已失败的 provider（401 认证失败等不可恢复错误）
        self._dead_providers: set[str] = set()

    @property
    def is_ready(self) -> bool:
        """检查是否有至少一个 provider 可用。"""
        return any(p["name"] not in self._dead_providers for p in self._providers)

    @property
    def _primary_model(self) -> str:
        """返回第一个可用 provider 的模型名（用于日志）。"""
        for p in self._providers:
            if p["name"] not in self._dead_providers:
                return p["model"]
        return "none"

    @property
    def _api_key(self) -> str:
        """向后兼容：返回第一个 provider 的 api_key。"""
        return self._providers[0]["api_key"] if self._providers else ""

    @property
    def _client(self) -> OpenAI | None:
        """向后兼容：返回第一个可用 provider 的 client。"""
        for p in self._providers:
            if p["name"] not in self._dead_providers:
                return p["client"]
        return None

    @property
    def _model(self) -> str:
        """向后兼容：返回第一个可用 provider 的 model。"""
        return self._primary_model

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    # 图表类型优先级：架构图 > 结果表 > 曲线图 > 其他
    _TYPE_PRIORITY = {
        "architecture": 0,
        "result_table": 1,
        "loss_curve": 2,
        "other": 3,
    }

    # 章节标题关键词 → 图表类型映射
    _SECTION_KEYWORDS = {
        "architecture": ["arch", "framework", "model", "overview", "pipeline", "structure", "network", "system", "method", "approach", "模型", "架构", "框架", "方法", "整体"],
        "result_table": ["table", "result", "performance", "comparison", "ablation", "baseline", "experiment", "evaluation", "实验", "结果", "对比", "消融", "性能"],
        "loss_curve": ["loss", "curve", "convergence", "training", "epoch", "tuning", "sensitivity", "analysis", "训练", "收敛", "分析"],
    }

    def _classify_by_section(self, heading_text: str) -> str:
        """根据 markdown 章节标题推断图片类型。"""
        h = heading_text.lower()
        for fig_type, keywords in self._SECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in h:
                    return fig_type
        return "other"

    def _select_core_images(self, image_files: list[Path], max_figures: int, paper_dir: Path | None = None) -> list[Path]:
        """
        智能选择最核心的 2-3 张图片。

        策略：
        1. 如果有 paper_dir，读取 .md 文件，按图片在 markdown 中的章节标题分类
        2. 否则回退到文件名关键词分类
        3. 按优先级排序（架构图 > 结果表 > 曲线 > 其他），取前 N 张
        4. 恢复原始文件顺序
        """
        if len(image_files) <= max_figures:
            return image_files

        # 尝试从 markdown 上下文分类
        section_map: dict[str, str] = {}  # filename -> figure_type
        if paper_dir:
            section_map = self._build_section_map(paper_dir, image_files)

        # 分类并打分
        scored: list[tuple[int, int, Path]] = []
        for idx, img in enumerate(image_files):
            if img.name in section_map:
                fig_type = section_map[img.name]
            else:
                fig_type = _classify_figure(img.name)
            priority = self._TYPE_PRIORITY.get(fig_type, 3)
            scored.append((priority, idx, img))

        # 按优先级排序，同优先级按原始顺序
        scored.sort(key=lambda x: (x[0], x[1]))
        selected = [item[2] for item in scored[:max_figures]]

        # 恢复原始文件顺序（方便阅读）
        selected.sort(key=lambda p: image_files.index(p))
        return selected

    def _build_section_map(self, paper_dir: Path, image_files: list[Path]) -> dict[str, str]:
        """读取 .md 文件，为每张图片找到所属章节标题并分类。"""
        result: dict[str, str] = {}
        md_files = list(paper_dir.glob("*.md"))
        if not md_files:
            return result

        # 收集所有图片文件名集合
        img_names = {f.name for f in image_files}

        for md_file in md_files:
            try:
                lines = md_file.read_text(encoding="utf-8").split("\n")
            except (UnicodeDecodeError, OSError):
                continue

            current_heading = ""
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    current_heading = stripped
                # 检查这行是否引用了某个图片
                for img_name in img_names:
                    if img_name in line and img_name not in result:
                        fig_type = self._classify_by_section(current_heading)
                        if fig_type != "other":
                            result[img_name] = fig_type
                        else:
                            # 回退到文件名分类
                            result[img_name] = _classify_figure(img_name)

        return result

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        对论文图片执行视觉理解。

        参数:
            paper_dir      (str): 论文文件夹路径
            arxiv_id       (str): arXiv ID
            images_subdir  (str): 图片子目录名，默认 "images"
            max_figures    (int): 最多处理的图片数，默认 3（智能选取核心图片）
            skip_existing  (bool): 若 _figures.json 已存在则跳过，默认 True
            max_retries    (int): 每张图片最大重试次数，默认 3

        返回:
            {
                "ready": bool,
                "arxiv_id": str,
                "figures_path": str | None,
                "figures_count": int,
                "error": str | None,
            }
        """
        if not self.is_ready:
            logger.warning("No vision provider available; vision enhancement skipped.")
            return {
                "ready": False,
                "arxiv_id": kwargs.get("arxiv_id", ""),
                "figures_path": None,
                "figures_count": 0,
                "error": "No vision provider API key configured (checked ModelScope, SiliconFlow, Zhipu)",
            }

        arxiv_id: str = kwargs.get("arxiv_id", "")
        paper_dir: str = kwargs.get("paper_dir", "")
        images_subdir: str = kwargs.get("images_subdir", "images")
        max_figures: int = kwargs.get("max_figures", 3)
        skip_existing: bool = kwargs.get("skip_existing", True)
        max_retries: int = kwargs.get("max_retries", 3)

        if not paper_dir:
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "figures_path": None,
                "figures_count": 0,
                "error": "paper_dir is required.",
            }

        paper_path = Path(paper_dir)
        images_dir = paper_path / images_subdir
        figures_path = paper_path / f"{arxiv_id}_figures.json"

        # 若已存在则跳过
        if skip_existing and figures_path.exists():
            logger.info("[Vision] _figures.json already exists: %s", figures_path.name)
            try:
                existing = json.loads(figures_path.read_text(encoding="utf-8"))
                return {
                    "ready": True,
                    "arxiv_id": arxiv_id,
                    "figures_path": str(figures_path),
                    "figures_count": len(existing.get("figures", [])),
                    "error": None,
                }
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass  # 文件损坏，重新生成

        if not images_dir.exists():
            logger.warning("[Vision] No images/ directory in %s", paper_path.name)
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "figures_path": None,
                "figures_count": 0,
                "error": f"No {images_subdir}/ directory found.",
            }

        # 收集图片文件
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        image_files = sorted([
            f for f in images_dir.iterdir()
            if f.suffix.lower() in image_extensions and f.is_file()
        ])

        if not image_files:
            logger.warning("[Vision] No image files in %s", images_dir)
            return {
                "ready": True,
                "arxiv_id": arxiv_id,
                "figures_path": None,
                "figures_count": 0,
                "error": "No image files found.",
            }

        # 智能选取核心图片（优先架构图、结果表）
        image_files = self._select_core_images(image_files, max_figures, paper_path)
        logger.info(
            "[Vision] Selected %d core images for %s (providers: %s): %s",
            len(image_files), arxiv_id,
            ", ".join(p["name"] for p in self._providers),
            ", ".join(f.name for f in image_files),
        )

        # 对每张图片执行视觉理解
        figures: list[dict[str, Any]] = []
        for img_file in image_files:
            figure_type = _classify_figure(img_file.name)
            prompt = _get_prompt(figure_type)

            description, used_provider = self._describe_image(img_file, prompt, max_retries)
            if description:
                # 尝试从 .md 文件中定位图片引用的章节
                source_section = self._find_source_section(paper_path, img_file.name)

                figures.append({
                    "image_file": f"{images_subdir}/{img_file.name}",
                    "figure_type": figure_type,
                    "description": description,
                    "source_section": source_section,
                    "model": self._model,
                    "provider": used_provider,
                })
                logger.info("[Vision] Described %s as %s (provider=%s)", img_file.name, figure_type, used_provider)
            else:
                logger.warning("[Vision] Failed to describe %s", img_file.name)

        # 保存结果
        result_data = {
            "arxiv_id": arxiv_id,
            "model": self._primary_model,
            "providers_available": [p["name"] for p in self._providers if p["name"] not in self._dead_providers],
            "providers_dead": list(self._dead_providers),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "figures_count": len(figures),
            "figures": figures,
        }

        figures_path.write_text(
            json.dumps(result_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("[Vision] Saved %d figure descriptions -> %s", len(figures), figures_path.name)

        return {
            "ready": True,
            "arxiv_id": arxiv_id,
            "figures_path": str(figures_path),
            "figures_count": len(figures),
            "error": None,
        }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _describe_image(self, image_path: Path, prompt: str, max_retries: int) -> tuple[str | None, str]:
        """
        调用视觉模型描述单张图片，支持多 provider 自动 fallback。

        返回: (描述文本, 使用的 provider 名称)
        若所有 provider 均失败，返回 (None, "none")。
        """
        b64_image = _encode_image_base64(image_path)
        mime_type = _get_mime_type(image_path)

        for provider in self._providers:
            if provider["name"] in self._dead_providers:
                continue

            client: OpenAI = provider["client"]
            model: str = provider["model"]
            provider_name: str = provider["name"]

            for attempt in range(1, max_retries + 1):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{mime_type};base64,{b64_image}",
                                        },
                                    },
                                ],
                            }
                        ],
                        temperature=0.1,
                        max_tokens=1024,
                    )
                    content = response.choices[0].message.content or ""
                    if content:
                        return content, provider_name
                except Exception as exc:
                    exc_str = str(exc)
                    # 429 配额耗尽 / 401 认证失败 → 标记 provider 为死亡，立即切换
                    if "429" in exc_str or "rate_limit" in exc_str.lower():
                        logger.warning(
                            "[Vision] Provider %s rate-limited (429), switching to next provider.",
                            provider_name,
                        )
                        self._dead_providers.add(provider_name)
                        break  # 跳出 retry 循环，进入下一个 provider
                    if "401" in exc_str or "authentication" in exc_str.lower():
                        logger.warning(
                            "[Vision] Provider %s auth failed (401), marking as dead.",
                            provider_name,
                        )
                        self._dead_providers.add(provider_name)
                        break

                    logger.error(
                        "[Vision] Provider %s attempt %d/%d error for %s: %s",
                        provider_name, attempt, max_retries, image_path.name, exc,
                    )
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)

            # 如果此 provider 被标记为死亡，继续下一个
            if provider_name in self._dead_providers:
                continue
            # 此 provider 重试耗尽但未死亡，也继续尝试下一个
            logger.warning(
                "[Vision] Provider %s exhausted retries for %s, trying next provider.",
                provider_name, image_path.name,
            )

        return None, "none"

    @staticmethod
    def _find_source_section(paper_dir: Path, image_filename: str) -> str:
        """
        尝试从论文 .md 文件中定位图片引用所在章节。

        搜索 .md 中对 image_filename 的引用，返回最近的标题。
        """
        md_files = list(paper_dir.glob("*.md"))
        if not md_files:
            return ""

        # 去掉扩展名用于匹配
        stem = Path(image_filename).stem

        for md_file in md_files:
            try:
                lines = md_file.read_text(encoding="utf-8").split("\n")
            except (UnicodeDecodeError, OSError):
                continue

            current_heading = ""
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("#"):
                    current_heading = stripped
                elif stem in line or image_filename in line:
                    return current_heading or ""

        return ""

    # ------------------------------------------------------------------
    # L3 校验层：图文一致性交叉校验
    # ------------------------------------------------------------------

    def cross_validate(
        self,
        summary_path: str,
        figures_path: str,
    ) -> dict[str, Any]:
        """
        交叉校验摘要与图表描述的一致性（L3 校验层）。

        参数:
            summary_path   (str): 摘要 .md 文件路径
            figures_path   (str): _figures.json 文件路径

        返回:
            {
                "consistent": bool,
                "issues": list[str],
                "checked_figures": int,
            }
        """
        issues: list[str] = []
        checked = 0

        try:
            summary_text = Path(summary_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {"consistent": False, "issues": ["Cannot read summary file."], "checked_figures": 0}

        try:
            figures_data = json.loads(Path(figures_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"consistent": False, "issues": ["Cannot read figures.json file."], "checked_figures": 0}

        figures: list[dict] = figures_data.get("figures", [])

        for fig in figures:
            checked += 1
            desc = fig.get("description", "")
            fig_type = fig.get("figure_type", "")
            img_file = fig.get("image_file", "")

            # 检查摘要中是否引用了该图片
            # 从描述中提取关键名词
            key_terms = re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Za-z]{3,20}", desc)
            key_terms = list(set(key_terms))[:5]  # 取最多5个关键词

            matched_terms = []
            for term in key_terms:
                if term.lower() in summary_text.lower():
                    matched_terms.append(term)

            if not matched_terms and fig_type in ("architecture", "result_table"):
                issues.append(
                    f"图片 {img_file} ({fig_type}) 的描述关键词均未在摘要中出现，"
                    f"可能存在图文不一致。关键词: {key_terms}"
                )

            # 检查架构图描述中是否有模块名出现在摘要中
            if fig_type == "architecture":
                module_pattern = re.findall(r"模块[：:]\s*(.+?)(?:\n|$)", desc)
                for module_line in module_pattern:
                    module_names = re.findall(r"[\u4e00-\u9fff]{2,10}|[A-Z][a-z]+(?:[A-Z][a-z]+)*", module_line)
                    for name in module_names[:3]:
                        if name.lower() not in summary_text.lower():
                            issues.append(
                                f"架构图中的模块 '{name}' 未在摘要的方法部分提及。"
                            )

        consistent = len(issues) == 0
        return {
            "consistent": consistent,
            "issues": issues,
            "checked_figures": checked,
        }
