"""一次性脚本：用 MinerU v4 解析 NLGCL+ (ACM TORS 2026) 论文 PDF。

Windows 下 httpx 与 mineru.net 偶发 TLS 握手超时，故本脚本改用 curl.exe
作为传输层（连通性已验证 HTTP 200），流程与 skills/pdf_parser.py 完全一致：
  1. POST /api/v4/file-urls/batch      申请上传链接
  2. PUT  <cdn_url>                    上传 PDF
  3. GET  /api/v4/extract-results/batch/{batch_id}  轮询
  4. 下载结果 ZIP → 解压 → 重命名为 {paper_id}.md / _content.json
"""
from __future__ import annotations

import json
import subprocess
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
PAPER_ID = "3806231_NLGCL-Plus"
PDF_PATH = ROOT / "data" / "papers" / "3806231_NLGCL-Plus.pdf"
OUT_DIR = ROOT / "data" / "parsed" / PAPER_ID
API_BASE = "https://mineru.net"
POLL_INTERVAL = 10
POLL_MAX = 90


def _api_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("MINERU_API_KEY="):
            return line.partition("=")[2].strip()
    raise RuntimeError("MINERU_API_KEY not found in .env")


def _curl(args: list[str], timeout: int = 300) -> bytes:
    proc = subprocess.run(
        ["curl.exe", "--ssl-no-revoke", "--fail", "--silent", "--show-error",
         "--location", "--retry", "3", "--retry-delay", "3", *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
    )
    return proc.stdout


def request_upload_url(key: str) -> tuple[str, str]:
    payload = {
        "files": [{"name": PDF_PATH.name, "data_id": PAPER_ID}],
        "model_version": "vlm",
        "enable_formula": True,
        "enable_table": True,
        "language": "en",
    }
    body_file = OUT_DIR / "_req.json"
    body_file.write_text(json.dumps(payload), encoding="utf-8")
    out = _curl([
        "-X", "POST", f"{API_BASE}/api/v4/file-urls/batch",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {key}",
        "-d", f"@{body_file}",
    ], timeout=90)
    try:
        body_file.unlink(missing_ok=True)
    except OSError:
        pass  # Windows 沙箱 safe-delete 拦截，忽略
    data = json.loads(out).get("data", {})
    batch_id, urls = data.get("batch_id", ""), data.get("file_urls", [])
    if not batch_id or not urls:
        raise RuntimeError(f"Bad response: {out[:400]!r}")
    return batch_id, urls[0]


def upload(cdn_url: str) -> None:
    size = PDF_PATH.stat().st_size
    print(f"[MinerU] Uploading {PDF_PATH.name} ({size:,} bytes) ...")
    _curl(["-X", "PUT", cdn_url, "--upload-file", str(PDF_PATH)], timeout=600)
    print("[MinerU] Upload OK")


def poll(key: str, batch_id: str) -> str:
    url = f"{API_BASE}/api/v4/extract-results/batch/{batch_id}"
    for i in range(1, POLL_MAX + 1):
        try:
            out = _curl(["-X", "GET", url, "-H", f"Authorization: Bearer {key}"], timeout=90)
            results = json.loads(out).get("data", {}).get("extract_result", [])
        except Exception as exc:
            print(f"[MinerU] poll {i} error: {exc}")
            time.sleep(POLL_INTERVAL)
            continue
        if not results:
            time.sleep(POLL_INTERVAL)
            continue
        r = results[0]
        state = r.get("state", "")
        if state == "done":
            print(f"[MinerU] Done at poll {i}")
            return r.get("full_zip_url", "")
        if state == "failed":
            raise RuntimeError(f"MinerU failed: {r.get('err_msg')}")
        prog = r.get("extract_progress", {})
        print(f"[MinerU] poll {i}/{POLL_MAX} state={state} "
              f"{prog.get('extracted_pages', 0)}/{prog.get('total_pages', 0)} pages")
        time.sleep(POLL_INTERVAL)
    raise RuntimeError("poll timeout")


def download_extract(zip_url: str) -> Path:
    zip_path = OUT_DIR / "_result.zip"
    content = _curl([zip_url], timeout=600)
    zip_path.write_bytes(content)
    print(f"[MinerU] Downloaded {len(content):,} bytes")
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            name = Path(member).name
            if name == "full.md":
                target = OUT_DIR / f"{PAPER_ID}.md"
            elif name.endswith("_content_list.json"):
                target = OUT_DIR / f"{PAPER_ID}_content.json"
            elif "images/" in member:
                (OUT_DIR / "images").mkdir(exist_ok=True)
                target = OUT_DIR / "images" / name
            else:
                target = OUT_DIR / name
            with zf.open(member) as src:
                target.write_bytes(src.read())
    try:
        zip_path.unlink(missing_ok=True)
    except OSError:
        pass
    md = OUT_DIR / f"{PAPER_ID}.md"
    if not md.exists():
        cands = sorted(OUT_DIR.glob("*.md"))
        if cands:
            md.write_bytes(cands[0].read_bytes())
    return md


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    key = _api_key()
    batch_id, cdn = request_upload_url(key)
    print(f"[MinerU] batch_id={batch_id}")
    upload(cdn)
    zip_url = poll(key, batch_id)
    md = download_extract(zip_url)
    print("=" * 70)
    print("markdown:", md, "| exists:", md.exists(),
          "| chars:", len(md.read_text(encoding="utf-8")) if md.exists() else 0)
    print("images  :", len(list((OUT_DIR / 'images').glob('*'))) if (OUT_DIR / 'images').exists() else 0)
    print("=" * 70)
    return 0 if md.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
