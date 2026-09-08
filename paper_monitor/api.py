"""极简内部 REST API（设计文档§3 GET /papers）。

使用 stdlib http.server，零依赖；用于本地查询已入库论文与趋势。
  GET /papers?since=YYYY-MM-DD&topic=recsys&limit=50
  GET /trends/burst
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from .config import get_config
from .store import SQLiteStore


class _Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        store = SQLiteStore(config=get_config())
        try:
            if parsed.path == "/papers":
                q = parse_qs(parsed.query)
                since = q.get("since", [None])[0]
                topic = q.get("topic", [None])[0]
                limit = int(q.get("limit", ["50"])[0])
                papers = store.query(since=since, topic=topic, limit=limit)
                self._send([p.to_dict() for p in papers])
            elif parsed.path == "/trends/burst":
                self._send(store.detect_bursts())
            else:
                self._send({"error": "unknown endpoint", "paths": ["/papers", "/trends/burst"]}, 404)
        finally:
            store.close()

    def log_message(self, *args) -> None:  # 静默访问日志
        return


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    httpd = ThreadingHTTPServer((host, port), _Handler)
    print(f"paper_monitor API on http://{host}:{port}  (Ctrl+C 退出)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
