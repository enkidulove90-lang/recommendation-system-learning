"""L2 A 轨：富文本渲染器（Document → 微信安全内联 HTML）。

产出纯 <section> 片段（无 <style>/<div>/class），可直接粘贴公众号编辑器。
预览页（含 tokens.css）由 ``wrap_preview`` 提供，仅供浏览器预览，不粘贴。
"""
from __future__ import annotations

from typing import List

from ..core.components import render_block_html
from ..core.types import Document, ThemeTokens, leaf
from ..tokens import GENERATED_DIR


def render_document(doc: Document, theme: ThemeTokens) -> str:
    """渲染文档正文为微信安全内联 HTML（A 轨）。"""
    parts: List[str] = []
    for b in doc.blocks:
        parts.append(render_block_html(b.type, b.props, theme))
    return "\n".join(parts)


def wrap_preview(doc: Document, theme: ThemeTokens, html: str) -> str:
    """包成可浏览器预览的页面（含复制按钮）。此产物仅供预览，不粘贴公众号。"""
    css_path = f"tokens.{theme.name}.css"
    sig = theme.brand.get("signature", "@RecSysLab")
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{doc.title or 'DTLE 预览'} · {theme.name}</title>
<style>
@import url("{css_path}");
body{{max-width:680px;margin:0 auto;padding:24px;background:#f2f4f7;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;}}
.art{{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.06);}}
.copy{{position:sticky;top:8px;float:right;background:var(--rc-primary,#3a5fcd);color:#fff;border:0;border-radius:8px;padding:8px 14px;cursor:pointer;font-size:14px;}}
.sig{{text-align:center;color:#8a94a6;font-size:13px;margin-top:24px;}}
</style></head>
<body>
<button class="copy" onclick="copyArt()">复制全文</button>
<div class="art" id="art">
{html}
</div>
<div class="sig">{sig}</div>
<script>
function copyArt(){{const a=document.getElementById('art');navigator.clipboard.writeText(a.innerText);alert('已复制正文，去公众号粘贴即可');}}
</script>
</body></html>"""


def build(theme_name: str, doc: Document) -> str:
    t = ThemeTokens.load(theme_name)
    return render_document(doc, t)
