"""阶段一验证：自动化管线复用 gzh-design recsys-blue 组件库的 MVP 证明。

动作：
1. 渲染 2608.00267 的 WeChat HTML（经 gzh_components 组件库）。
2. 写正文 body 到临时文件，跑 validate_gzh_html 校验。
3. 生成预览 doc，打印 span leaf 覆盖率对比。
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]  # .../recommendation-system-learning
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".workbuddy" / "skills" / "gzh-design" / "scripts"))

from redbook.automation.paper_to_xhs import load_assets  # noqa: E402
from redbook.automation.paper_to_wechat import build_package, render_wechat_html, render_wechat_preview_doc  # noqa: E402
from redbook.automation import gzh_components as gzh  # noqa: E402
from validate_gzh_html import validate  # noqa: E402

ROOT = Path(".")
PID = "2608.00267"

assets = load_assets(PID, ROOT)
pkg = build_package(assets, canonical_url=f"https://arxiv.org/abs/{PID}")
html = pkg.metadata["wechat_html"]

# 1) 组件库加载来源确认
print(f"[1] gzh_components 从文件加载的组件数 = {len(gzh._RAW)} / 11 "
      f"（fallback 兜底 {11 - len(gzh._RAW)} 个）")
print(f"    section-header 是否来自文件: {'小标题文字' in gzh._tpl('section-header')}")

# 2) 校验
errors, warnings, leaf_n = validate(html, name=f"{PID} body")
print(f"\n[2] validate_gzh_html 结果:")
print(f"    span leaf 包裹: {leaf_n} 处")
print(f"    ERROR ×{len(errors)}:")
for e in errors:
    print(f"      • {e}")
print(f"    WARNING ×{len(warnings)}:")
for w in warnings[:8]:
    print(f"      • {w}")

# 3) 正文是否含禁用标签（应当为 0）
import re
bad = re.findall(r"<style|<script|</?div|class=|id=|display:grid|position:", html, re.I)
print(f"\n[3] 正文禁用标签命中: {len(bad)}")

# 4) 预览 doc
preview = render_wechat_preview_doc(assets, ROOT)
print(f"\n[4] 预览文件: {preview}")

# 5) body 写出（供人工粘贴对比）
body_file = ROOT / "data" / "logs" / f"wechat_body_{PID}_mvp.html"
body_file.write_text(html, encoding="utf-8")
print(f"    正文 body: {body_file}")

print("\n=== MVP 结论 ===")
if not errors and leaf_n > 0:
    print("✅ 自动化管线已复用 recsys-blue 组件库，正文自带 <span leaf>，校验零 ERROR。")
else:
    print("⚠️ 仍有 ERROR，需修复。")
