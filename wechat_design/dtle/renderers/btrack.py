"""B 轨后端调度：开发(dev) = HTML/Playwright，生产(production) = Satori + resvg(PNG)。

后端选择（优先级）：
  1. 显式参数 backend=
  2. 环境变量 DTLE_BTRACK_BACKEND = production | dev（默认 dev）
生产后端命中条件：node 可用 且  dtle/prod/node_modules 含 satori。

生产渲染：Document → CardNode → Satori 元素树(JSX 风格) → node btrack.js
          → Satori(JSX→SVG) → @resvg/resvg-js(SVG→PNG)，确定性、无浏览器。
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional

from ..core.components import render_block_card
from ..core.types import CardNode, Document, ThemeTokens
from .card import build_card_root, card_to_png, render_card_html

PROD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prod")

# 受管 Node 路径（兜底用 PATH 上的 node）
_MANAGED_NODE = "C:/Users/xu.yan1/.workbuddy/binaries/node/versions/22.22.2/node.exe"

_FONT_CANDIDATES = [
    os.environ.get("DTLE_FONT"),
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def resolve_node() -> Optional[str]:
    if os.path.exists(_MANAGED_NODE):
        return _MANAGED_NODE
    return shutil.which("node")


def resolve_font() -> Optional[str]:
    for c in _FONT_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def _img_dims(path: str) -> Optional[tuple]:
    """读取本地位图（PNG/JPEG）的像素尺寸；不支持或失败返回 None。"""
    try:
        with open(path, "rb") as f:
            head = f.read(64)
        if len(head) >= 24 and head[:8] == b"\x89PNG\r\n\x1a\n":
            import struct
            w, h = struct.unpack(">II", head[16:24])
            return w, h
        if len(head) >= 4 and head[:2] in (b"\xff\xd8",):  # JPEG
            import struct
            f = open(path, "rb")
            try:
                f.read(2)
                while True:
                    b = f.read(1)
                    while b and b != b"\xff":
                        b = f.read(1)
                    marker = f.read(1)
                    if marker in (b"\xc0", b"\xc1", b"\xc2", b"\xc3"):
                        f.read(3)
                        h, w = struct.unpack(">HH", f.read(4))
                        return w, h
                    else:
                        ln = struct.unpack(">H", f.read(2))[0]
                        f.read(ln - 2)
            finally:
                f.close()
    except Exception:
        return None
    return None


# B 轨内容宽度（卡片 1242 − 左右 padding 64×2）
_BTRACK_CONTENT_W = 1114

# 1×1 透明 PNG（data URL）。Satori 0.12 不会经 images.fetch 拉取远程图，
# 故对缺失/远程的 img 直接以透明占位内联，避免整页渲染崩溃。
_TRANSPARENT_PNG = ("data:image/png;base64,"
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
                    "+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC")


def production_available() -> bool:
    node = resolve_node()
    if not node:
        return False
    return os.path.exists(os.path.join(PROD_DIR, "node_modules", "satori")) and \
        os.path.exists(os.path.join(PROD_DIR, "node_modules", "@resvg", "resvg-js"))


def _to_satori_node(node: Any) -> Any:
    """CardNode(camelCase 风格) → Satori/React 元素树。"""
    if isinstance(node, str):
        return node
    style = {k: v for k, v in node.style.items() if v is not None}
    children = [_to_satori_node(c) for c in node.children]
    if node.text:
        children = [node.text] + children
    props: Dict[str, Any] = {"style": style}
    if node.type in ("img", "br"):
        raw = node.style.get("src") or node.style.get("Src") or ""
        # 本地图 → data URL 内联；缺失/远程图 → 透明占位（Satori 不拉远程，避免整页崩溃）
        dims = None
        if raw and os.path.exists(raw):
            ext = os.path.splitext(raw)[1].lower().lstrip(".")
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "webp": "image/webp"}.get(ext, "image/png")
            with open(raw, "rb") as f:
                src = f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
            dims = _img_dims(raw)
        else:
            src = _TRANSPARENT_PNG
        # Satori 要求 img 必须有显式像素宽高，否则整页渲染崩溃
        style["width"] = _BTRACK_CONTENT_W
        if dims and dims[0]:
            style["height"] = max(1, round(_BTRACK_CONTENT_W * dims[1] / dims[0]))
        else:
            style["height"] = 480  # 远程/未知尺寸时的兜底比例
        style["objectFit"] = "cover"
        style.pop("src", None)
        style.pop("Src", None)
        props["src"] = src
    n_children = len(children)
    if children:
        props["children"] = children[0] if n_children == 1 else children
    # Satori 要求：含子节点的容器必须有显式 display:flex（HTML 默认 block，Satori 不默认）。
    # 单列 flex 容器与 block 视觉等价，对单/多子节点统一设置，避免「Expected display:flex」崩溃。
    if node.type not in ("img", "br") and n_children >= 1 and "display" not in style:
        style["display"] = "flex"
        style["flexDirection"] = "column"
    return {"type": node.type, "props": props}


def src_original(node: Any) -> str:
    """取 img 节点的原始（未内联）本地路径，用于读尺寸。"""
    s = node.style.get("src") or node.style.get("Src") or ""
    return s if s and os.path.exists(s) else ""


def render_card_satori(doc: Document, theme: ThemeTokens, out_path: str,
                       width: int = 1242, height: int = 1656) -> str:
    """生产后端：经 node btrack.js 渲染 PNG。返回 out_path。"""
    node = resolve_node()
    if not node:
        raise RuntimeError("未找到 node，无法运行 Satori 生产后端")
    font = resolve_font()
    if not font:
        raise RuntimeError("未找到 CJK 字体，请设置 DTLE_FONT 或安装中文字体")
    root = build_card_root(doc, theme, width, height)
    element = _to_satori_node(root)
    payload = {"element": element, "width": width, "height": height, "fontPath": font}
    proc = subprocess.run(
        [node, os.path.join(PROD_DIR, "btrack.js"), out_path],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError("Satori 渲染失败: " + proc.stderr.decode("utf-8", "replace"))
    return out_path


def render_btrack(doc: Document, theme: ThemeTokens, backend: Optional[str] = None,
                  out_path: Optional[str] = None, width: int = 1242,
                  height: int = 1656, png: bool = False) -> Dict[str, Any]:
    """B 轨统一入口。

    返回 {backend, format, html?, png_path?, note?}
      - dev        → format=html（默认）或 format=png（Playwright 截图，需 out_path）
      - production  → format=png（Satori+resvg 确定性渲染，需 out_path）
    生产不可用时会降级到 dev（PNG 走 Playwright，HTML 直出）并注明。

    png=True 时要求 out_path，且 dev 路径依赖已安装 Playwright。
    """
    backend = backend or os.environ.get("DTLE_BTRACK_BACKEND", "dev")

    def _dev(html: str) -> Dict[str, Any]:
        if not png:
            if out_path:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(html)
                return {"backend": "dev", "format": "html", "html_path": out_path,
                        "html": html}
            return {"backend": "dev", "format": "html", "html": html}
        # dev PNG → Playwright
        if not out_path:
            raise ValueError("dev 后端导出 PNG 需要 out_path")
        try:
            card_to_png(html, out_path)
        except RuntimeError as e:
            return {"backend": "dev", "format": "png", "error": str(e),
                    "note": "Playwright 未安装，无法导出 dev PNG"}
        return {"backend": "dev", "format": "png", "png_path": out_path}

    # dev 直出（无需 Satori）
    if backend != "production":
        return _dev(render_card_html(doc, theme))

    # production：Satori + resvg
    if not production_available():
        note = "生产后端(Satori)不可用（缺 node 或 dtle/prod 未 npm install），降级 dev"
        res = _dev(render_card_html(doc, theme))
        res["note"] = note
        return res
    if not out_path:
        raise ValueError("生产后端需要 out_path 以写出 PNG")
    render_card_satori(doc, theme, out_path, width, height)
    return {"backend": "production", "format": "png", "png_path": out_path}
