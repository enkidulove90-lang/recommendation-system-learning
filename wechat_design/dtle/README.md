# DTLE · 双轨排版引擎（Dual-Track Layout Engine）

> 基于 `docs/frontend-layout-research.md` 与 `docs/dual-track-layout-engine.md` 设计的落地实现。
> **一套配置，双轨输出**：A 轨 = 微信安全内联 HTML；B 轨 = 小红书 1242×1656 卡片 HTML。
> 复用并扩展既有 `wechat_design` 设计系统（recsys-blue 主题 + `validate_gzh_html.py` 校验门）。

---

## 1. 架构（L0–L4）

```
wechat_design/dtle/
├── tokens/            L0 设计 Token 层
│   ├── recsys-blue.yaml | minimal.yaml | academic.yaml   # 单一事实源
│   ├── build_tokens.py  # YAML → generated/tokens.{name}.css|json
│   └── generated/       # 构建产物（css 供 A 轨预览，json 供 B 轨 Satori）
├── core/              L1 组件层（平台无关）
│   ├── types.py        # ThemeTokens / CardNode / Document
│   ├── components.py   # 11 组件 × {to_html, to_card}
│   └── document.py     # Markdown → Document 轻量解析
├── renderers/         L2 渲染层
│   ├── rich_text.py    # A 轨：Document → 微信内联 HTML
│   ├── card.py         # B 轨：Document → 1242×1656 卡片 HTML（PNG 走可选 Playwright）
│   └── chart.py        # 共享图表：纯 Python SVG（bar/line/pie）
├── validation/        L3 校验层
│   └── gate.py         # 微信安全门(复用 validate_gzh_html) + 移动端断言 + 可选 Playwright 截图
├── service/           L4 服务运维层
│   └── server.py       # stdlib http.server：POST /render，主题热更新
├── cli.py             # dtle build-tokens | render | serve
├── integration.py     # 供 multi-platform-publishing skill 调用的入口
└── tests/             # unittest 全层覆盖（13 用例）
```

