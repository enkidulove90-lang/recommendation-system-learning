"""L0 设计 Token 层 —— 运行时加载与构建。

单一事实源：`tokens/*.yaml`。
- 运行时：``load_theme_raw(name)`` 直接读 YAML（无需先 build）。
- 构建：``build_all()`` 把每个 YAML 展开为 ``generated/tokens.<name>.css``（A 轨预览/HTML）
  与 ``generated/tokens.<name>.json``（B 轨 Satori/卡片），并写 ``generated/manifest.json``。
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import yaml

THEMES_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(THEMES_DIR, "generated")

# Typography.js（报告 #14）同款模块化字号阶梯：base * ratio^i
def modular_scale(base: float, ratio: float, steps: int = 6) -> Dict[str, float]:
    return {f"step{i}": round(base * ratio ** i, 2) for i in range(steps)}


def rhythm(base: float, line_height: float) -> float:
    """Typography.js rhythm()：垂直韵律单位 = 基础字号 × 行高。"""
    return round(base * line_height, 2)


def list_themes() -> list[str]:
    out = []
    for fn in os.listdir(THEMES_DIR):
        if fn.endswith(".yaml"):
            out.append(fn[: -len(".yaml")])
    return sorted(out)


def load_theme_raw(name: str) -> Dict[str, Any]:
    path = os.path.join(THEMES_DIR, f"{name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"主题不存在: {name}（可选 {list_themes()}）")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def derive_tokens(raw: Dict[str, Any]) -> Dict[str, Any]:
    """从 YAML 派生完整 token 集（含自动 scale/rhythm 与角色覆盖）。"""
    t = raw.get("type", {})
    base = float(t.get("baseFontSize", 15))
    ratio = float(t.get("scaleRatio", 1.25))
    lh = float(t.get("lineHeight", 1.8))
    scale = modular_scale(base, ratio)
    roles = dict(t.get("roles", {}))
    # 角色未显式覆盖时，用 scale 推算：body=step0, h2=step1, h1=step2
    roles.setdefault("body", scale["step0"])
    roles.setdefault("h2", scale["step1"])
    roles.setdefault("h1", scale["step2"])
    roles.setdefault("caption", round(base * 0.85, 2))
    roles.setdefault("kpi", scale["step1"])
    return {
        "name": raw["name"],
        "description": raw.get("description", ""),
        "colors": raw.get("colors", {}),
        "type": {
            "baseFontSize": base,
            "scaleRatio": ratio,
            "lineHeight": lh,
            "scale": scale,
            "rhythm": rhythm(base, lh),
            "roles": {k: float(v) for k, v in roles.items()},
        },
        "spacing": raw.get("spacing", {"base": 8, "rhythmUnit": 24}),
        "radius": raw.get("radius", 8),
        "brand": raw.get("brand", {"signature": "@RecSysLab", "watermark": True}),
    }


def build_all() -> Dict[str, Any]:
    os.makedirs(GENERATED_DIR, exist_ok=True)
    manifest = {"themes": []}
    for name in list_themes():
        raw = load_theme_raw(name)
        toks = derive_tokens(raw)
        # A 轨 CSS 变量
        css = _to_css(toks)
        with open(os.path.join(GENERATED_DIR, f"tokens.{name}.css"), "w", encoding="utf-8") as f:
            f.write(css)
        # B 轨 Satori JSON
        with open(os.path.join(GENERATED_DIR, f"tokens.{name}.json"), "w", encoding="utf-8") as f:
            json.dump(toks, f, ensure_ascii=False, indent=2)
        manifest["themes"].append(name)
    with open(os.path.join(GENERATED_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return manifest


def _to_css(toks: Dict[str, Any]) -> str:
    lines = [":root {"]
    for k, v in toks["colors"].items():
        lines.append(f"  --rc-{k}: {v};")
    lines.append(f"  --rc-font-body: {toks['type']['roles']['body']}px;")
    lines.append(f"  --rc-font-h2: {toks['type']['roles']['h2']}px;")
    lines.append(f"  --rc-font-h1: {toks['type']['roles']['h1']}px;")
    lines.append(f"  --rc-line-height: {toks['type']['lineHeight']};")
    lines.append(f"  --rc-radius: {toks['radius']}px;")
    lines.append(f"  --rc-space: {toks['spacing']['base']}px;")
    lines.append("}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    m = build_all()
    print("✅ 已生成 token 产物:", m["themes"])
