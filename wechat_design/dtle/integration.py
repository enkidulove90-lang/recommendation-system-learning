"""DTLE ↔ multi-platform-publishing skill 集成入口。

现有发布 skill（skills/multi-platform-publishing）可在「内容渲染」环节改为调用本模块，
统一走双轨引擎，取代手工拼 components.md。

    from wechat_design.dtle.integration import render_for_publish
    res = render_for_publish(markdown_text, track="wechat", theme="recsys-blue")
    if res["ok"] and res["gate"]["passed"]:
        draft_html = res["html"]
"""
from __future__ import annotations

import sys
import os
from typing import Any, Dict, Union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from wechat_design.dtle import render_source  # noqa: E402


def render_for_publish(source: Union[str, Dict[str, Any]], track: str,
                        theme: str = "recsys-blue") -> Dict[str, Any]:
    """发布 skill 调用：成功返回 {ok, html, gate}；失败返回 {ok:False, error}。"""
    try:
        out = render_source(source, track=track, theme=theme)
        return {"ok": True, "track": out.track, "theme": out.theme,
                "html": out.html, "gate": out.gate,
                "preview_html": out.preview_html}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def render_both(source: Union[str, Dict[str, Any]],
                 theme: str = "recsys-blue") -> Dict[str, Any]:
    """一次出双轨：{wechat_html, xhs_html, gate}。"""
    a = render_for_publish(source, track="wechat", theme=theme)
    b = render_for_publish(source, track="xhs", theme=theme)
    return {"ok": a["ok"] and b["ok"],
            "wechat_html": a.get("html"), "xhs_html": b.get("html"),
            "gate": a.get("gate"), "error": a.get("error") or b.get("error")}
