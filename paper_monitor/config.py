"""配置中心：所有密钥/路径/阈值均走环境变量（通用建议，非调研报告项目）。

环境变量清单（.env.example 同义）：
  OPENALEX_API_KEY    OpenAlex 免费 key（polite pool + 更高限额），可空
  OPENALEX_MAILTO     注册 polite pool 的邮箱，强烈建议设置
  S2_API_KEY          Semantic Scholar key，匿名亦可但易 429
  PM_DB_PATH          SQLite 路径，默认 ./paper_monitor/data/paper_monitor.db
  PM_TIME_WINDOW_DAYS 时间窗（近 N 天），默认 7
  PM_PER_PAGE         OpenAlex 分页大小，默认 100
  PM_MAX_PER_SOURCE   每源最大拉取条数，默认 200
  PM_DELIVERY         console,file,email,slack 逗号分隔，默认 console,file
  PM_DIGEST_PATH      落盘 digest 路径，默认 ./paper_monitor/data/digest/
  PM_SMTP_* / PM_SLACK_*  投递配置
  PM_LOG_LEVEL        日志级别，默认 INFO
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

# 项目根（paper_monitor 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "paper_monitor" / "data"


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    try:
        return int(v) if v is not None else default
    except ValueError:
        return default


def _env_first(*names: str) -> str | None:
    """依次读取多个候选环境变量名，返回首个非空值（兼容不同命名习惯）。"""
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


def _load_dotenv() -> None:
    """轻量 .env 解析（stdlib，无 python-dotenv 依赖）。加载首个存在的 .env。"""
    candidates = [
        Path(os.environ.get("PM_DOTENV", "")) if os.environ.get("PM_DOTENV") else None,
        Path.cwd() / ".env",
        PROJECT_ROOT / ".env",
    ]
    for p in candidates:
        if not p:
            continue
        p = Path(p)
        if not p.exists():
            continue
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass
        break


_load_dotenv()


@dataclass
class Config:
    # --- 数据源凭证 ---
    openalex_api_key: str | None = field(default_factory=lambda: os.environ.get("OPENALEX_API_KEY"))
    openalex_mailto: str | None = field(default_factory=lambda: os.environ.get("OPENALEX_MAILTO"))
    # 兼容多种命名：S2_API_KEY / SEMANTIC_SCHOLAR_API_KEY / Semantic_Scholar_API_Key
    s2_api_key: str | None = field(default_factory=lambda: _env_first(
        "S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY", "Semantic_Scholar_API_Key"))

    # --- 摄入参数 ---
    time_window_days: int = field(default_factory=lambda: _env_int("PM_TIME_WINDOW_DAYS", 7))
    per_page: int = field(default_factory=lambda: _env_int("PM_PER_PAGE", 100))
    max_per_source: int = field(default_factory=lambda: _env_int("PM_MAX_PER_SOURCE", 200))
    # 是否仅用 fixture（离线测试模式）。设为 1 时所有 adapter 返回内置样例。
    offline_fixture: bool = field(default_factory=lambda: _env_bool("PM_OFFLINE_FIXTURE", False))

    # --- 存储 ---
    db_path: Path = field(
        default_factory=lambda: Path(os.environ.get("PM_DB_PATH", str(DEFAULT_DATA_DIR / "paper_monitor.db")))
    )

    # --- 主题硬过滤（OpenAlex topics 软封装）---
    # 叶子 topic 精确匹配（display_name 子串，小写）；父 topic 保召回。
    topic_allowlist: list[str] = field(default_factory=lambda: [
        "recommender", "recommendation", "information retrieval",
        "collaborative filtering", "ranking", "personalization",
        "artificial intelligence", "machine learning", "deep learning",
        "natural language processing", "computer vision", "multimodal",
        "knowledge graph", "graph neural network", "representation learning",
        "reinforcement learning", "generative", "embedding",
    ])
    # 必须命中至少一层 topic 才进入推荐流（硬过滤开关）
    enable_topic_filter: bool = field(default_factory=lambda: _env_bool("PM_TOPIC_FILTER", True))

    # --- 兴趣画像（软过滤重排关键词）---
    interest_profile: list[str] = field(default_factory=lambda: [
        w.strip().lower() for w in
        os.environ.get("PM_INTEREST", "recommendation,llm,agent,multimodal,sequential").split(",") if w.strip()
    ])

    # --- 打分权重 ---
    score_weights: dict = field(default_factory=lambda: {
        "influential_citation": 0.35,
        "upvotes": 0.25,
        "github_stars": 0.15,
        "cited_by_count": 0.15,
        "interest_match": 0.10,
    })

    # --- 投递 ---
    delivery: list[str] = field(
        default_factory=lambda: [s.strip() for s in os.environ.get("PM_DELIVERY", "console,file").split(",") if s.strip()]
    )
    digest_path: Path = field(
        default_factory=lambda: Path(os.environ.get("PM_DIGEST_PATH", str(DEFAULT_DATA_DIR / "digest")))
    )
    smtp_host: str | None = field(default_factory=lambda: os.environ.get("PM_SMTP_HOST"))
    smtp_port: int = field(default_factory=lambda: _env_int("PM_SMTP_PORT", 465))
    smtp_user: str | None = field(default_factory=lambda: os.environ.get("PM_SMTP_USER"))
    smtp_pass: str | None = field(default_factory=lambda: os.environ.get("PM_SMTP_PASS"))
    smtp_to: str | None = field(default_factory=lambda: os.environ.get("PM_SMTP_TO"))
    slack_webhook: str | None = field(default_factory=lambda: os.environ.get("PM_SLACK_WEBHOOK"))

    log_level: str = field(default_factory=lambda: os.environ.get("PM_LOG_LEVEL", "INFO"))

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.digest_path.mkdir(parents=True, exist_ok=True)


def get_config() -> Config:
    return Config()


# 模块级 logger
logging.basicConfig(
    level=os.environ.get("PM_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("paper_monitor")
