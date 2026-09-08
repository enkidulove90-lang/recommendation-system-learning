"""L4 服务运维层：HTTP API。

双后端策略（对应「当前/开发环境」与「生产环境」两档配置）：
  - Flask（首选，开发环境）：pip install flask 后自动启用，功能完整、易扩展。
  - stdlib http.server（兜底）：零依赖，flask 缺失时仍可起服务。

B 轨（xhs）渲染后端可经请求参数 / 环境变量切换：
  - format=html（默认）：返回小红书卡片 HTML（可预览/可截图）。
  - format=png     ：导出 PNG。
        backend=production（默认读 DTLE_BTRACK_BACKEND）→ Satori+resvg 确定性无浏览器渲染；
        backend=dev                              → Playwright 截图（需 pip install playwright）。
        生产后端不可用时自动降级 dev 并附 note。

端点
----
  GET  /health                 健康检查 + 可用主题 + 后端可用状态
  POST /render  {source, track, theme?, format?, backend?, preview?}
        → {ok, track, theme, html?, preview_html?, png?(dataURL), gate?, backend?, note?}
        source 可为 Markdown 文本 / .md / .json 路径 / 结构化 dict(JSON)
"""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from wechat_design.dtle import list_available_themes, render_source, resolve_doc  # noqa: E402
from wechat_design.dtle.core.types import ThemeTokens  # noqa: E402


# --------------------------------------------------------------------------- #
# 共享渲染逻辑（Flask 与 stdlib 共用，避免重复）
# --------------------------------------------------------------------------- #
def _render_payload(req: dict):
    """返回 (payload_dict, http_status)。"""
    source = req.get("source")
    track = req.get("track")
    theme = req.get("theme", "recsys-blue")
    fmt = (req.get("format") or "html").lower()
    backend = req.get("backend")  # auto | dev | production（仅 B 轨 PNG 生效）
    preview = bool(req.get("preview", False))

    if not source or track not in ("wechat", "xhs"):
        return {"ok": False,
                "error": "需要 source(str/dict) 与 track(wechat|xhs)"}, 400

    try:
        out = render_source(source, track=track, theme=theme)
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500

    if track == "wechat":
        payload = {"ok": True, "track": out.track, "theme": out.theme,
                   "html": out.html, "gate": out.gate}
        if preview and out.preview_html:
            payload["preview_html"] = out.preview_html
        return payload, 200

    # —— B 轨（xhs）——
    if fmt == "png":
        from wechat_design.dtle.renderers.btrack import render_btrack  # 延迟 import
        try:
            doc, t = resolve_doc(source, theme)
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            res = render_btrack(doc, ThemeTokens.load(t), backend=backend,
                                out_path=tmp.name, png=True)
        except Exception as e:
            return {"ok": False, "error": f"B 轨 PNG 渲染失败: {e}"}, 500
        if res.get("error"):
            return {"ok": False, "error": res["error"],
                    "note": res.get("note")}, 500
        with open(res["png_path"], "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        try:
            os.unlink(tmp.name)  # Windows 沙箱可能拦截，忽略
        except OSError:
            pass
        return {"ok": True, "track": "xhs", "theme": t,
                "backend": res["backend"], "format": "png",
                "png": f"data:image/png;base64,{b64}",
                "note": res.get("note")}, 200

    # 默认：返回 HTML
    return {"ok": True, "track": out.track, "theme": out.theme,
            "html": out.html}, 200


def _health_payload() -> dict:
    from wechat_design.dtle.renderers.btrack import production_available  # 延迟 import
    flask_ok = _flask_available()
    return {"ok": True, "themes": list_available_themes(),
            "tracks": ["wechat", "xhs"],
            "backends": {
                "http": "flask" if flask_ok else "stdlib",
                "flask_available": flask_ok,
                "btrack_production_satori": production_available(),
                "btrack_dev_playwright": _playwright_available(),
            }}


def _flask_available() -> bool:
    try:
        import flask  # noqa: F401
        return True
    except ImportError:
        return False


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


# --------------------------------------------------------------------------- #
# stdlib http.server 兜底实现
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", ""):
            self._send(200, _health_payload())
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/render":
            self._send(404, {"ok": False, "error": "not found"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            req = json.loads(raw.decode("utf-8") or "{}")
        except Exception as e:
            self._send(400, {"ok": False, "error": f"bad json: {e}"})
            return
        payload, code = _render_payload(req)
        self._send(code, payload)

    def log_message(self, *a):
        pass  # 静默


# --------------------------------------------------------------------------- #
# Flask 实现（首选）
# --------------------------------------------------------------------------- #
def make_flask_app():
    from flask import Flask, request, jsonify  # type: ignore

    app = Flask("dtle")

    @app.get("/health")
    def health():
        return jsonify(_health_payload())

    @app.post("/render")
    def render():
        req = request.get_json(silent=True) or {}
        payload, code = _render_payload(req)
        return jsonify(payload), code

    return app


# --------------------------------------------------------------------------- #
# 启动入口
# --------------------------------------------------------------------------- #
def run(host: str = "127.0.0.1", port: int = 8787, server: str = "auto"):
    """server: auto（默认，flask 可用时优先）| flask | stdlib。"""
    if server in ("auto", "flask") and _flask_available():
        if server == "flask":
            print("🚀 DTLE 服务（Flask）已启动")
        else:
            print("🚀 DTLE 服务（Flask，auto 选中；stdlib 为兜底）已启动")
        app = make_flask_app()
        print(f"   http://{host}:{port}   GET /health  POST /render")
        app.run(host=host, port=port, threaded=True)
        return
    if server == "flask":
        raise RuntimeError("Flask 不可用（pip install flask），无法以 flask 模式启动")
    print(f"🚀 DTLE 服务（stdlib http.server 兜底）已启动： http://{host}:{port}")
    print(f"   POST /render {{source, track, theme}}   GET /health")
    srv = ThreadingHTTPServer((host, port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    run()
