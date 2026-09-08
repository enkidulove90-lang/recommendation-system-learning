#!/usr/bin/env python3
"""DTLE 命令行入口。

子命令
------
  build-tokens              由 tokens/*.yaml 生成 generated/tokens.*.css|json
  render -s SRC -t TRACK    渲染双轨产物；-t wechat|xhs；--out 写文件（--preview 额外写预览页）
  serve --host --port       启动 HTTP 服务（POST /render）

示例
------
  python wechat_design/dtle/cli.py build-tokens
  python wechat_design/dtle/cli.py render -s article.md -t wechat -o out.html --preview
  python wechat_design/dtle/cli.py render -s article.json -t xhs -o card.html
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from wechat_design.dtle import list_available_themes, render_source  # noqa: E402
from wechat_design.dtle.tokens import build_all  # noqa: E402


def cmd_build_tokens(_):
    m = build_all()
    print(f"✅ token 产物已生成：{m['themes']}")


def cmd_render(args):
    out = render_source(args.source, track=args.track, theme=args.theme)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out.html)
    print(f"✅ [{args.track}/{args.theme}] 已写 {args.out} "
          f"({len(out.html)} 字符)")
    if args.track == "wechat" and out.gate:
        g = out.gate
        print(f"   校验门：passed={g['passed']} errors={len(g['errors'])} "
              f"warnings={len(g['warnings'])} leaf={g['leaf_count']}")
        for e in g["errors"]:
            print(f"   ❌ {e}")
    if args.preview and out.preview_html:
        pv = args.out.replace(".html", "_preview.html")
        with open(pv, "w", encoding="utf-8") as f:
            f.write(out.preview_html)
        print(f"   预览页：{pv}")


def cmd_serve(args):
    from wechat_design.dtle.service.server import run  # 延迟导入避免循环
    run(host=args.host, port=args.port, server=args.server)


def main():
    ap = argparse.ArgumentParser(prog="dtle", description="双轨排版引擎 DTLE")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build-tokens", help="生成 token 产物").set_defaults(
        func=cmd_build_tokens)

    rp = sub.add_parser("render", help="渲染双轨产物")
    rp.add_argument("-s", "--source", required=True,
                    help="Markdown 文本 / .md 文件 / .json 结构化文档")
    rp.add_argument("-t", "--track", choices=["wechat", "xhs"], required=True)
    rp.add_argument("--theme", default="recsys-blue")
    rp.add_argument("-o", "--out", required=True)
    rp.add_argument("--preview", action="store_true", help="(wechat) 额外写预览页")
    rp.set_defaults(func=cmd_render)

    sp = sub.add_parser("serve", help="启动 HTTP 服务")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8787)
    sp.add_argument("--server", choices=["auto", "flask", "stdlib"], default="auto",
                    help="HTTP 后端：auto=flask 可用时优先；flask；stdlib(零依赖兜底)")
    sp.set_defaults(func=cmd_serve)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
