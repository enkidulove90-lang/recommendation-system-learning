"""Hugging Face 代码/模型/数据集 关联富集（替换 PWC #13 的"代码/SOTA 链接"角色）。

Papers With Code 公共 API 已于 2025-07 停用；本 adapter 改用 Hugging Face 论文详情 API
（免鉴权）：GET https://huggingface.co/api/papers/{arxiv_id}
返回 githubRepo / githubStars / numTotalModels / numTotalDatasets / numTotalSpaces，
据此标注"是否有可运行代码/实现"（code_count），补上 PWC 缺失的可编程能力。
"""
from __future__ import annotations

import time
from typing import Iterable

import requests

from ..config import Config, get_config, log
from ..models import Paper
from .base import IngestAdapter

BASE = "https://huggingface.co/api/papers"


class HuggingFaceCodeAdapter(IngestAdapter):
    name = "hfcode"

    def enrich(self, papers: Iterable[Paper]) -> list[Paper]:
        """对已有论文（按 arxiv_id）富集代码/模型/数据集关联信号，原地更新并返回。"""
        if self.cfg.offline_fixture:
            return self._enrich_fixture(papers)
        out = []
        for p in papers:
            out.append(self._enrich_one(p))
            time.sleep(0.15)  # 礼貌间隔
        return out

    def _enrich_one(self, p: Paper) -> Paper:
        if not p.arxiv_id:
            return p
        url = f"{BASE}/{p.arxiv_id}"
        try:
            resp = requests.get(url, timeout=20)
        except requests.RequestException as exc:
            log.warning("[hfcode] request failed %s: %s", p.arxiv_id, exc)
            return p
        if resp.status_code != 200:
            return p
        try:
            d = resp.json()
        except ValueError:
            return p
        repo = d.get("githubRepo")
        stars = d.get("githubStars")
        code_count = (d.get("numTotalModels", 0) or 0) + \
                     (d.get("numTotalDatasets", 0) or 0) + \
                     (d.get("numTotalSpaces", 0) or 0)
        if repo:
            p.github_repo = repo
        if p.github_stars is None and stars is not None:
            p.github_stars = stars
        if code_count:
            p.code_count = code_count
        p.raw = {**(p.raw or {}), "hf_code": {
            "github_repo": repo, "github_stars": stars, "code_count": code_count,
        }}
        return p

    def _enrich_fixture(self, papers: Iterable[Paper]) -> list[Paper]:
        out = []
        for i, p in enumerate(papers):
            if p.arxiv_id:
                p.code_count = 3 + (i % 4)
                p.github_repo = f"https://github.com/example/repo-{p.arxiv_id}"
                p.raw = {**(p.raw or {}), "hf_code": {"code_count": p.code_count}}
            out.append(p)
        return out


def enrich_code_links(papers: list[Paper], config: Config | None = None) -> list[Paper]:
    """模块级便捷入口（orchestrator 调用）。"""
    cfg = config or get_config()
    return HuggingFaceCodeAdapter(config=cfg).enrich(papers)
