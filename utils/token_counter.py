"""
utils/token_counter.py — Token 计数工具

基于 tiktoken 提供精确的 token 计数功能，
用于文档合并时控制最终输出大小。
支持多种编码器 (cl100k_base, o200k_base 等)。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 尝试加载 tiktoken，如果不可用则回退到字符估算
try:
    import tiktoken

    _HAS_TIKTOKEN = True
    # 默认使用 cl100k_base (GPT-4 / DeepSeek 兼容)
    _DEFAULT_ENCODING = "cl100k_base"
    _encoder_cache: dict[str, tiktoken.Encoding] = {}
except ImportError:
    _HAS_TIKTOKEN = False
    logger.warning("tiktoken not installed; falling back to character-based estimation.")


# ---------------------------------------------------------------------------
# 公开 API
# ---------------------------------------------------------------------------


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    计算文本的 token 数量。

    参数:
        text: 输入文本
        encoding_name: tiktoken 编码器名称，默认 cl100k_base

    返回:
        int: token 数量
    """
    if not text:
        return 0

    if _HAS_TIKTOKEN:
        encoder = _get_encoder(encoding_name)
        return len(encoder.encode(text))
    else:
        # 回退: 英语文本 ~4 chars/token, 中英文混合 ~2.5 chars/token
        return max(1, len(text) // 3)


def count_tokens_file(file_path: str | Path, encoding_name: str = "cl100k_base") -> int:
    """
    计算文件的 token 数量。

    参数:
        file_path: 文件路径
        encoding_name: tiktoken 编码器名称

    返回:
        int: token 数量，若文件不存在返回 0
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning("File not found for token counting: %s", file_path)
        return 0

    text = path.read_text(encoding="utf-8", errors="replace")
    return count_tokens(text, encoding_name)


def estimate_chinese_tokens(text: str) -> int:
    """
    针对中英文混合文本的 Token 估算（比 char/4 更精确）。

    规则:
      - 英文字母/数字: ~4 chars/token (GPT tokenizer)
      - 中文字符: ~1.5 chars/token (每个中文字约 1.5-2 token)
      - 空格/标点: token 边界，基本不计

    返回:
        int: 估算 token 数
    """
    if _HAS_TIKTOKEN:
        return count_tokens(text)

    chinese_count = sum(1 for c in text if '一' <= c <= '鿿')
    other_count = len(text) - chinese_count
    return max(1, int(chinese_count / 1.5 + other_count / 4))


def token_size_friendly(token_count: int) -> str:
    """将 token 数转为人类友好的显示格式。"""
    if token_count >= 1_000_000:
        return f"{token_count / 1_000_000:.1f}M"
    elif token_count >= 1_000:
        return f"{token_count / 1_000:.1f}k"
    else:
        return str(token_count)


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------


def _get_encoder(encoding_name: str) -> "tiktoken.Encoding":
    """获取或缓存 tiktoken 编码器实例。"""
    if encoding_name not in _encoder_cache:
        _encoder_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
    return _encoder_cache[encoding_name]