设计要点：
- **L0 单一事实源**：三套主题 YAML 同时生成 `tokens.css`（A 轨预览/HTML 变量）与
  `tokens.json`（B 轨 Satori/卡片），改 YAML 即双轨一致。字体比例用 Typography.js(#14)
  同款模块化 scale(`base*ratio^i`) + rhythm 数学生成。
- **L1 双 adapter**：同一份 `ComponentSpec` 经 `to_html` / `to_card` 映射到两轨，
  保证"一处改、双轨一致"。A 轨中文文字节点一律 `<span leaf="">` 包裹（公众号铁律）。
- **L2 双轨**：A 轨纯 `<section>` 内联（无 `<div>/<style>/class`，可直接粘贴）；
  B 轨 1242×1656 自包含卡片 HTML（浏览器打开即所见即所得，可截图出 PNG）。
- **L3 安全门**：直接复用项目既有 `validate_gzh_html.py` 的 FORBIDDEN/LeafChecker 作
  为发布前必过结构门；另加移动端启发式断言（字号≥12px、图片 width:100%）。
- **L4 热更新**：主题每次渲染从 YAML 重读，改 `themes/*.yaml` 即生效，无需重启。

---

## 2. 快速开始

```bash
# 0) 依赖（仅需 PyYAML；其余全用标准库）
pip install pyyaml         # 或：python -m venv .venv && .venv/bin/pip install pyyaml

# 1) 生成 token 产物（首次/改主题后）
python wechat_design/dtle/cli.py build-tokens

# 2) 渲染（source 可为 Markdown 文本 / .md / .json 结构化文档）
python wechat_design/dtle/cli.py render -s article.md -t wechat -o out.html --preview
python wechat_design/dtle/cli.py render -s article.json -t xhs -o card.html

# 3) 起 HTTP 服务
python wechat_design/dtle/cli.py serve --host 0.0.0.0 --port 8787
```

### Python API
```python
from wechat_design.dtle import render_source
out = render_source("# 标题\n正文", track="wechat", theme="recsys-blue")
print(out.html)            # A 轨内联 HTML
print(out.gate["passed"])  # 校验门结果
```

### 发布 skill 集成
```python
from wechat_design.dtle.integration import render_for_publish
res = render_for_publish(markdown_text, track="wechat", theme="recsys-blue")
if res["ok"] and res["gate"]["passed"]:
    draft_html = res["html"]   # 直接进发布 skill 草稿
```

---

## 3. HTTP API（L4）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/health` | `{ok, themes, tracks}` |
| POST | `/render` | body `{source, track, theme}` → `{ok, html, gate?}` |

`source` 可为：① Markdown 文本；② `.md` 文件路径；③ `.json` 结构化文档；④ dict。

```bash
curl -X POST http://127.0.0.1:8787/render \
  -H 'Content-Type: application/json' \
  -d '{"source":"# 标题\n正文","track":"wechat","theme":"recsys-blue"}'
```

---

## 4. 测试

```bash
python wechat_design/dtle/tests/run.py
# 或 python -m unittest wechat_design.dtle.tests.test_dtle -v
```
覆盖：token 构建、11 组件微信安全、双轨渲染、三主题、图表 SVG、Markdown 解析、
校验门正/反例、integration 入口。全部 13 用例绿。

---

## 5. 部署运维

DTLE 按「当前/开发环境」与「生产环境」两档配置（对应调研报告选型）：

### 5.1 当前/开发环境：Flask + Playwright
- **HTTP 服务**：`Flask` 首选（`service/server.py` 自动启用），`stdlib http.server` 零依赖兜底。
  `pip install -r wechat_design/dtle/requirements-dev.txt && playwright install chromium`
- **B 轨 PNG / 视觉回归**：`Playwright(#23)` 截图（开发态快速验证），由
  `renderers/card.py:card_to_png` 与 `validation/gate.py:visual_regression` 调用。
- **启动**：`python wechat_design/dtle/cli.py serve --server flask`
  （`--server auto` 时 flask 可用即优先；`stdlib` 强制零依赖）。

### 5.2 生产环境：Satori + resvg（确定性无浏览器）
- **B 轨 PNG 渲染**：`Satori(#9)+@resvg/resvg-js`（Node，JSX→SVG→PNG），无浏览器、边缘可跑。
  依赖见 `wechat_design/dtle/prod/package.json`：`cd prod && npm install`。
- **后端切换**：设 `DTLE_BTRACK_BACKEND=production`（或请求 `backend=production`），
  `renderers/btrack.py:render_btrack` 走 Satori；不可用时自动降级 dev(Playwright) 并附 `note`。
- **CJK 字体**：Satori 必须显式提供字体，设 `DTLE_FONT` 或放置到候选路径
  （`C:/Windows/Fonts/simhei.ttf` 等，见 `renderers/btrack.py`），否则抛清晰错误。

### 5.3 镜像与运行
- **开发镜像**：`Dockerfile`（`python:3.13-slim` + Flask + Playwright/Chromium，暴露 8787）。
  `docker build -t dtle-dev -f wechat_design/dtle/Dockerfile . && docker run -p 8787:8787 dtle-dev`
- **生产镜像**：`Dockerfile.prod`（`python:3.13-slim` + Node + Satori/resvg，内置 Noto CJK）。
  `docker build -t dtle-prod -f wechat_design/dtle/Dockerfile.prod . && docker run -p 8787:8787 -e DTLE_BTRACK_BACKEND=production dtle-prod`
- **热更新**：改 `tokens/*.yaml` 后无需重启，下次渲染自动生效。
- **缓存/CDN（L4 增强）**：生产可在 `service/server.py` 外加一层按
  `hash(source+track+theme)` 的 immutable 缓存（OSS/CDN），命中即返回。
- **图表复杂交互**：可换 **ECharts(#17)/Chart.js(#15)/G2Plot(#16)** 替纯 SVG（接口兼容）。
- **视觉回归**：**Playwright(#24) 三视口截图 / Percy+Chromatic(#25) / BackstopJS(#26)**。

---

## 6. 已知残留

`wechat_design/dle/`（非 `dtle`）是构建时的路径笔误残留，已改为废弃 stub 并指向
`wechat_design.dtle`。沙箱 safe-delete 禁止删除，可手动 `rm -rf wechat_design/dle` 清理。
